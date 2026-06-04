import mimetypes
import shutil
import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path

from common.cmd_utilities import run_cmd


class ClipboardProvider(ABC):
    """Abstract interface for OS-specific clipboard backends."""

    command: str

    @classmethod
    @abstractmethod
    def copy_text(cls, text: str) -> bool:
        pass

    @classmethod
    @abstractmethod
    def copy_file(cls, file_path: Path, mime_type: str | None = None) -> bool:
        pass

    @classmethod
    @abstractmethod
    def clear(cls) -> bool:
        pass

    @classmethod
    def is_available(cls) -> bool:
        """Checks if the required system utility is installed."""
        return shutil.which(cls.command) is not None


# Linux


class XClipProvider(ClipboardProvider):
    command = "xclip"

    @classmethod
    def copy_text(cls, text: str) -> bool:
        result = subprocess.run(
            [cls.command, "-sel", "clip"], input=text.encode(), check=True
        )
        return result.returncode == 0

    @classmethod
    def copy_file(cls, file_path: Path, mime_type: str | None = None) -> bool:
        mime_type = mime_type or mimetypes.guess_type(file_path)[0] or "text/plain"
        return run_cmd(
            [cls.command, "-sel", "clip", "-t", mime_type, "-i", file_path],
        ).success

    @classmethod
    def clear(cls) -> bool:
        return run_cmd([cls.command, "-sel", "clip", "/dev/null"]).success


class XSelProvider(ClipboardProvider):
    command = "xsel"

    @classmethod
    def copy_text(cls, text: str) -> bool:
        result = subprocess.run(
            [cls.command, "--clipboard", "--input"], input=text.encode(), check=True
        )
        return result.returncode == 0

    @classmethod
    def copy_file(cls, file_path: Path, mime_type: str | None = None):
        # xsel is primarily for text; copying a file usually involves passing the path
        # or the file content. To match the "file" behavior, we pass the absolute path.
        path_str = str(file_path.absolute())
        result = subprocess.run(
            [cls.command, "--clipboard", "--input"], input=path_str.encode(), check=True
        )
        return result.returncode == 0

    @classmethod
    def clear(cls) -> bool:
        return run_cmd([cls.command, "--clipboard", "--clear"]).success


class WaylandProvider(ClipboardProvider):
    command = "wl-copy"

    @classmethod
    def copy_text(cls, text: str) -> bool:
        result = subprocess.run([cls.command], input=text.encode(), check=True)
        return result.returncode == 0

    @classmethod
    def copy_file(cls, file_path: Path, mime_type: str | None = None) -> bool:
        mime = mime_type or mimetypes.guess_type(file_path)[0] or "text/plain"
        with open(file_path, "rb") as f:
            result = subprocess.run([cls.command, "--type", mime], stdin=f, check=True)
        return result.returncode == 0

    @classmethod
    def clear(cls) -> bool:
        return run_cmd([cls.command, "--clear"]).success


# macOS


class MacProvider(ClipboardProvider):
    command = "pbcopy"

    @classmethod
    def copy_text(cls, text: str) -> bool:
        result = subprocess.run([cls.command], input=text.encode(), check=True)
        return result.returncode == 0

    @classmethod
    def copy_file(cls, file_path: Path, mime_type: str | None = None) -> bool:
        # macOS uses AppleScript to handle 'file objects' for Finder pasting
        script = f'set the clipboard to (POSIX file "{file_path.absolute()}")'
        return run_cmd(["osascript", "-e", script]).success

    @classmethod
    def clear(cls):
        return run_cmd(["osascript", "-e", 'set the clipboard to ""']).success


# Windows


class WindowsProvider(ClipboardProvider):
    command = "powershell"

    @classmethod
    def copy_text(cls, text: str) -> bool:
        # Using UTF-16 for Windows clipboard compatibility
        process = subprocess.Popen(
            [cls.command, "-command", "Set-Clipboard"], stdin=subprocess.PIPE
        )
        process.communicate(input=text.encode("utf-16"))
        return process.returncode == 0

    @classmethod
    def copy_file(cls, file_path: Path, mime_type: str | None = None) -> bool:
        # Set-Clipboard -Path automatically handles the FileDropList format
        cmd = f"Set-Clipboard -Path {str(file_path.absolute())!r}"
        return run_cmd([cls.command, "-Command", cmd]).success

    @classmethod
    def clear(cls) -> bool:
        return run_cmd([cls.command, "-Command", "Clear-Clipboard"]).success


# Manager


class ClipboardManager:
    _provider: type[ClipboardProvider] | None = None

    @classmethod
    def _resolve(cls) -> type[ClipboardProvider]:
        """Detects the OS and utility once, then caches the result."""
        if cls._provider:
            return cls._provider

        sys_name = sys.platform
        potential_providers = []

        if sys_name == "linux":
            potential_providers = [WaylandProvider, XSelProvider, XClipProvider]
        elif sys_name == "darwin":
            potential_providers = [MacProvider]
        elif sys_name == "win32":
            potential_providers = [WindowsProvider]

        for provider in potential_providers:
            if provider.is_available():
                cls._provider = provider
                return provider

        raise RuntimeError(f"No supported clipboard utility found for {sys_name}. ")

    @classmethod
    def copy_text(cls, text: str) -> bool:
        return cls._resolve().copy_text(text)

    @classmethod
    def copy_file(cls, path: str | Path, mime_type: str | None = None) -> bool:
        path_obj = Path(path).resolve()

        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {path_obj}")

        return cls._resolve().copy_file(path_obj, mime_type)

    @classmethod
    def clear(cls) -> bool:
        return cls._resolve().clear()

import mimetypes
import platform
import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Type, Union


class ClipboardProvider(ABC):
    """Abstract interface for OS-specific clipboard backends."""

    command: str

    @classmethod
    @abstractmethod
    def copy_text(cls, text: str) -> None:
        pass

    @classmethod
    @abstractmethod
    def copy_file(cls, file_path: Path, mime_type: Optional[str] = None) -> None:
        pass

    @classmethod
    @abstractmethod
    def clear(cls) -> None:
        pass

    @classmethod
    def is_available(cls) -> bool:
        """Checks if the required system utility is installed."""
        return shutil.which(cls.command) is not None


# Linux


class XClipProvider(ClipboardProvider):
    command = "xclip"

    @classmethod
    def copy_text(cls, text: str):
        subprocess.run([cls.command, "-sel", "clip"], input=text.encode(), check=True)

    @classmethod
    def copy_file(cls, file_path: Path, mime_type: Optional[str] = None):
        # Fallback logic: param -> guessed type -> text/plain
        mime_type = mime_type or mimetypes.guess_type(file_path)[0] or "text/plain"
        subprocess.run(
            [cls.command, "-sel", "clip", "-t", mime_type, "-i", str(file_path)],
            check=True,
        )

    @classmethod
    def clear(cls):
        subprocess.run([cls.command, "-sel", "clip", "/dev/null"], check=True)


class XSelProvider(ClipboardProvider):
    command = "xsel"

    @classmethod
    def copy_text(cls, text: str):
        subprocess.run(
            [cls.command, "--clipboard", "--input"], input=text.encode(), check=True
        )

    @classmethod
    def copy_file(cls, file_path: Path, mime_type: Optional[str] = None):
        # xsel is primarily for text; copying a file usually involves passing the path
        # or the file content. To match the "file" behavior, we pass the absolute path.
        path_str = str(file_path.absolute())
        subprocess.run(
            [cls.command, "--clipboard", "--input"], input=path_str.encode(), check=True
        )

    @classmethod
    def clear(cls):
        subprocess.run([cls.command, "--clipboard", "--clear"], check=True)


class WaylandProvider(ClipboardProvider):
    command = "wl-copy"

    @classmethod
    def copy_text(cls, text: str):
        subprocess.run([cls.command], input=text.encode(), check=True)

    @classmethod
    def copy_file(cls, file_path: Path, mime_type: Optional[str] = None):
        mime = mime_type or mimetypes.guess_type(file_path)[0] or "text/plain"
        with open(file_path, "rb") as f:
            subprocess.run([cls.command, "--type", mime], stdin=f, check=True)

    @classmethod
    def clear(cls):
        subprocess.run([cls.command, "--clear"], check=True)


# macOS


class MacProvider(ClipboardProvider):
    command = "pbcopy"

    @classmethod
    def copy_text(cls, text: str):
        subprocess.run([cls.command], input=text.encode(), check=True)

    @classmethod
    def copy_file(cls, file_path: Path, mime_type: Optional[str] = None):
        # macOS uses AppleScript to handle 'file objects' for Finder pasting
        script = f'set the clipboard to (POSIX file "{file_path.absolute()}")'
        subprocess.run(["osascript", "-e", script], check=True)

    @classmethod
    def clear(cls):
        subprocess.run(["osascript", "-e", 'set the clipboard to ""'], check=True)


# Windows


class WindowsProvider(ClipboardProvider):
    command = "powershell"

    @classmethod
    def copy_text(cls, text: str):
        # Using UTF-16 for Windows clipboard compatibility
        process = subprocess.Popen(
            [cls.command, "-command", "Set-Clipboard"], stdin=subprocess.PIPE
        )
        process.communicate(input=text.encode("utf-16"))

    @classmethod
    def copy_file(cls, file_path: Path, mime_type: Optional[str] = None):
        # Set-Clipboard -Path automatically handles the FileDropList format
        cmd = f"Set-Clipboard -Path '{file_path.absolute()}'"
        subprocess.run([cls.command, "-Command", cmd], check=True)

    @classmethod
    def clear(cls):
        subprocess.run([cls.command, "-Command", "Clear-Clipboard"], check=True)


# Manager


class ClipboardManager:
    _provider: Optional[Type[ClipboardProvider]] = None

    @classmethod
    def _resolve(cls) -> Type[ClipboardProvider]:
        """Detects the OS and utility once, then caches the result."""
        if cls._provider:
            return cls._provider

        sys_name = platform.system()
        potential_providers = []

        if sys_name == "Linux":
            potential_providers = [WaylandProvider, XSelProvider, XClipProvider]
        elif sys_name == "Darwin":
            potential_providers = [MacProvider]
        elif sys_name == "Windows":
            potential_providers = [WindowsProvider]

        for provider in potential_providers:
            if provider.is_available():
                cls._provider = provider
                return provider

        raise RuntimeError(f"No supported clipboard utility found for {sys_name}. ")

    @classmethod
    def copy_text(cls, text: str):
        cls._resolve().copy_text(text)

    @classmethod
    def copy_file(cls, path: Union[str, Path], mime_type: Optional[str] = None):
        path_obj = Path(path).resolve()
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {path_obj}")
        cls._resolve().copy_file(path_obj, mime_type)

    @classmethod
    def clear(cls):
        cls._resolve().clear()


# Public API


def copy_text(text: str):
    """Copies plain text to the system clipboard."""
    ClipboardManager.copy_text(text)


def copy_file(path: Union[str, Path], mime_type: Optional[str] = None):
    """
    Copies a file to the clipboard.
    On Desktop OSs, this allows 'Pasting' the file into folders.
    """
    ClipboardManager.copy_file(path, mime_type)


def clear_clipboard():
    """Wipes the clipboard content."""
    ClipboardManager.clear()

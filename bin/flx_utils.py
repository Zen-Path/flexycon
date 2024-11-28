import os
import shutil
import subprocess
from abc import ABC, abstractmethod


def ensure_directories_exist(file_path):
    """
    Ensure all directories leading to the given file path exist.
    """
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)


class ClipboardUtility(ABC):
    """Abstract class for clipboard utilities."""

    command: str  # Command to execute the clipboard utility

    @abstractmethod
    def text(self, text: str):
        """Copy text to the clipboard."""
        pass

    @abstractmethod
    def file(self, file_path: str):
        """Copy a file to the clipboard."""
        pass

    @classmethod
    def can_handle(cls) -> bool:
        """Check if this utility is available on the system."""
        return shutil.which(cls.command) is not None

    @classmethod
    def get_instance(cls):
        """Detect the available clipboard utility and return an instance."""
        for subclass in cls.__subclasses__():
            if subclass.can_handle():
                return subclass()

        raise EnvironmentError("No known clipboard utility is available.")


class XClip(ClipboardUtility):
    command = "xclip"

    def text(self, text: str):
        subprocess.run([self.command, "-sel", "clip"], input=text.encode(), check=True)

    def file(self, file_path: str):
        subprocess.run(
            [self.command, "-sel", "clip", "-t", "image/png", "-i", file_path],
            check=True,
        )


class XSel(ClipboardUtility):
    command = "xsel"

    def text(self, text: str):
        subprocess.run(
            [self.command, "--clipboard", "--input"], input=text.encode(), check=True
        )

    def file(self, file_path: str):
        subprocess.run([self.command, "--clipboard", "--input", file_path], check=True)

import logging
import os
import shutil
import subprocess
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple

from common.logger import logger


@dataclass
class CommandResult:
    return_code: int
    output: str

    @property
    def success(self) -> bool:
        return self.return_code == 0

    def __str__(self) -> str:
        return self.output


def resolve_path(path_parts: List[str]) -> str:
    """Resolve a list of path parts into a single expanded string path."""
    return os.path.expandvars(os.path.join(*path_parts))


def run_command(command: List[str]) -> CommandResult:
    """Run a shell command and return its result."""
    logger.info(f"Running: {command}")

    output = []
    with subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
    ) as process:
        if process.stdout is not None:
            for line in process.stdout:
                output.append(line)
                logger.info(line.strip())

        return_code = process.wait()

    logger.info(f"Command ({command}) finished with return code {return_code}")

    return CommandResult(return_code=return_code, output="\n".join(output))


def prompt_user(prompt, positive_resp=["y"], negative_resp=["n"], default="n"):
    possible_resp = positive_resp + negative_resp
    if default not in possible_resp:
        return False

    default_index = possible_resp.index(default)
    possible_resp[default_index] = possible_resp[default_index].upper()

    try:
        user_resp = input(f"> {prompt} ({'/'.join(possible_resp)}): ").strip().lower()
    except KeyboardInterrupt:
        exit()

    return user_resp in positive_resp


def notify(title: str, message: str = ""):
    """Send a desktop notification."""
    result = subprocess.run(["notify-send", title, message], check=False)
    return result.returncode == 0


def ensure_directory_interactive(path):
    if not os.path.exists(path):
        print(f":: The directory '{path}' does not exist.")
        user_resp = prompt_user("Would you like to create the directory?")
        if user_resp:
            os.makedirs(path)
        else:
            print(":: Operation cancelled by user.")
            sys.exit(1)


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

import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from common.helpers import CommandResult, resolve_path, run_command
from common.logger import logger
from common.variables import flex_scripts
from dotenv import load_dotenv

load_dotenv(flex_scripts / "media_server" / ".env")


class Media(ABC):
    BASE_DIR = Path(os.getenv("DOWNLOAD_DIR") or Path.home() / "Downloads")
    DOWNLOAD_DIR: Path
    FILES_DIR = BASE_DIR / "Files"

    @classmethod
    @abstractmethod
    def download(
        cls,
        urls: List[str],
        range_start: Optional[int] = None,
        range_end: Optional[int] = None,
    ) -> CommandResult:
        pass


class Gallery(Media):
    DOWNLOAD_DIR = Media.BASE_DIR / "Galleries"

    @classmethod
    def download(
        cls,
        urls: List[str],
        range_start: Optional[int] = None,
        range_end: Optional[int] = None,
    ) -> CommandResult:
        """
        Download media using 'gallery-dl'.
        """
        command = [
            "gallery-dl",
            "-o",
            f"base-directory={cls.DOWNLOAD_DIR}",
            "--no-colors",
            *urls,
        ]

        if range_start or range_end:
            command += ["--range", f"{range_start or 0}-{range_end or ""}"]

        return run_command(command)

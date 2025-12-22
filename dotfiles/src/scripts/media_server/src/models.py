import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Tuple

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
        cls, urls: List[str], range_parts: Optional[Tuple[int, int]] = None
    ) -> CommandResult:
        pass


class Gallery(Media):
    DOWNLOAD_DIR = Media.BASE_DIR / "Galleries"

    @classmethod
    def _build_command(
        cls, urls: List[str], range_parts: Optional[Tuple[int, int]] = None
    ) -> List[str]:
        # logger.debug(cls.DOWNLOAD_DIR)

        gallery_dl_cmd = (
            "gallery-dl"
            if shutil.which("gallery-dl")
            else str(resolve_path(["$FLEXYCON_HOME", "venv", "bin", "gallery-dl"]))
        )
        if gallery_dl_cmd != "gallery-dl":
            logger.debug(f"Gallery-dl command: {gallery_dl_cmd}")

        command = [
            gallery_dl_cmd,
            "-o",
            f"base-directory={cls.DOWNLOAD_DIR}",
            "--no-colors",
            *urls,
        ]

        if range_parts:
            command += ["--range", f"{range_parts[0]}-{range_parts[1]}"]

        exec_cmd = (
            f"mkdir -p {cls.FILES_DIR}; "
            f'if [ -f "{cls.FILES_DIR}/{{_filename}}" ]; then rm {{_path}}; '
            f"else mv {{_path}} {cls.FILES_DIR}; fi && "
            f"ln -s {cls.FILES_DIR}/{{_filename}} {{_directory}}"
        )

        # command += ["--exec", exec_cmd]

        return command

    @classmethod
    def download(
        cls, urls: List[str], range_parts: Optional[Tuple[int, int]] = None
    ) -> CommandResult:
        command = cls._build_command(urls, range_parts)
        return run_command(command)

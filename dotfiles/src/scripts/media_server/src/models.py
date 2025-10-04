import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

from common.helpers import CommandResult, resolve_path, run_command
from common.logger import logger
from dotenv import load_dotenv

load_dotenv()


class Gallery:
    BASE_DIR = Path(os.getenv("DOWNLOAD_DIR") or Path.home() / "Downloads")
    GALLERIES_DIR = BASE_DIR / "Galleries"
    FILES_DIR = BASE_DIR / "Files"

    @staticmethod
    def ensure_directories() -> None:
        if not Gallery.FILES_DIR.exists():
            Gallery.FILES_DIR.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directory '{Gallery.FILES_DIR}' created.")

    @staticmethod
    def build_command(urls: List[str], range_: Optional[Tuple[int, int]]) -> List[str]:
        gallery_dl_cmd = (
            "gallery-dl"
            if shutil.which("gallery-dl")
            else resolve_path(["$FLEXYCON_HOME", "venv", "bin", "gallery-dl"])
        )
        if gallery_dl_cmd != "gallery-dl":
            logger.debug(f"Gallery-dl command: {gallery_dl_cmd}")

        command = [
            gallery_dl_cmd,
            "-o",
            f"base-directory={Gallery.GALLERIES_DIR}",
            *urls,
        ]

        if range_:
            command += ["--range", f"{range_[0]}-{range_[1]}"]

        exec_cmd = (
            f"mkdir -p {Gallery.FILES_DIR}; "
            f'if [ -f "{Gallery.FILES_DIR}/{{_filename}}" ]; then rm {{_path}}; '
            f"else mv {{_path}} {Gallery.FILES_DIR}; fi && "
            f"ln -s {Gallery.FILES_DIR}/{{_filename}} {{_directory}}"
        )

        # command += ["--exec", exec_cmd]

        return command

    @staticmethod
    def download(
        urls: List[str], range_: Optional[Tuple[int, int]] = None
    ) -> CommandResult:
        # Gallery.ensure_directories()

        command = Gallery.build_command(urls, range_)

        return run_command(command)

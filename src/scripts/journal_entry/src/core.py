import os
import subprocess
from datetime import datetime
from pathlib import Path

from common.io_utilities import ensure_directory_interactive
from common.logger import log


def open_journal_entry(target_date: datetime) -> bool:
    year_fmt = str(target_date.year)
    month_num_fmt = f"{target_date.month:02}"
    day_fmt = f"{target_date.day:02}"

    journal_home_path = os.getenv("JOURNAL_HOME")
    if not journal_home_path:
        raise EnvironmentError("Environment variable 'JOURNAL_HOME' is not set.")

    file_name = f"{month_num_fmt}.{day_fmt}.md"
    file_path = Path(journal_home_path) / year_fmt / month_num_fmt / file_name
    log.info(f"File path: {str(file_path)!r}")

    if not ensure_directory_interactive(file_path.parent):
        return False

    editor = os.getenv("EDITOR", "vim")
    log.debug(f"Editor: {editor!r}")

    subprocess.run([editor, file_path])
    return True


def get_journal_entry_path(target_date: datetime) -> Path | None:
    journal_home_path = os.getenv("JOURNAL_HOME")
    if not journal_home_path:
        raise EnvironmentError("Environment variable 'JOURNAL_HOME' is not set.")

    return (
        Path(journal_home_path)
        / target_date.strftime("%Y")
        / target_date.strftime("%m")
        / f"{target_date.strftime('%m.%d')}.md"
    )

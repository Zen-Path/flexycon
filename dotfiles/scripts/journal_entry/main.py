#!/usr/bin/env python3

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from shared.args import format_help_choices
from shared.date_args import add_date_args, resolve_date
from shared.helpers import ensure_directory_interactive, run_command
from shared.logger import setup_logging

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Open a journal entry in the user's $EDITOR for a date."
        "If no $EDITOR is found, it defaults to 'vim'."
    )

    add_date_args(parser, format_help_choices)

    parser.add_argument(
        "--get-journal-entry-path",
        action="store_true",
        help="return the path of the journal entry",
    )

    parser.add_argument("--verbose", action="store_true", help="enable debug output")

    return parser.parse_args()


def open_journal_entry(target_date):
    year = str(target_date.year)
    month_num = f"{target_date.month:02}"
    day = f"{target_date.day:02}"

    journal_home_dir = os.getenv("JOURNAL_HOME")

    if not journal_home_dir:
        raise EnvironmentError("JOURNAL_HOME environment variable is not set.")

    journal_year_dir = os.path.join(journal_home_dir, year)
    journal_month_dir = os.path.join(journal_year_dir, month_num)

    ensure_directory_interactive(journal_year_dir)
    ensure_directory_interactive(journal_month_dir)

    file_path = os.path.join(journal_month_dir, f"{month_num}.{day}.md")
    logger.info(f"File path: {file_path}")

    editor = os.getenv("EDITOR", "vim")
    logger.debug(f"Editor: {editor}")

    subprocess.run([editor, file_path])


def get_journal_entry_path(target_date) -> Optional[Path]:
    journal_home_var = os.getenv("JOURNAL_HOME")
    if not journal_home_var:
        logger.warning(f"Missing environment variable 'JOURNAL_HOME'")

    journal_home = journal_home_var or (Path.home() / "Documents" / "Journal")

    return (
        Path(journal_home)
        / target_date.strftime("%Y")
        / target_date.strftime("%m")
        / f"{target_date.strftime('%m.%d')}.md"
    )


# TODO: add tests
def main():
    args = parse_args()

    setup_logging(verbose=args.verbose)

    target_date = resolve_date(args)

    if args.get_journal_entry_path:
        path = get_journal_entry_path(target_date)
        if not path:
            logger.error(
                "Could not find journal entry for %s", target_date.strftime("%Y-%m-%d")
            )
            sys.exit(1)
        print(path)
        return

    open_journal_entry(target_date)


if __name__ == "__main__":
    main()

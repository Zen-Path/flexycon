#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from common.args import add_date_args, resolve_date
from common.helpers import ensure_directory_interactive
from common.logger import logger, setup_logging


def build_parser():
    parser = argparse.ArgumentParser(
        description="Open a journal entry in the user's $EDITOR for a date."
        "If no $EDITOR is found, it defaults to 'vim'."
    )

    add_date_args(parser)

    parser.add_argument(
        "--get-journal-entry-path",
        action="store_true",
        help="return the path of the journal entry",
    )

    parser.add_argument("--verbose", action="store_true", help="enable debug output")

    return parser


def open_journal_entry(target_date: datetime):
    year_fmt = str(target_date.year)
    month_num_fmt = f"{target_date.month:02}"
    day_fmt = f"{target_date.day:02}"

    journal_home_path = os.getenv("JOURNAL_HOME")
    if not journal_home_path:
        raise EnvironmentError("Environment variable 'JOURNAL_HOME' is not set.")

    file_name = f"{month_num_fmt}.{day_fmt}.md"
    file_path = Path(journal_home_path) / year_fmt / month_num_fmt / file_name
    logger.info(f"File path: {file_path!r}")

    ensure_directory_interactive(file_path.parent)

    editor = os.getenv("EDITOR", "vim")
    logger.debug(f"Editor: {editor!r}")

    subprocess.run([editor, file_path])


def get_journal_entry_path(target_date) -> Path | None:
    journal_home_path = os.getenv("JOURNAL_HOME")
    if not journal_home_path:
        raise EnvironmentError("Environment variable 'JOURNAL_HOME' is not set.")

    return (
        Path(journal_home_path)
        / target_date.strftime("%Y")
        / target_date.strftime("%m")
        / f"{target_date.strftime('%m.%d')}.md"
    )


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.WARNING)

    target_date = resolve_date(args)
    logger.info(f"Target date: {target_date.strftime('%Y-%m-%d')}")

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

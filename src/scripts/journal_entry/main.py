#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import sys

from common.args import add_date_args, resolve_date
from common.helpers import get_version
from common.logger import logger, setup_logging
from scripts.journal_entry.src.core import get_journal_entry_path, open_journal_entry


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="journal_entry",
        description="Open a journal entry in the user's $EDITOR for a date."
        "If no $EDITOR is found, it defaults to 'vim'.",
    )

    add_date_args(parser)

    parser.add_argument(
        "--get-journal-entry-path",
        action="store_true",
        help="return the path of the journal entry",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    return parser


def main() -> None:
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.WARNING)
    logger.debug(args)

    target_date = resolve_date(args)
    logger.info(f"Target date: {target_date.strftime('%Y-%m-%d')}")

    if args.get_journal_entry_path:
        path = get_journal_entry_path(target_date)
        if not path:
            logger.error(
                f"Could not find journal entry for {target_date.strftime('%Y-%m-%d')}"
            )
            sys.exit(1)

        print(path)
        return

    if not open_journal_entry(target_date):
        sys.exit(1)


if __name__ == "__main__":
    main()

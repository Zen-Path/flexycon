#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import sys

from common.cmd_utilities import run_cmd
from common.helpers import NotificationSystem, get_version
from common.logger import log, setup_logging
from common.packages.clipboard_utilities import ClipboardManager
from common.prompt_utilities import prompt_options
from scripts.unicode_selector.data.characters import CHARACTERS
from scripts.unicode_selector.src.core import format_char_entries


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="unicode_selector",
        description="Prompt the user for a unicode character and copies or inserts it.",
    )

    parser.add_argument(
        "-i", "--insert-char", action="store_true", help="insert the selected char"
    )
    parser.add_argument(
        "--no-copy", action="store_true", help="do not copy the selected char"
    )
    parser.add_argument(
        "--no-notify",
        action="store_true",
        help="do not notify user of the selected char",
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

    setup_logging(log, logging.DEBUG if args.verbose else logging.ERROR)

    char_categories = list(CHARACTERS.keys())
    log.debug(f"char_categories: {char_categories}")

    # Prompt user for a category or common emojis
    prompt_result = prompt_options(
        prompt="Emoji",
        options=char_categories + format_char_entries(CHARACTERS["emoji"]),
        list_view_item_count=30,
    )

    if prompt_result is None:
        log.error("Selection is empty.")
        sys.exit(1)

    _idx, selection = prompt_result

    if selection in char_categories:
        prompt_result = prompt_options(
            prompt="Emoji",
            options=format_char_entries(CHARACTERS[selection]),
            list_view_item_count=30,
        )

        if prompt_result is None:
            log.error("Selection is empty.")
            sys.exit(1)

        _idx, selection = prompt_result

    selection_parts = selection.split(" - ", maxsplit=1)
    log.info(f"Selection parts: {selection_parts}")

    # skip empty or malformed lines
    if len(selection_parts) < 2:
        return

    char, name = selection_parts
    log.info(f"char: {str(char)!r}, name: {str(name)!r}")

    if args.insert_char:
        run_cmd(["xdotool", "type", char])
        log.info("Character inserted.")

    if not args.no_copy:
        ClipboardManager.copy_text(char)
        log.info("Character copied.")

        if not args.no_notify:
            NotificationSystem.run("Character copied", f"Copied {str(char)!r}.")


if __name__ == "__main__":
    main()

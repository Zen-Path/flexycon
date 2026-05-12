#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import subprocess
import sys

from common.helpers import NotificationSystem, get_version, run_command
from common.logger import logger, setup_logging
from common.prompt_utilities import prompt_options
from scripts.select_unicode.data import CHARS


def format_char_entries(chars: dict[str, str]) -> list[str]:
    result: list[str] = []
    for char in chars:
        result.append(f"{char} - {chars[char]}")
    return result


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="select_unicode",
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


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.ERROR)

    char_categories = list(CHARS.keys())
    logger.debug(f"char_categories: {char_categories}")

    # Prompt user for a category or common emojis
    prompt_result = prompt_options(
        prompt="Emoji",
        options=char_categories + format_char_entries(CHARS["emoji"]),
        list_view_item_count=30,
    )

    if prompt_result is None:
        logger.error("Selection is empty.")
        sys.exit(1)

    _idx, selection = prompt_result

    if selection in char_categories:
        prompt_result = prompt_options(
            prompt="Emoji",
            options=format_char_entries(CHARS[selection]),
            list_view_item_count=30,
        )

        if prompt_result is None:
            logger.error("Selection is empty.")
            sys.exit(1)

        _idx, selection = prompt_result

    selection_parts = selection.split(" - ", maxsplit=1)
    logger.info(f"Selection parts: {selection_parts}")

    # skip empty or malformed lines
    if len(selection_parts) < 2:
        return

    char, name = selection_parts
    logger.info(f"char: {str(char)!r}, name: {str(name)!r}")

    if args.insert_char:
        run_command(["xdotool", "type", char])
        logger.info("Character inserted.")

    if not args.no_copy:
        subprocess.run(["xclip", "-selection", "clipboard"], input=char.encode())
        logger.info("Character copied.")

        if not args.no_notify:
            NotificationSystem.run("Character copied", f"Copied {str(char)!r}.")


if __name__ == "__main__":
    main()

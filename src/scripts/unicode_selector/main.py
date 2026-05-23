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
from scripts.unicode_selector.src.core import braille_bin_to_symbol, format_char_entries


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    global_parent = argparse.ArgumentParser(add_help=False)
    global_parent.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )

    global_parent.add_argument(
        "-i", "--insert-char", action="store_true", help="insert the selected char"
    )
    global_parent.add_argument(
        "--no-copy", action="store_true", help="do not copy the selected char"
    )
    global_parent.add_argument(
        "--no-notify",
        action="store_true",
        help="do not notify user of the selected char",
    )

    parser = argparse.ArgumentParser(
        prog="unicode_selector",
        description="Prompt the user for a unicode character and copies or inserts it.",
        parents=[global_parent],
    )

    subparsers = parser.add_subparsers(dest="mode", metavar="MODE", help="HELP_MSG")

    braille_sp = subparsers.add_parser(
        name="braille",
        parents=[global_parent],
        help="braille pattern operations",
    )
    braille_sp.add_argument(
        "patterns",
        nargs="+",
        metavar="PATTERN",
        help="binary representation of a Braille symbol",
    )
    braille_sp.add_argument(
        "-r",
        "--by-row",
        action="store_true",
        help="treat PATTERN as the rows of a Braille symbol",
    )
    braille_sp.add_argument(
        "-f",
        "--format",
        action="store_true",
        help="make the output more readable",
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    return parser


def main() -> None:
    args = build_parser().parse_args()

    setup_logging(log, logging.DEBUG if args.verbose else logging.ERROR)
    log.debug(args)

    if args.mode == "braille":
        results = braille_bin_to_symbol(
            args.patterns, CHARACTERS["braille"], args.by_row
        )
        if not results:
            log.debug("No braille results.")
            return

        if args.format:
            print(
                "\n".join(
                    [f"{symbol} - {pattern}" for symbol, pattern in results.items()]
                )
            )
        else:
            print(list(results.keys()))

        return

    row_count = 20

    char_categories = list(CHARACTERS.keys())
    log.debug(f"char_categories: {char_categories}")

    # Prompt user for a category or common emojis
    selection = prompt_options(
        prompt="Emoji",
        options=char_categories + format_char_entries(CHARACTERS["emoji"]),
        row_count=row_count,
    )

    if selection is None:
        log.error("Selection is empty.")
        sys.exit(1)

    if selection in char_categories:
        selection = prompt_options(
            prompt="Emoji",
            options=format_char_entries(CHARACTERS[selection]),
            row_count=row_count,
        )

        if selection is None:
            log.error("Selection is empty.")
            sys.exit(1)

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

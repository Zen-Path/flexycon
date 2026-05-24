#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging

from common.helpers import get_version
from common.logger import log, setup_logging
from scripts.unicode_selector.src.core import (
    handle_braille_mode,
    handle_default_mode,
)


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    global_parent = argparse.ArgumentParser(add_help=False)
    global_parent.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )
    global_parent.add_argument(
        "--no-copy",
        dest="copy",
        action="store_false",
        default=True,
        help="do not copy selection to clipboard",
    )

    parser = argparse.ArgumentParser(
        prog="unicode_selector",
        description="Prompt the user for a unicode character and copies or inserts it.",
        parents=[global_parent],
    )

    subparsers = parser.add_subparsers(
        dest="mode",
        metavar="MODE",
        help="Operation mode to execute",
    )

    # BRAILLE
    braille_sp = subparsers.add_parser(
        name="braille",
        parents=[global_parent],
        help="translate binary patterns, ASCII, or encode Braille symbols",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    braille_sp.add_argument(
        "patterns",
        nargs="+",
        metavar="PATTERN",
        help="one or more target patterns to convert",
    )
    braille_sp.add_argument(
        "-t",
        "--pattern-type",
        choices=["bin_col", "bin_row", "ascii", "encode"],
        default="bin_col",
        help=(
            "how to interpret input patterns:\n"
            "  bin_col  - binary string processed by columns ('10100101' == '⢕')\n"
            "  bin_row  - binary string processed by rows ('10100101' == '⢣')\n"
            "  ascii    - direct ASCII characters to turn into Braille symbol\n"
            "  encode   - translate a Braille symbol back to binary"
        ),
    )
    braille_sp.add_argument(
        "-p",
        "--pretty-print",
        action="store_true",
        help="pretty-print the final output",
    )

    # DEFAULT MODE
    parser.add_argument(
        "-i",
        "--insert-selection",
        action="store_true",
        help="automatically type out selection",
    )
    parser.add_argument(
        "--no-notify",
        dest="notify",
        action="store_false",
        default=True,
        help="do not notify user of selected chars",
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
        handle_braille_mode(args)
        return

    handle_default_mode(args)


if __name__ == "__main__":
    main()

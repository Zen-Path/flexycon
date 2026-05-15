#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging

from common.helpers import get_version
from common.logger import log, setup_logging


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="PROG_NAME",
        description="DESCRIPTION.",
    )

    # ---

    # Choices
    parser.add_argument(
        "-c",
        "--choice",
        choices=["one", "two", "three"],
        metavar="METAVAR",
        help="HELP_MSG",
    )

    # Negative bool store
    parser.add_argument(
        "-n",
        "--no-dry-run",
        dest="DEST",
        action="store_false",
        default=True,
        help="HELP_MSG",
    )

    # Type + default
    parser.add_argument(
        "-i",
        "--indentation",
        type=int,
        default=4,
        help="HELP_MSG",
    )

    # Multiple data
    parser.add_argument("NAME", nargs="+", type=int, help="HELP_MSG")

    # Action and exit
    parser.add_argument(
        "-l",
        "--list-shortcuts",
        action="store_true",
        help="ACTION and exit",
    )

    # ---

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    return parser


def subparser_parser(options: list[str]) -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    global_parent = argparse.ArgumentParser(add_help=False)
    global_parent.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )

    parser = argparse.ArgumentParser(
        prog="PROG",
        description="DESCRIPTION.",
        parents=[global_parent],
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    # SUBCOMMANDS
    cmd_parent = argparse.ArgumentParser(add_help=False)
    cmd_parent.add_argument("-s", "--max-size", type=int)

    subparsers = parser.add_subparsers(dest="DEST", metavar="METAVAR", help="HELP_MSG")

    for opt in options:
        subparsers.add_parser(
            name=opt,
            parents=[global_parent, cmd_parent],
            help="HELP_MSG",
        )

    return parser


def main() -> None:
    args = build_parser().parse_args()

    setup_logging(log, logging.DEBUG if args.verbose else logging.ERROR)
    log.debug(args)


if __name__ == "__main__":
    main()

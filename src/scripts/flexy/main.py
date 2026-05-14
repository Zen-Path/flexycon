#!/usr/bin/env python3

import argparse
import logging

from common.helpers import get_version
from common.logger import logger, setup_logging
from scripts.flexy.src import targets
from scripts.flexy.src.helpers import ACTIONS, ActionInfo

__all__ = ["targets"]


def build_parser(actions: dict[str, ActionInfo]) -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="flexy",
        description="Help utility for managing flexycon.",
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    # SUBCOMMANDS
    cmd_parent = argparse.ArgumentParser(add_help=False)
    cmd_parent.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )

    subparsers = parser.add_subparsers(
        dest="action", metavar="ACTION", required=True, help="System action"
    )

    for name, meta in actions.items():
        subparsers.add_parser(
            name=name,
            parents=[cmd_parent],
            help=meta["description"],
        )

    return parser


def main() -> None:
    args = build_parser(ACTIONS).parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.INFO)
    logger.debug(args)

    if args.action in ACTIONS:
        ACTIONS[args.action]["fn"]()


if __name__ == "__main__":
    main()

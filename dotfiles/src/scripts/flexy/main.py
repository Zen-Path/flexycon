#!/usr/bin/env python3

import argparse
import logging

from common.helpers import get_version
from common.logger import logger, setup_logging
from scripts.flexy.src.targets import TARGETS


def build_parser(targets):
    parser = argparse.ArgumentParser(
        prog="flexy", description="Help utility for managing flexycon."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Dynamically add subcommands
    for name, meta in targets.items():
        subparsers.add_parser(name, help=meta["description"])

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    return parser


def main():
    args = build_parser(TARGETS).parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.INFO)

    if args.command in TARGETS:
        TARGETS[args.command]["fn"]()


if __name__ == "__main__":
    main()

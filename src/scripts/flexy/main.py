#!/usr/bin/env python3

import argparse
import logging

from common.helpers import get_version
from common.logger import log, setup_logging
from scripts.flexy.src.helpers import Action
from scripts.flexy.src.targets import (
    clean,
    install,
    install_system_packages,
    setup,
    setup_virtual_env,
    uninstall,
)

ACTIONS: list[Action] = [
    Action(
        name="install",
        description="install and apply configuration",
        fn=install,
    ),
    Action(
        name="uninstall",
        description="clean project and remove flexycon's data",
        fn=uninstall,
    ),
    Action(
        name="clean",
        description="remove caches and temporary files",
        fn=clean,
    ),
    Action(
        name="setup",
        description="setup venv, dependencies, packages etc",
        fn=setup,
    ),
    Action(
        name="install_packages",
        description="setup project and install dependencies",
        fn=install_system_packages,
    ),
    Action(
        name="setup_venv",
        description="create and setup a virtual environment",
        fn=setup_virtual_env,
    ),
]


def build_parser(actions: list[Action]) -> argparse.ArgumentParser:
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

    subparsers = parser.add_subparsers(dest="action", metavar="ACTION", required=True)

    for action in actions:
        subparsers.add_parser(
            name=action.name,
            parents=[cmd_parent],
            help=action.description,
        )

    return parser


def main() -> None:
    args = build_parser(ACTIONS).parse_args()

    setup_logging(log, logging.DEBUG if args.verbose else logging.INFO)
    log.debug(args)

    for action in ACTIONS:
        if action.name == args.action:
            action.fn()


if __name__ == "__main__":
    main()

#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging

from common.cmd_utilities import run_cmd_background
from common.helpers import NotificationSystem, get_version
from common.logger import logger, setup_logging
from common.statusbar import EDITOR, TERMINAL, MouseButton, handle_block_button

ACTIONS = {
    MouseButton.LEFT: lambda: 0,
    MouseButton.MIDDLE: lambda: 0,
    MouseButton.RIGHT: lambda: NotificationSystem.run(
        "⏺️ SCRIPT_NAME",
        "SCRIPT_DESCRIPTION.\n"
        "\n<b>Actions</b>\n"
        "- Left click to ACTION\n"
        "- Middle click to ACTION\n"
        "- Right click to show this message\n"
        "- Extra button click to edit script\n"
        "- Scroll to ACTION",
    ),
    MouseButton.EXTRA_3: lambda: run_cmd_background([TERMINAL, "-e", EDITOR, __file__]),
}


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="PROG_NAME",
        description="DESCRIPTION.",
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

    setup_logging(logger, logging.DEBUG if args.verbose else logging.ERROR)
    logger.debug(args)

    handle_block_button(ACTIONS)

    print("CHANGE_ME")


if __name__ == "__main__":
    main()

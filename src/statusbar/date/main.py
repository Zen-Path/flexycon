#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
from datetime import datetime

from common.cmd_utilities import run_cmd_background
from common.helpers import get_version
from common.logger import log, setup_logging
from common.notification_utilities import Notification
from common.statusbar import (
    EDITOR,
    TERMINAL,
    MouseButton,
    handle_block_button,
)
from statusbar.date.src.core import open_calcurse, show_info

ACTIONS = {
    MouseButton.LEFT: show_info,
    MouseButton.MIDDLE: open_calcurse,
    MouseButton.RIGHT: lambda: Notification(
        "📅 Date",
        "Show current date and time.\n"
        "\n<b>Actions</b>\n"
        "- Left   : Show calendar and appointments\n"
        "- Middle : Open 'calcurse'\n"
        "- Right  : Show this message\n"
        "- Extra  : Edit this script",
    ).send(),
    MouseButton.EXTRA_3: lambda: run_cmd_background(
        [TERMINAL, "-e", EDITOR, "{{@@ _dotfile_abs_src @@}}"]
    ),
}


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="sb_date",
        description="Statusbar script for date, calendar, and appointments.",
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
    log.debug(args)

    handle_block_button(ACTIONS)

    print(datetime.now().strftime("%d %b (%a) %H:%M"))


if __name__ == "__main__":
    main()

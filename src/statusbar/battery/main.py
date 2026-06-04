#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging

from common.cmd_utilities import run_cmd_background
from common.helpers import get_version
from common.logger import log, setup_logging
from common.notification_utilities import Notification
from common.statusbar import (
    MouseButton,
    handle_block_button,
)
from common.variables import EDITOR, TERMINAL
from statusbar.battery.src.core import adjust_backlight, get_battery_info

ACTIONS = {
    MouseButton.SCROLL_UP: lambda: adjust_backlight(10),
    MouseButton.SCROLL_DOWN: lambda: adjust_backlight(-10),
    MouseButton.RIGHT: lambda: Notification(
        " Battery",
        "Show battery(ies) status.\n"
        "\n<b>Actions</b>\n"
        "- Right click to show this message\n"
        "- Scroll : Adjust backlight\n"
        "\n<b>Status</b>\n"
        ": discharging\n"
        ": not charging\n"
        ": stagnant charge\n"
        ": charging\n"
        ": charged\n"
        ": low battery\n",
    ).send(),
    MouseButton.EXTRA_3: lambda: run_cmd_background(
        [TERMINAL, "-e", EDITOR, "{{@@ _dotfile_abs_src @@}}"]
    ),
}


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="sb_battery",
        description="Statusbar script for battery levels and backlight.",
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

    print(get_battery_info())


if __name__ == "__main__":
    main()

#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import re
import shutil
from datetime import datetime

from common.cmd_utilities import run_cmd, run_cmd_background
from common.helpers import NotificationSystem, get_version
from common.logger import logger, setup_logging
from common.statusbar import (
    EDITOR,
    TERMINAL,
    MouseButton,
    handle_block_button,
)


def get_calendar() -> str | None:
    """Gets the current calendar and highlights the current day."""
    try:
        current_day = datetime.now().strftime("%-d")
        result = run_cmd(["cal"])
        if not result.success:
            return None

        highlighted = re.sub(
            rf"\b({current_day})\b",
            r"<span color='#1D2021'><b>\1</b></span>",
            result.output,
        )
        return highlighted

    except Exception as e:
        logger.error(f"Could not retrieve calendar: {e}")

    return None


def get_appointments() -> str | None:
    """Returns upcoming appointments from calcurse."""
    if not shutil.which("calcurse"):
        logger.error(msg="Binary 'calcurse' not found.")
        return None

    try:
        result = run_cmd(["calcurse", "-d3"])
        if not result.success:
            return None

        return result.output if result.output else "No upcoming appointments."

    except Exception as e:
        logger.error(f"Could not retrieve appointments: {e}")

    return None


def show_info() -> None:
    """Triggers notifications for both calendar and appointments."""
    NotificationSystem.run("Calendar", get_calendar())

    appointments = get_appointments()
    if appointments:
        NotificationSystem.run("Appointments", appointments)


def open_calcurse() -> None:
    """Opens calcurse in the terminal if installed."""
    if not shutil.which("calcurse"):
        logger.error(msg="Binary 'calcurse' not found.")
        return None

    run_cmd_background([TERMINAL, "-e", "calcurse"])


ACTIONS = {
    MouseButton.LEFT: show_info,
    MouseButton.MIDDLE: open_calcurse,
    MouseButton.RIGHT: lambda: NotificationSystem.run(
        "📅 Date module",
        "Show the current date and time.\n"
        "\n<b>Actions</b>\n"
        "- Left click to show calendar and appointments\n"
        "- Middle click to open 'calcurse'\n"
        "- Right click to show this message\n"
        "- Extra button to edit script",
    ),
    MouseButton.EXTRA_3: lambda: run_cmd_background([TERMINAL, "-e", EDITOR, __file__]),
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

    setup_logging(logger, logging.DEBUG if args.verbose else logging.ERROR)
    logger.debug(args)

    handle_block_button(ACTIONS)

    print(datetime.now().strftime("%d %b (%a) %H:%M"))


if __name__ == "__main__":
    main()

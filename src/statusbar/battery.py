#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
from pathlib import Path

from common.cmd_utilities import run_cmd, run_cmd_background
from common.helpers import NotificationSystem, get_version
from common.logger import logger, setup_logging
from common.statusbar import (
    EDITOR,
    TERMINAL,
    MouseButton,
    handle_block_button,
)


def adjust_backlight(amount: int) -> None:
    """Adjusts backlight using xbacklight."""
    flag = "-inc" if amount > 0 else "-dec"
    try:
        run_cmd(["xbacklight", flag, str(abs(amount))])
    except Exception as e:
        logger.error(f"Failed to adjust backlight: {e}")


def get_battery_info() -> str:
    batteries = sorted(Path("/sys/class/power_supply/").glob("BAT*"))
    output_parts: list[str] = []

    status_map = {
        "Full": "",
        "Discharging": "",
        "Charging": "",
        "Not charging": "",
        "Unknown": "",
    }

    for battery in batteries:
        try:
            status = (battery / "status").read_text().strip()
            capacity = int((battery / "capacity").read_text().strip())

            icon = status_map.get(status, "")
            warn = ""
            if status == "Discharging" and capacity <= 25:
                warn = ""

            output_parts.append(f"{icon}{warn}{capacity}%")
        except (FileNotFoundError, ValueError) as e:
            logger.debug(f"Could not read battery {battery.name}: {e}")
            continue

    return " ".join(output_parts)


ACTIONS = {
    MouseButton.SCROLL_UP: lambda: adjust_backlight(10),
    MouseButton.SCROLL_DOWN: lambda: adjust_backlight(-10),
    MouseButton.RIGHT: lambda: NotificationSystem.run(
        " Battery",
        "Show battery(ies) status\n"
        "\n<b>Actions</b>\n"
        "- Scroll : Adjust backlight"
        "\n<b>Status</b>\n"
        ": discharging\n"
        ": not charging\n"
        ": stagnant charge\n"
        ": charging\n"
        ": charged\n"
        ": low battery\n",
    ),
    MouseButton.EXTRA_3: lambda: run_cmd_background([TERMINAL, "-e", EDITOR, __file__]),
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

    setup_logging(logger, logging.DEBUG if args.verbose else logging.ERROR)
    logger.debug(args)

    handle_block_button(ACTIONS)

    print(get_battery_info())


if __name__ == "__main__":
    main()

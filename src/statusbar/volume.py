#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}


import argparse
import logging

from common.cmd_utilities import run_cmd, run_cmd_background
from common.helpers import NotificationSystem, SoundUtility, get_version
from common.logger import logger, setup_logging
from common.statusbar import (
    EDITOR,
    STATUSBAR,
    TERMINAL,
    MouseButton,
    handle_block_button,
)

ACTIONS = {
    MouseButton.LEFT: lambda: (
        run_cmd(["setsid", "-w", "-f", TERMINAL, "-e", "pulsemixer"]),
        run_cmd(["pkill", "-RTMIN+10", STATUSBAR]),
    ),
    MouseButton.MIDDLE: SoundUtility.toggle_mute,
    MouseButton.RIGHT: lambda: NotificationSystem.run(
        "📢 Volume",
        "Show sound volume, 🔇 if muted.\n"
        "\n<b>Actions</b>\n"
        "- Left   : Open 'pulsemixer'\n"
        "- Middle : Mute\n"
        "- Right  : Show this message\n"
        "- Scroll : Update sound volume\n"
        "- Extra  : Edit this script",
    ),
    MouseButton.SCROLL_UP: lambda: SoundUtility.update_volume(2),
    MouseButton.SCROLL_DOWN: lambda: SoundUtility.update_volume(-2),
    MouseButton.EXTRA_3: lambda: run_cmd_background([TERMINAL, "-e", EDITOR, __file__]),
}


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="sb_volume",
        description="Statusbar script to manage sound and get volume.",
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

    setup_logging(logger, logging.DEBUG if args.verbose else logging.WARNING)
    logger.debug(args)

    handle_block_button(ACTIONS)

    volume_result = SoundUtility.get_volume()
    if volume_result is None:
        print("⛔ Connection")
        return

    volume, is_muted = volume_result

    if is_muted:
        icon = "🔇"
    else:
        if volume >= 70:
            icon = "🔊"
        elif volume >= 30:
            icon = "🔉"
        else:
            icon = "🔈"

    print(f"{icon}{volume}%")


if __name__ == "__main__":
    main()

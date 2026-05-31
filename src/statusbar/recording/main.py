#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging

from common.cmd_utilities import run_cmd_background
from common.helpers import get_version
from common.logger import log, setup_logging
from common.notification_utilities import Notification, NotificationSystem
from common.statusbar import (
    EDITOR,
    TERMINAL,
    MouseButton,
    handle_block_button,
)
from statusbar.recording.src.core import RECORDING_ICON_PATH, stop_recording

# TODO: Implement pause recording feature
ACTIONS = {
    MouseButton.LEFT: stop_recording,
    MouseButton.MIDDLE: lambda: NotificationSystem.set_paused("toggle"),
    MouseButton.RIGHT: lambda: Notification(
        "⏺️ Recording",
        "Show recording status and info.\n"
        "\n<b>Actions</b>\n"
        "- Left   : Stop recording\n"
        "- Middle : Toggle notifications\n"
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
        prog="sb_recording",
        description="Statusbar script to manage screen recording.",
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

    setup_logging(log, logging.DEBUG if args.verbose else logging.WARNING)
    log.debug(args)

    handle_block_button(ACTIONS)

    if not RECORDING_ICON_PATH.exists():
        return

    recording_icon = RECORDING_ICON_PATH.read_text().strip() or "⏺️"

    # Notifications can be paused to prevent interruptions
    are_notifications_paused = NotificationSystem.get_paused()
    notifications_suffix = "⏸️" if are_notifications_paused else ""

    print(f"{recording_icon}-{notifications_suffix}🔔")


if __name__ == "__main__":
    main()

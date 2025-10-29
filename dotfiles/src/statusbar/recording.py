#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import os
import signal
import subprocess
import sys
from pathlib import Path

from common.helpers import (
    get_notifications_paused_status,
    notify,
    run_command,
    set_notifications_status,
)
from common.logger import logger, setup_logging
from statusbar.shared import (
    EDITOR,
    TERMINAL,
    MouseButton,
    handle_block_button,
)

RECORDING_ICON_PATH = Path("/tmp/recording_icon")
RECORDING_PID_PATH = Path("/tmp/recording_pid")


def stop_recording():
    if not RECORDING_PID_PATH.exists():
        return

    with RECORDING_PID_PATH.open() as f:
        try:
            recording_pid = int(f.read().strip())
            os.kill(recording_pid, signal.SIGTERM)
        except ValueError:
            print("Invalid PID in file.")
        except ProcessLookupError:
            print(f"No such process: {recording_pid}")

    RECORDING_PID_PATH.unlink(missing_ok=True)


# TODO: Implement pause recording feature
ACTIONS = {
    MouseButton.LEFT: lambda: stop_recording,
    MouseButton.MIDDLE: lambda: set_notifications_status("toggle"),
    MouseButton.RIGHT: lambda: notify(
        "⏺️ Recording module",
        "Shows recording status and info.\n"
        "\n<b>Actions</b>\n"
        "- Left click to stop recording\n"
        "- Middle click to toggle notifications\n"
        "- Right click to show this message\n",
    ),
    MouseButton.EXTRA_3: lambda: run_command([TERMINAL, "-e", EDITOR, __file__]),
}


def build_parser():
    parser = argparse.ArgumentParser(
        description="Statusbar script to manage recordings."
    )

    parser.add_argument("--verbose", action="store_true", help="Enable debug output")

    return parser


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.WARNING)

    handle_block_button(ACTIONS)

    if not RECORDING_ICON_PATH.exists():
        return

    recording_icon = RECORDING_ICON_PATH.read_text().strip() or "⏺️"

    # Notifications can be paused to prevent interruptions
    are_notifications_paused = (
        get_notifications_paused_status().output.strip().lower() == "true"
    )
    notifications_suffix = "⏸️" if are_notifications_paused else ""

    print(f"{recording_icon}-{notifications_suffix}🔔")


if __name__ == "__main__":
    main()

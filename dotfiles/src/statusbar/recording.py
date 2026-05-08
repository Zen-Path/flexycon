#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import os
import signal
from pathlib import Path

from common.helpers import (
    NotificationSystem,
    run_command,
)
from common.logger import logger, setup_logging
from common.statusbar import (
    EDITOR,
    TERMINAL,
    MouseButton,
    handle_block_button,
)

RECORDING_ICON_PATH = Path("/tmp/recording_icon")
RECORDING_PID_PATH = Path("/tmp/recording_pid")


def stop_recording():
    recording_pid = None
    try:
        with RECORDING_PID_PATH.open() as f:
            content = f.read().strip()
        recording_pid = int(content)

        os.kill(recording_pid, signal.SIGTERM)

    except FileNotFoundError:
        return
    except ValueError:
        logger.error(f"Invalid PID in file: {RECORDING_PID_PATH!r}")
    except ProcessLookupError:
        logger.error(f"No such process: {recording_pid!r}")
    except PermissionError:
        logger.error(f"Permissions denied for PID {recording_pid!r}.")
    finally:
        RECORDING_PID_PATH.unlink(missing_ok=True)


# TODO: Implement pause recording feature
ACTIONS = {
    MouseButton.LEFT: lambda: stop_recording,
    MouseButton.MIDDLE: lambda: NotificationSystem.set_paused("toggle"),
    MouseButton.RIGHT: lambda: NotificationSystem.run(
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

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug output"
    )

    return parser


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.WARNING)

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

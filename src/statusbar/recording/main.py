#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import os
import signal
from pathlib import Path

from common.cmd_utilities import run_cmd_background
from common.helpers import NotificationSystem, get_version
from common.logger import log, setup_logging
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
        log.error(f"Invalid PID in file: {RECORDING_PID_PATH!r}")
    except ProcessLookupError:
        log.error(f"No such process: {recording_pid!r}")
    except PermissionError:
        log.error(f"Permissions denied for PID {recording_pid!r}.")
    finally:
        RECORDING_PID_PATH.unlink(missing_ok=True)


# TODO: Implement pause recording feature
ACTIONS = {
    MouseButton.LEFT: stop_recording,
    MouseButton.MIDDLE: lambda: NotificationSystem.set_paused("toggle"),
    MouseButton.RIGHT: lambda: NotificationSystem.run(
        "⏺️ Recording",
        "Shows recording status and info.\n"
        "\n<b>Actions</b>\n"
        "- Left   : Stop recording\n"
        "- Middle : Toggle notifications\n"
        "- Right  : Show this message\n"
        "- Extra  : Edit this script",
    ),
    MouseButton.EXTRA_3: lambda: run_cmd_background([TERMINAL, "-e", EDITOR, __file__]),
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

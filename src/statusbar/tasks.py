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

STATE_FILE = Path.home() / ".local/state/taskwarrior/overdue_tasks"


def get_task_count(filter_str: str) -> int | None:
    """Runs taskwarrior count with the specified filter."""
    try:
        result = run_cmd(["task", filter_str, "count"])
        if not result.success:
            return None

        return int(result.output)
    except Exception as e:
        logger.error(f"Could not get task count: {e}")

    return None


def process_tasks() -> str:
    """Processes task counts and handles overdue notifications."""
    # Ensure state directory exists
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Read previous overdue count
    old_overdue = 0
    if STATE_FILE.exists():
        try:
            old_overdue = int(STATE_FILE.read_text().strip())
        except ValueError:
            pass

    # Get current counts
    pending_tasks = get_task_count("+PENDING") or 0
    overdue_tasks = get_task_count("+OVERDUE") or 0
    due_tasks = pending_tasks - overdue_tasks

    # Update state file
    STATE_FILE.write_text(str(overdue_tasks))

    # Notify if more tasks became overdue
    difference = overdue_tasks - old_overdue
    if difference > 0:
        NotificationSystem.run(
            "⚠️ Taskwarrior Alert",
            f"{difference} task{'s' if difference > 1 else ''} become overdue.",
        )

    # Format output
    if overdue_tasks != 0:
        return f"{due_tasks} {overdue_tasks}"
    return f"{due_tasks}"


ACTIONS = {
    MouseButton.LEFT: lambda: run_cmd_background([TERMINAL, "-e", "taskwarrior-tui"]),
    MouseButton.RIGHT: lambda: NotificationSystem.run(
        " Tasks",
        "Show due and overdue tasks.\n"
        "\n<b>Actions</b>\n"
        "- Left  : Open 'taskwarrior-tui'\n"
        "- Right : Show this message\n"
        "- Extra : Edit this script",
    ),
    MouseButton.EXTRA_3: lambda: run_cmd_background([TERMINAL, "-e", EDITOR, __file__]),
}


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="sb_tasks",
        description="Statusbar script for managing tasks.",
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

    print(process_tasks())


if __name__ == "__main__":
    main()

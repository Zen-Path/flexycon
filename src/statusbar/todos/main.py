#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging

from common.cmd_utilities import run_cmd_background
from common.helpers import NotificationSystem, get_version
from common.logger import log, setup_logging
from common.statusbar import (
    EDITOR,
    TERMINAL,
    MouseButton,
    handle_block_button,
)
from statusbar.todos.src.core import process_tasks

ACTIONS = {
    MouseButton.LEFT: lambda: run_cmd_background([TERMINAL, "-e", "taskwarrior-tui"]),
    MouseButton.RIGHT: lambda: NotificationSystem.run(
        " ToDos",
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
        prog="sb_todos",
        description="Statusbar script for managing ToDos.",
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

    print(process_tasks())


if __name__ == "__main__":
    main()

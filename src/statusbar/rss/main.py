#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging

from common.cmd_utilities import run_cmd_background
from common.helpers import NotificationSystem, get_version
from common.logger import log, setup_logging
from common.statusbar import EDITOR, TERMINAL, MouseButton, handle_block_button
from statusbar.rss.src.core import (
    NEWS_DB_BACKUP,
    get_item_count_db,
    get_unread_count,
    refresh_feeds,
)

ACTIONS = {
    MouseButton.LEFT: lambda: run_cmd_background([TERMINAL, "-e", "newsraft"]),
    MouseButton.MIDDLE: refresh_feeds,
    MouseButton.RIGHT: lambda: NotificationSystem.run(
        " RSS Feed",
        "Show total and unread rss items.\n"
        "\n<b>Actions:</b>\n"
        "- Left   : Open 'newsraft'\n"
        "- Middle : Refresh RSS feeds\n"
        "- Right  : Show this message\n"
        "- Extra  : Edit this script\n"
        "\n<b>Note:</b> Only one instance of 'newsraft' may be running at a time.",
    ),
    MouseButton.EXTRA_3: lambda: run_cmd_background(
        [TERMINAL, "-e", EDITOR, "{{@@ _dotfile_abs_src @@}}"]
    ),
}


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="sb_rss",
        description="Statusbar script to manage news and get unread count.",
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

    unread_count = get_unread_count()
    total_count = get_item_count_db(NEWS_DB_BACKUP)

    if not unread_count:
        print(" ❗err")
    else:
        print(f"{unread_count} / {total_count}")


if __name__ == "__main__":
    main()

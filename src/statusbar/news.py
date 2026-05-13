#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import os
import shutil
from pathlib import Path

from common.cmd_utilities import run_cmd, run_cmd_background
from common.helpers import NotificationSystem, get_version
from common.logger import logger, setup_logging
from common.statusbar import EDITOR, TERMINAL, MouseButton, handle_block_button

NEWS_DIR = (
    Path(os.getenv("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "newsraft"
)
NEWS_DB = NEWS_DIR / "newsraft.sqlite3"
NEWS_DB_BACKUP = NEWS_DIR / "newsraft_backup.sqlite3"


def reload_newsraft() -> bool:
    """Reload newsraft's contents."""
    return run_cmd(["newsraft", "-e", "reload-all"]).success


def _get_unread_newsraft() -> int | None:
    """Get unread items count using newsraft."""
    result = run_cmd(["newsraft", "-e", "print-unread-items-count"])
    if result.success:
        return int(result.output)

    return None


def _get_unread_db(db_path: Path) -> int | None:
    """Get unread items count directly from the database."""
    try:
        # TODO: maybe use sqlite module?
        result = run_cmd(
            [
                "sqlite3",
                f"file:{db_path}?mode=ro",
                "SELECT COUNT(*) FROM items WHERE unread = 1",
            ]
        )
        if result.success:
            return int(result.output)
        return None
    except Exception as e:
        logger.error(f"Could not read from db {str(db_path)!r}: {e}")
        return None


def get_unread_count() -> int | None:
    unread_count = _get_unread_newsraft()
    if unread_count:
        return unread_count

    # Fallback to reading from the database
    try:
        shutil.copy2(NEWS_DB, NEWS_DB_BACKUP)
        return _get_unread_db(NEWS_DB_BACKUP)
    except Exception as e:
        logger.error(
            f"Failed to backup db {str(NEWS_DB)!r} to {str(NEWS_DB_BACKUP)!r}: {e}"
        )
        return None


def handle_reload() -> bool:
    """Reload all items and notify user."""
    notification_title = "News Fetch"
    NotificationSystem.run(notification_title, "Fetching news. Please wait...")

    if not reload_newsraft():
        NotificationSystem.run(notification_title, "Unable to fetch news.")
        return False

    unread_count = get_unread_count()
    if unread_count:
        NotificationSystem.run(
            notification_title, f"Newsraft has {unread_count} items."
        )
    else:
        NotificationSystem.run(
            notification_title,
            "Fetch successful, but unknown item count.",
        )

    return True


ACTIONS = {
    MouseButton.LEFT: lambda: run_cmd_background([TERMINAL, "-e", "newsraft"]),
    MouseButton.MIDDLE: handle_reload,
    MouseButton.RIGHT: lambda: NotificationSystem.run(
        " News",
        "Shows unread news items.\n"
        "\n<b>Actions:</b>\n"
        "- Left   : Open 'newsraft'\n"
        "- Middle : Sync RSS feeds\n"
        "- Right  : Show this message\n"
        "- Extra  : Edit this script"
        "\n<b>Note:</b> Only one instance of 'newsraft' may be running at a time.",
    ),
    MouseButton.EXTRA_3: lambda: run_cmd_background([TERMINAL, "-e", EDITOR, __file__]),
}


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="sb_news",
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

    setup_logging(logger, logging.DEBUG if args.verbose else logging.ERROR)
    logger.debug(args)

    handle_block_button(ACTIONS)

    unread_count = get_unread_count()
    if not unread_count:
        print(" ❗err")
    else:
        print(f"{unread_count}")


if __name__ == "__main__":
    main()

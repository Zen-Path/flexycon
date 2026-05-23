import os
import shutil
import sqlite3
from contextlib import closing
from pathlib import Path

from common.cmd_utilities import run_cmd
from common.helpers import NotificationSystem
from common.logger import log

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


def get_item_count_db(db_path: Path, unread: bool = False) -> int | None:
    """Get unread items count directly from the database."""
    # .resolve() ensures the path is absolute, which file URIs prefer
    db_uri = f"file:{db_path.resolve()}?mode=ro"

    try:
        # sqlite3.connect context managers don't automatically close connections,
        # so contextlib.closing handles the clean-up.
        with closing(sqlite3.connect(db_uri, uri=True)) as conn:
            cursor = conn.cursor()

            query = "SELECT COUNT(*) FROM items"
            if unread:
                query += " WHERE unread = 1"

            cursor.execute(query)
            row = cursor.fetchone()

            # SELECT COUNT(*) always returns exactly one row, even if 0
            return int(row[0]) if row else 0

    except sqlite3.Error as e:
        log.error(f"SQLite database error reading from {str(db_path)!r}: {e}")
        return None
    except Exception as e:
        log.error(f"Unexpected error reading from db {str(db_path)!r}: {e}")
        return None


def get_unread_count() -> int | None:
    unread_count = _get_unread_newsraft()
    if unread_count:
        return unread_count

    # Fallback to reading from the database
    try:
        shutil.copy2(NEWS_DB, NEWS_DB_BACKUP)
        return get_item_count_db(db_path=NEWS_DB_BACKUP, unread=True)
    except Exception as e:
        log.error(
            f"Failed to backup db {str(NEWS_DB)!r} to {str(NEWS_DB_BACKUP)!r}: {e}"
        )
        return None


def refresh_feeds() -> bool:
    """Refresh all feeds and notify user."""

    notification_title = "RSS Refresh"
    NotificationSystem.run(notification_title, "Refreshing feeds...")

    if not reload_newsraft():
        NotificationSystem.run(notification_title, "Unable to refresh feeds.")
        return False

    total_count = get_item_count_db(db_path=NEWS_DB_BACKUP)
    if total_count:
        NotificationSystem.run(notification_title, f"Newsraft has {total_count} items.")
    else:
        NotificationSystem.run(
            notification_title,
            "Refresh successful, but unknown item count.",
        )

    return True

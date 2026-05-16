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


def _get_unread_db(db_path: Path) -> int | None:
    """Get unread items count directly from the database."""
    # .resolve() ensures the path is absolute, which file URIs prefer
    db_uri = f"file:{db_path.resolve()}?mode=ro"

    try:
        # sqlite3.connect context managers don't automatically close connections,
        # so contextlib.closing handles the clean-up.
        with closing(sqlite3.connect(db_uri, uri=True)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM items WHERE unread = 1")
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
        return _get_unread_db(NEWS_DB_BACKUP)
    except Exception as e:
        log.error(
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

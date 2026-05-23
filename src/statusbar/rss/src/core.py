import shutil
import sqlite3
from contextlib import closing
from pathlib import Path

from common.cmd_utilities import run_cmd
from common.helpers import NotificationSystem
from common.logger import log
from common.variables import XDG_DATA_HOME

NEWSRAFT_DATA_DIR = XDG_DATA_HOME / "newsraft"
NEWSRAFT_DB = NEWSRAFT_DATA_DIR / "newsraft.sqlite3"


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

    db_backup_path = db_path.parent / f"{db_path.name}.bak"
    try:
        shutil.copy2(db_path, db_backup_path)
    except Exception as e:
        log.error(
            f"Failed to backup db {str(db_path)!r} to {str(db_backup_path)!r}: {e}"
        )
        return None

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
    return get_item_count_db(db_path=NEWSRAFT_DB, unread=True)


def refresh_feeds() -> bool:
    """Refresh all feeds and notify user."""

    notification_title = "RSS Refresh"
    NotificationSystem.run(notification_title, "Refreshing feeds...")

    if not reload_newsraft():
        NotificationSystem.run(notification_title, "Unable to refresh feeds.")
        return False

    total_count = get_item_count_db(db_path=NEWSRAFT_DB)
    if total_count:
        NotificationSystem.run(notification_title, f"Newsraft has {total_count} items.")
    else:
        NotificationSystem.run(
            notification_title,
            "Refresh successful, but unknown item count.",
        )

    return True

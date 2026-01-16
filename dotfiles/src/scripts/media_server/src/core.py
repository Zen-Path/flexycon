import queue
import sqlite3
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from common.logger import logger


def init_db(db_path: Path):
    """
    Initializes the database schema.
    Raises sqlite3.Error or PermissionError if setup fails.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS downloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    title TEXT,
                    media_type TEXT,
                    start_time TEXT,
                    end_time TEXT
                )
            """
            )
            # Context manager auto-commits on success
            logger.debug(f"Schema initialized at {db_path}")

    except PermissionError:
        logger.critical(f"No permission to write to {db_path.parent}")
        raise  # Re-raise so the app knows it failed
    except sqlite3.Error as e:
        logger.critical(f"Database initialization failed: {e}")
        raise


def seed_db(db_path: Path, data_rows: List[Tuple]):
    """
    Injects data into the database.
    """
    if not data_rows:
        return

    # Ensure table exists first
    init_db(db_path)

    logger.info(f"Seeding database at: {db_path} with {len(data_rows)} rows")

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Using executemany instead of loop for optimization purposes
            cursor.executemany(
                "INSERT INTO downloads (url, title, media_type, start_time, end_time) VALUES (?, ?, ?, ?, ?)",
                data_rows,
            )

    except sqlite3.Error as e:
        logger.error(f"Failed to seed database: {e}")
        raise


class MessageAnnouncer:
    def __init__(self):
        self.listeners = []

    def listen(self):
        q = queue.Queue(maxsize=10)
        self.listeners.append(q)
        return q

    def announce(self, msg):
        # Iterate backwards to remove dead listeners safely
        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(msg)
            except queue.Full:
                del self.listeners[i]


@dataclass
class DownloadReportItem:
    url: str
    status: bool = True
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    log: str = ""
    output: str = ""

    def to_dict(self):
        return asdict(self)

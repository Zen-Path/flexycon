import json
import queue
import sqlite3
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from common.helpers import run_command
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


def expand_collection_urls(url: str, depth: int = 0) -> List[str]:
    """
    Determines if a URL is a collection based on Level Homogeneity. (best effort)
    """

    if depth > 3:
        return []

    try:
        cmd = ["gallery-dl", "-s", "-j", url]
        result = run_command(cmd)
        if not result.success:
            return []

        data = json.loads(result.output)

        # If there is only ONE unique level (e.g., all are level 6), it is probably
        # a collection of gallery links.
        # TODO: investigate gallery returns type to improve this logic
        levels = [entry[0] for entry in data if entry[0] > 1]
        unique_levels = set(levels)
        if len(unique_levels) != 1:
            return []

        child_urls = []
        for entry in data:
            # Entry structure: [level, content]
            if (
                len(entry) >= 2
                and isinstance(entry[1], str)
                and entry[1].startswith("http")
            ):
                c_url = entry[1]
                if c_url != url:  # Prevent self-reference loops
                    child_urls.append(c_url)
                    child_urls.extend(expand_collection_urls(c_url, depth + 1))

        return list(dict.fromkeys(child_urls))

    except Exception as e:
        logger.warning(f"Expansion error for {url}: {e}")
        return []

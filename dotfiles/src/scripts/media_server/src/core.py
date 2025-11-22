import queue
import sqlite3
import sys
from functools import wraps
from pathlib import Path

from common.logger import logger
from flask import abort, current_app, request


def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check Header OR Query String (for SSE)
        key = request.headers.get("X-API-Key") or request.args.get("api_key")

        if key != current_app.config.get("MEDIA_SERVER_KEY"):
            abort(401)
        return f(*args, **kwargs)

    return decorated_function


def init_db(db_name: Path):
    try:
        db_name.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(db_name) as conn:
            logger.debug(f"Successfully connected to {db_name} database")

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
            conn.commit()

    except PermissionError:
        logger.error(f"No permission to write to {db_name.parent}")
        sys.exit(1)
    except sqlite3.Error as e:
        logger.error(f"SQLite: {e}")
        sys.exit(1)


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

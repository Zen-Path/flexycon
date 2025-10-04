import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, List

from common.helpers import ensure_directories_exist
from common.logger import logger

DATA_HOME_DIR = (
    Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local/share")) / "flexycon"
)

DEFAULT_QUEUE_SIZE = 10  # flush after this many entries


@dataclass
class HistoryEntry:
    urls: List[str]
    entry_type: str
    finish_timestamp: datetime

    def to_dict(self) -> dict:
        return {
            "urls": self.urls,
            "type": self.entry_type,
            "finish_timestamp": self.finish_timestamp.isoformat(),
        }


class HistoryLogger:
    def __init__(self, history_path: Path | None = None):
        self.history_path = (
            Path(history_path) if history_path else DATA_HOME_DIR / "history.json"
        )

        self.lock = Lock()
        self.queue: List[dict[str, Any]] = []

        # Load previous history
        self.history: List[dict[str, Any]] = []
        if self.history_path.exists():
            try:
                with self.history_path.open("r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except json.JSONDecodeError:
                logger.error(
                    f"Could not decode history file: '{self.history_path}'. Starting fresh."
                )

    def queue_for_saving(self, entries: List[HistoryEntry]):
        """Queue HistoryEntry objects for saving."""
        entries_fmt = [entry.to_dict() for entry in entries]

        with self.lock:
            self.history.extend(entries_fmt)
            self.queue.extend(entries_fmt)

            if len(self.queue) >= DEFAULT_QUEUE_SIZE:
                self._save_to_file()
                self.queue.clear()

    def flush(self):
        """Flush remaining entries to file."""
        with self.lock:
            if self.queue:
                self._save_to_file()
                self.queue.clear()

    def _save_to_file(self):
        """Write the current history to the JSON file atomically."""
        ensure_directories_exist(self.history_path)

        temp_file = self.history_path.with_suffix(".tmp")

        try:
            with temp_file.open("w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=4)
            temp_file.replace(self.history_path)
        except Exception as e:
            logger.error(f"Failed to save history to {self.history_path}: {e}")

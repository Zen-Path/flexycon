import json
import os
import time
from pathlib import Path

XDG_DATA_HOME = Path(
    os.getenv("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
)
FLEXYCON_DATA_DIR = XDG_DATA_HOME / "flexycon"
HISTORY_FILE = FLEXYCON_DATA_DIR / "history.json"
LOCK_FILE = "history.lock"


def acquire_lock(max_tries=100, delay=0.5):
    tries = 0
    while os.path.exists(LOCK_FILE):
        if tries >= max_tries:
            raise TimeoutError("Could not acquire lock after multiple tries.")
        time.sleep(delay)
        tries += 1
    # Create lock file
    with open(LOCK_FILE, "w") as f:
        f.write("locked")


def release_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)


def log_history_entry(urls, status="done"):
    try:
        acquire_lock()
        # Read history
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = []
        else:
            history = []

        # Append new entry
        history.append({"urls": urls, "status": status})

        # Write updated history
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4)

    finally:
        release_lock()

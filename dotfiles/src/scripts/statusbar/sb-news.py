#!/usr/bin/env python3

import os
import subprocess

from scripts.statusbar.shared import EDITOR, TERMINAL, MouseButton

# Environment variables
NEWS_DIR = os.path.join(
    os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share")), "newsraft"
)
NEWS_DB = os.path.join(NEWS_DIR, "newsraft.sqlite3")
NEWS_DB_BACKUP = os.path.join(NEWS_DIR, "newsraft_backup.sqlite3")


def notify(title, message):
    """Send a desktop notification."""
    result = subprocess.run(["notify-send", title, message], check=False)
    return result.returncode == 0


def reload_newsraft():
    """Reload newsraft's contents."""
    result = subprocess.run(
        ["newsraft", "-e", "reload-all"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return result.returncode == 0


def get_unread_items_count():
    unread_count = get_unread_newsraft()

    # If newsraft fails, fallback to reading from the database
    if not unread_count:
        try:
            subprocess.run(["cp", "-f", NEWS_DB, NEWS_DB_BACKUP], check=False)
            unread_count = get_unread_db(NEWS_DB_BACKUP)
        except Exception:
            unread_count = None

    return unread_count


def get_unread_newsraft():
    """Get unread items count using newsraft."""
    try:
        result = subprocess.run(
            ["newsraft", "-e", "print-unread-items-count"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return result.stdout.strip()
    except Exception:
        return None


def get_unread_db(db_file):
    """Get unread items count directly from the database."""
    try:
        result = subprocess.run(
            [
                "sqlite3",
                f"file:{db_file}?mode=ro",
                "SELECT COUNT(*) FROM items WHERE unread = 1",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return result.stdout.strip()
    except Exception:
        return None


def handle_reload():
    """Reload all items and notify user."""
    notify("News Update", "Updating news, please wait...")
    if reload_newsraft():
        unread_count = get_unread_items_count()
        if unread_count:
            notify("News Update", f"Newsraft has {unread_count} items!")
        else:
            notify(
                "News Update",
                "Update succeeded, but unread count could not be retrieved.",
            )
    else:
        notify("News Update Failed", "Unable to update the news.")


def handle_block_button(button_id):
    """Handle block button events."""
    match button_id:
        case MouseButton.LEFT.value:
            subprocess.Popen([TERMINAL, "-e", "newsraft"])
        case MouseButton.MIDDLE.value:
            handle_reload()
        case MouseButton.RIGHT.value:
            notify(
                " News module",
                "Shows unread news items.\n"
                "\n<b>Actions:</b>\n"
                "- Left click opens newsraft\n"
                "- Middle click syncs RSS feeds\n"
                "\n<b>Note:</b> Only one instance of newsraft may be running at a time.",
            )
        case MouseButton.EXTRA_3.value:
            subprocess.Popen([TERMINAL, "-e", EDITOR, __file__])


def main():
    block_button = os.environ.get("BLOCK_BUTTON")
    if block_button:
        handle_block_button(int(block_button))

    unread_count = get_unread_items_count()
    if not unread_count:
        print(f" ❗err")
    else:
        print(f"{unread_count}")


if __name__ == "__main__":
    main()

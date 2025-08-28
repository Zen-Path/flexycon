#!/usr/bin/env python3

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

from common.logger import logger, setup_logging

UNICODE_DIR = (
    Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "unicode"
)
# List of files containing unicode characters
FILES = ["icons", "math", "alphanum", "flags", "braille"]


def user_prompt(options: list[str]) -> str:
    """Run dmenu with input text and return selection."""
    try:
        result = subprocess.run(
            ["dmenu", "-p", "Select char", "-l", "30"],
            input="\n".join(options).encode(),
            capture_output=True,
            check=True,
        )
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError:
        return ""


def main():
    parser = argparse.ArgumentParser(
        description="Prompt the user for a unicode character and copies or inserts it."
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug output.")
    args = parser.parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.ERROR)

    # Prompt user for a file or the concents of the emoji file
    emoji_file = UNICODE_DIR / "emoji"
    emoji_entries = []
    if emoji_file.exists():
        with open(emoji_file, "r", encoding="utf-8") as f:
            emoji_entries = [line.strip() for line in f if line.strip()]

    first_prompt = FILES + emoji_entries
    char = user_prompt(first_prompt)

    # If selected entry is a file, prompt again
    file_path = UNICODE_DIR / char
    if file_path.is_file():
        with open(file_path, "r", encoding="utf-8") as f:
            char = user_prompt(f.read())

    # Quit if empty selection
    if not char:
        return

    # Discard the name/description (take first token)
    char = char.split()[0]

    # Running the script with an argument automatically inserts the selected
    # character. Otherwise, the character is copied and a the user notified.
    if len(sys.argv) > 1:
        subprocess.run(["xdotool", "type", char])
    else:
        subprocess.run(["xclip", "-selection", "clipboard"], input=char.encode())
        subprocess.run(["notify-send", f"'{char}' was copied."])


if __name__ == "__main__":
    main()

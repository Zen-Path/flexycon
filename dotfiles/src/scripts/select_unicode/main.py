#!/usr/bin/env python3

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

from common.helpers import notify, run_command
from common.logger import logger, setup_logging
from scripts.select_unicode.data import CHARS


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


def format_char_entries(chars: dict[str, str]) -> list[str]:
    result = []
    for char in chars:
        result.append(f"{char} - {chars[char]}")
    return result


def build_parser():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Prompt the user for a unicode character and copies or inserts it."
    )

    parser.add_argument(
        "-i", "--insert-char", action="store_true", help="insert the selected char"
    )
    parser.add_argument(
        "--no-copy", action="store_true", help="do not copy the selected char"
    )
    parser.add_argument(
        "--no-notify",
        action="store_true",
        help="do not notify user of the selected char",
    )
    parser.add_argument("--verbose", action="store_true", help="enable debug output")

    return parser


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.ERROR)

    char_categories = list(CHARS.keys())
    logger.debug(f"char_categories: {char_categories}")

    # Prompt user for a category or common emojis
    selection = user_prompt(char_categories + format_char_entries(CHARS["emoji"]))
    if selection in char_categories:
        selection = user_prompt(format_char_entries(CHARS[selection]))

    selection_parts = selection.split(" - ", maxsplit=1)
    logger.info(f"Selection parts: {selection_parts}")

    # skip empty or malformed lines
    if len(selection_parts) < 2:
        return

    char, name = selection_parts
    logger.info(f"char: '{char}', name: '{name}'")

    if args.insert_char:
        run_command(["xdotool", "type", char])

    if not args.no_copy:
        subprocess.run(["xclip", "-selection", "clipboard"], input=char.encode())
        logger.info(f"Character copied.")

        if not args.no_notify:
            notify("Character copied", f"'{char}' was copied.")


if __name__ == "__main__":
    main()

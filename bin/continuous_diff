#!/usr/bin/env python3

import difflib
import sys
from pathlib import Path


def read_file(path):
    """Read the contents of the file as a list of lines."""
    with open(path, "r") as file:
        return file.readlines()


def display_diff(old, new):
    """Display the diff between the old and new file contents."""
    diff = difflib.unified_diff(
        old, new, fromfile="Previous", tofile="Current", lineterm=""
    )
    print("\n".join(diff) or "No changes detected.")


def monitor_file(path):
    """Monitor the file for changes and display diffs."""
    path = Path(path)

    if not path.is_file():
        print(f"Error: {path} is not a valid file.")
        sys.exit(1)

    print(f"Monitoring file: {path}")
    old_content = read_file(path)

    while True:
        input("Press Enter to check for changes (Ctrl+C to exit)...")
        try:
            new_content = read_file(path)
            display_diff(old_content, new_content)
            old_content = new_content
        except FileNotFoundError:
            print("File not found!")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python file_diff_tool.py <path_to_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    try:
        monitor_file(file_path)
    except KeyboardInterrupt:
        print("\nExiting...")

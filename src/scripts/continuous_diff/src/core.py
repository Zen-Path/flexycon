import difflib
from pathlib import Path

from common.logger import logger


def read_file_lines(path: Path) -> list[str]:
    """Read the contents of the file as a list of lines."""
    with open(path, "r") as file:
        return file.readlines()


def display_diff(old: list[str], new: list[str]) -> None:
    """Display the diff between the old and new file contents."""
    diff = difflib.unified_diff(
        old, new, fromfile="Previous", tofile="Current", lineterm=""
    )
    print("\n".join(diff) or "No changes detected.")


def monitor_file(path: Path) -> None:
    """Monitor the file for changes and display diffs."""
    if not path.is_file():
        logger.error(f"Path {str(path)!r} is not a valid file.")
        return

    logger.info(f"Monitoring file {str(path)!r}")
    old_content = read_file_lines(path)

    while True:
        input("Press Enter to check for changes (Ctrl+C to exit)...")
        try:
            new_content = read_file_lines(path)
            display_diff(old_content, new_content)
            old_content = new_content
        except FileNotFoundError:
            logger.error("File not found!")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

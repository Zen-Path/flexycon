#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import difflib
import logging
import sys
from pathlib import Path

from common.helpers import get_version
from common.logger import logger, setup_logging


def read_file(path: Path) -> list[str]:
    """Read the contents of the file as a list of lines."""
    with open(path, "r") as file:
        return file.readlines()


def display_diff(old: list[str], new: list[str]):
    """Display the diff between the old and new file contents."""
    diff = difflib.unified_diff(
        old, new, fromfile="Previous", tofile="Current", lineterm=""
    )
    print("\n".join(diff) or "No changes detected.")


def monitor_file(path: Path):
    """Monitor the file for changes and display diffs."""
    if not path.is_file():
        logger.error(f"Path {str(path)!r} is not a valid file.")
        return

    logger.info(f"Monitoring file {str(path)!r}")
    old_content = read_file(path)

    while True:
        input("Press Enter to check for changes (Ctrl+C to exit)...")
        try:
            new_content = read_file(path)
            display_diff(old_content, new_content)
            old_content = new_content
        except FileNotFoundError:
            logger.error("File not found!")
        except Exception as e:
            logger.error(f"An error occurred: {e}")


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="continuous_diff",
        description="Showcase diff of the same file as it's being changed.",
    )

    parser.add_argument(
        "-p", "--target-path", required=True, type=Path, help="the jsonc file"
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    return parser


def main() -> None:
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.ERROR)
    logger.debug(args)

    if args.target_path is None:
        logger.error("Missing target path.")
        sys.exit(1)

    try:
        monitor_file(Path(args.target_path))
    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    main()

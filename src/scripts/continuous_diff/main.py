#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
from pathlib import Path

from common.helpers import get_version
from common.logger import log, setup_logging
from scripts.continuous_diff.src.core import monitor_file


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="continuous_diff",
        description="Showcase diff of the same file as it's being changed.",
    )

    parser.add_argument(
        "target_path", type=Path, help="the file that will be monitored"
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

    setup_logging(log, logging.DEBUG if args.verbose else logging.ERROR)
    log.debug(args)

    try:
        monitor_file(Path(args.target_path))
    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    main()

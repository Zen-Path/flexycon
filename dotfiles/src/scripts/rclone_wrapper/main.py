#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import json
import logging
import sys
import tempfile

from common.helpers import get_version, run_command
from common.logger import logger, setup_logging
from scripts.rclone_wrapper.src.config import load_config
from scripts.rclone_wrapper.src.formatting import (
    format_operations,
    format_stats,
    print_table,
)
from scripts.rclone_wrapper.src.rclone import build_rclone_command, parse_rclone_output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rclone_wrapper",
        description="Wrapper around rclone with persistent config.",
    )

    parser.add_argument("source", help="source path")
    parser.add_argument("destination", help="destination path")

    parser.add_argument(
        "-a",
        "--action",
        choices=["copy", "sync", "c", "s"],
        required=True,
        help="action to perform",
    )

    parser.add_argument(
        "-n",
        "--no-dry-run",
        dest="dry_run",
        action="store_false",
        default=True,
        help="actually perform the changes (default is dry-run)",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    return parser


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.WARNING)

    logger.debug(args)

    try:
        config = load_config()
        logger.debug(json.dumps(config, indent=2))
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    command = build_rclone_command(args, config)
    if not args.dry_run:
        run_command(command)
        return

    result = run_command(command)

    operations_data, stats = parse_rclone_output(result.output)
    formatted_operations = format_operations(operations_data)

    print_table(formatted_operations, headers=["Type", "Filepath", "Size Fmt", "Size"])

    formatted_stats = format_stats(stats)
    print_table(
        [[k, v] for k, v in formatted_stats.items()], headers=["Field", "Value"]
    )

    # Create a temporary log file that holds the table data
    # Useful in cases when the some useful data is truncated
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp:
        log_data = {"operations": operations_data, "stats": stats}
        tmp.write(json.dumps(log_data))

        logger.debug(f"Temporary log file created at: {tmp.name}")


if __name__ == "__main__":
    main()

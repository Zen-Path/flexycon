#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import json
import logging
import sys
import tempfile

from common.cmd_utilities import run_cmd
from common.helpers import get_version
from common.logger import logger, setup_logging
from scripts.rclone_wrapper.src.config import load_config
from scripts.rclone_wrapper.src.formatting import (
    format_stats,
    prepare_table_rows,
    print_table,
    transform_operations,
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
        logger.debug(f"Config:\n{json.dumps(config.model_dump(), indent=2)}")
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    command = build_rclone_command(args, config)
    result = run_cmd(command)

    if not args.dry_run:
        sys.exit(result.return_code)

    raw_ops, stats = parse_rclone_output(result.output)
    processed_ops = transform_operations(raw_ops)
    formatted_rows = prepare_table_rows(processed_ops)

    if len(formatted_rows) > 0:
        print_table(
            formatted_rows, headers=["Update Type", "Filepath", "Size Fmt", "Size"]
        )

    if stats is not None:
        stats_rows = format_stats(stats)
        print_table(stats_rows, headers=["Field", "Value"])

    # Create a temporary log file that holds the table data
    # Useful in cases when the some useful data is truncated
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp:
        log_data = {
            "operations": [op.model_dump() for op in processed_ops],
            "stats": stats.model_dump() if stats else None,
        }
        tmp.write(json.dumps(log_data, indent=2))

        print(f"Log file created at {tmp.name!r}")

    sys.exit(result.return_code)


if __name__ == "__main__":
    main()

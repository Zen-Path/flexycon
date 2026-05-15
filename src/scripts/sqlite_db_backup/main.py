#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging

from common.helpers import get_version
from common.logger import logger, setup_logging
from scripts.sqlite_db_backup.src.core import (
    generate_diff,
    generate_test_data,
    restore_database,
)


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="sqlite_db_backup",
        description="SQLite diff and restore utility",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    diff_parser = subparsers.add_parser(
        "diff", help="generate diff between two databases"
    )
    diff_parser.add_argument("old_db", help="path to the old database")
    diff_parser.add_argument("new_db", help="path to the new database")
    diff_parser.add_argument("output_dir", help="directory to save the diff")

    restore_parser = subparsers.add_parser(
        "restore", help="restore database from base schema and diffs"
    )
    restore_parser.add_argument("base_schema", help="path to the base schema SQL file")
    restore_parser.add_argument("diffs_dir", help="directory containing diff SQL files")
    restore_parser.add_argument("output_db", help="output database path")

    test_parser = subparsers.add_parser(
        "generate-test-data", help="generate test data and diffs"
    )
    test_parser.add_argument(
        "output_dir", help="directory to save the test databases and diffs"
    )
    test_parser.add_argument("base_db", help="path to the base database")
    test_parser.add_argument(
        "--num-backups", type=int, default=10, help="number of backups to generate"
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

    if args.command == "diff":
        generate_diff(args.old_db, args.new_db, args.output_dir)
    elif args.command == "restore":
        restore_database(args.base_schema, args.diffs_dir, args.output_db)
    elif args.command == "generate-test-data":
        generate_test_data(args.output_dir, args.base_db, args.num_backups)


if __name__ == "__main__":
    main()

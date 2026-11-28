#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
from pathlib import Path

from common.helpers import get_version
from common.logger import log, setup_logging
from scripts.documents_syncer.src.core import (
    cmd_add,
    cmd_remove,
    cmd_sync,
    load_store,
)


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="documents_syncer",
        description="Tracks and converts binary documents (PDF, Word, Excel) into text formats for Git versioning.",
    )

    parser.add_argument(
        "-s",
        "--store-path",
        type=Path,
        help="path to the JSON store file tracking documents (default: documents_store.json)",
    )
    parser.add_argument(
        "--pre-commit-hook",
        action="store_true",
        default=False,
        help="act as a pre-commit hook (exits with code 1 if files were updated)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    subparsers = parser.add_subparsers(dest="command")

    # sync (also the default when no subcommand is passed)
    subparsers.add_parser(
        "sync",
        help="convert any tracked documents whose source or generated output changed",
    )

    # add
    add_parser = subparsers.add_parser(
        "add",
        help="add one or more documents to the tracking store and convert them",
    )
    add_parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="file paths to start tracking",
    )

    # remove
    remove_parser = subparsers.add_parser(
        "remove",
        help="stop tracking one or more documents",
    )
    remove_parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="file paths to stop tracking",
    )
    remove_parser.add_argument(
        "--delete-generated",
        action="store_true",
        default=False,
        help="also delete the generated text/html/csv file from disk",
    )

    return parser


def main() -> None:
    args = build_parser().parse_args()

    setup_logging(log, logging.DEBUG if args.verbose else logging.INFO)
    log.debug(args)

    store = load_store(args.store_path)

    match args.command:
        case "add":
            cmd_add(args.paths, store, args.store_path)
        case "remove":
            cmd_remove(args.paths, store, args.store_path, args.delete_generated)
        case "sync" | None:
            cmd_sync(store, args.store_path, args.pre_commit_hook)
        case _:
            log.error(f"Unknown subcommand: {args.command!r}")


if __name__ == "__main__":
    main()

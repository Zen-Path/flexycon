#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import sys
from pathlib import Path

from common.helpers import get_version
from common.logger import log, setup_logging
from scripts.documents_syncer.src.core import (
    collect_target_files,
    get_destination_path,
    get_file_hash,
    load_store,
    run_conversion,
    save_store,
)


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="documents_syncer",
        description="Helps with git versioning PDF, Word, Excel and other documents.",
    )

    parser.add_argument(
        "-s",
        "--store-path",
        type=Path,
        help="where to put the store file containing microsoft documents data",
    )
    parser.add_argument(
        "--pre-commit-hook",
        action="store_true",
        default=False,
        help="act as a pre-commit hook",
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

    setup_logging(log, logging.DEBUG if args.verbose else logging.INFO)
    log.debug(args)

    store = load_store(args.store_path)

    any_changes_made = False
    conversion_count = 0

    # Clean up the store; remove paths that no longer exist
    missing_paths = [path for path in store if not Path(path).exists()]
    for path in missing_paths:
        log.info(f"Removing missing file from store: {str(path)!r}")
        del store[path]
        any_changes_made = True

    target_files = collect_target_files()

    for source_file in target_files:
        # Build destination automatically. Skip if it's an unmapped extension.
        destination_file = get_destination_path(source_file)
        if not destination_file:
            continue

        str_source_path = str(source_file)
        str_dest_path = str(destination_file)

        current_source_hash = get_file_hash(source_file)
        current_dest_hash = get_file_hash(destination_file)

        needs_conversion = False

        # Determine if we need to convert
        if not destination_file.exists():
            needs_conversion = True
        else:
            store_entry = store.get(str_source_path)

            if not store_entry:
                needs_conversion = True
            elif store_entry.get("source_hash") != current_source_hash:
                needs_conversion = True
            elif store_entry.get("destination_hash") != current_dest_hash:
                needs_conversion = True

        # Run conversion and update store if needed
        if needs_conversion:
            success = run_conversion(source_file, destination_file)
            conversion_count += 1

            if success:
                # Update store with fresh hashes
                store[str_source_path] = {
                    "source_path": str_source_path,
                    "source_hash": current_source_hash,
                    "destination_path": str_dest_path,
                    "destination_hash": get_file_hash(destination_file),
                }
                any_changes_made = True

    if not any_changes_made:
        return

    save_store(store, args.store_path)

    if conversion_count > 0:
        log.info("All documents successfully converted.")

    if args.pre_commit_hook:
        sys.exit(1)


if __name__ == "__main__":
    main()

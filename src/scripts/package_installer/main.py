#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging

from common.helpers import get_version
from common.logger import log, setup_logging
from scripts.package_installer.data.packages import packages
from scripts.package_installer.src.core import process_packages


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="package_installer",
        description="Install system packages.",
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="preview packages to be installed"
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

    process_packages(packages, args.dry_run)


if __name__ == "__main__":
    main()

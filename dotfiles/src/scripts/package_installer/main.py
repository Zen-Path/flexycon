#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging

from common.helpers import get_version
from common.logger import logger, setup_logging
from common.packages.models import Package
from scripts.package_installer.data.packages import packages


def build_parser():
    parser = argparse.ArgumentParser(
        description="Generate bookmarks for various tools."
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


def process_packages(packages: list[Package], dry_run: bool = False):
    managers_cache: dict[str, bool] = {}

    for package in packages:
        if not package.condition:
            logger.warning(f"Skipping {package.name!r}: unmet condition.")
            continue

        # Find the first available manager
        available_manager = None
        for manager_cls in package.managers:
            manager_name = manager_cls.__name__

            # Cache manager availability checks
            if manager_name not in managers_cache:
                managers_cache[manager_name] = manager_cls.check_availability()

            if managers_cache[manager_name]:
                available_manager = manager_cls
                break

        if not available_manager:
            logger.warning(f"Skipping {package.name!r}: no available manager found.")
            continue

        logger.info(f"Installing {package.name!r} using {available_manager.__name__}.")
        if not dry_run:
            available_manager.install(package)


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.INFO)

    process_packages(packages, args.dry_run)


if __name__ == "__main__":
    main()

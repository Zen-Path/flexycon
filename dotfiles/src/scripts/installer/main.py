import argparse
import logging
from typing import List

from common.logger import logger, setup_logging
from common.packages.models import Package
from scripts.installer.data.packages import packages


def build_parser():
    parser = argparse.ArgumentParser(
        description="Generate bookmarks for various tools."
    )

    parser.add_argument("--verbose", action="store_true", help="enable debug output")

    return parser


def process_packages(packages: List[Package]):
    managers_cache: dict[str, bool] = {}

    for package in packages:
        if not package.condition:
            logger.warning(f"Skipping '{package.name}': unmet condition.")
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
            logger.warning(f"Skipping '{package.name}': no available manager found.")
            continue

        logger.info(f"Installing '{package.name}' using {available_manager.__name__}.")
        available_manager.install(package)


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.INFO)

    process_packages(packages)


if __name__ == "__main__":
    main()

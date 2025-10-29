import argparse
import logging
import platform

from common.logger import logger, setup_logging
from scripts.installer.data.packages import packages


def build_parser():
    parser = argparse.ArgumentParser(
        description="Generate bookmarks for various tools."
    )

    parser.add_argument("--verbose", action="store_true", help="enable debug output")

    return parser


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.INFO)

    for package in packages:
        if not platform.system() == package.managers[0].PLATFORM:
            logger.warning(
                f"Skipped package '{package.name}' due to unsupported platform."
            )
            continue

        if not package.condition:
            logger.warning(f"Skipped package '{package.name}' due to unmet condition.")
            continue

        logger.info(
            f"Installing package '{package.name}' with manager {package.managers[0].__name__}."
        )
        package.managers[0].install(package)


if __name__ == "__main__":
    main()

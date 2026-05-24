#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
from collections import defaultdict

from common.helpers import get_version
from common.logger import log, setup_logging
from common.packages.models import Package, PackageManager
from scripts.package_installer.data.packages import packages


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


def process_packages(packages: list[Package], dry_run: bool = False):
    managers_cache: dict[str, bool] = {}
    batch_queue: dict[type[PackageManager], list[Package]] = defaultdict(list)

    for package in packages:
        if not package.condition:
            log.warning(f"Skipping {package.name!r}: unmet condition.")
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
            log.warning(f"Skipping {package.name!r}: no available manager found.")
            continue

        batch_queue[available_manager].append(package)

    for manager_cls, pkgs in batch_queue.items():
        log.info(f"[{manager_cls.__name__}] Installing {len(pkgs)} packages...")

        if not dry_run:
            manager_cls.install(pkgs)


def main() -> None:
    args = build_parser().parse_args()

    setup_logging(log, logging.DEBUG if args.verbose else logging.INFO)
    log.debug(args)

    process_packages(packages, args.dry_run)


if __name__ == "__main__":
    main()

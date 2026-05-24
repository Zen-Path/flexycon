from collections import defaultdict

from common.logger import log
from common.packages.models import Package, PackageManager


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

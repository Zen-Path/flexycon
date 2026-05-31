import re
import shutil
import sys
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from git import Repo

from common.cmd_utilities import run_cmd
from common.logger import log


class PackageManager(ABC):
    COMMAND: str
    # When platform is None, it means it's available on all platforms
    PLATFORM: str | None

    @classmethod
    def check_availability(cls) -> bool:
        """Check if the package manager is available on the system."""
        is_platform_same = cls.PLATFORM is None or sys.platform == cls.PLATFORM
        return is_platform_same and shutil.which(cls.COMMAND) is not None

    @classmethod
    @abstractmethod
    def install(cls, packages: list[Package]) -> None:
        """Install packages using manager."""
        pass

    @classmethod
    @abstractmethod
    def uninstall(cls, package: Package) -> None:
        """Uninstall package using manager."""
        pass

    @classmethod
    @abstractmethod
    def update_all(cls) -> None:
        """Update all packages."""
        pass


@dataclass
class Package:
    """Represents a software package with metadata."""

    identifier: str
    managers: list[type[PackageManager]]
    name: str | None = None
    description: str | None = None
    is_gui: bool | None = False
    destination: Path | None = None  # Can be None since only Git is using it
    condition: bool = True

    def __post_init__(self):
        if self.name is None:
            self.name = self.identifier


class Brew(PackageManager):
    PLATFORM = "darwin"
    COMMAND = "brew"

    update_outdated_pattern = re.compile(
        r"([^ ]+) .* is already installed but outdated"
    )
    update_action_pattern = re.compile(r"^==> Upgrading ([^ ]+)$")
    install_success_pattern = re.compile(
        r"^🍺\s+/opt/homebrew/(?:Cellar|Caskroom)/([^/]+)"
    )

    @classmethod
    def process_output(cls, output: str):
        for line in output.splitlines():
            if not line:
                continue

            # Updates
            match = cls.update_outdated_pattern.match(
                line
            ) or cls.update_action_pattern.match(line)
            if match:
                log.info(f"- {match.group(1)} was updated.")
                continue

            # Installs
            match = cls.install_success_pattern.match(line)
            if match:
                log.info(f"- {match.group(1)} was installed.")
                continue

    @classmethod
    def install(cls, packages: list[Package]) -> None:
        if not packages:
            return

        formulas: list[str] = []
        casks: list[str] = []
        for package in packages:
            if package.is_gui:
                casks.append(package.identifier)
            else:
                formulas.append(package.identifier)

        # Batch all regular formulas together
        if formulas:
            cmd = [cls.COMMAND, "install"] + formulas
            result = run_cmd(cmd)
            cls.process_output(result.output)

        # Batch all GUI casks together
        if casks:
            cmd = [cls.COMMAND, "install", "--cask"] + casks
            result = run_cmd(cmd)
            cls.process_output(result.output)

    @classmethod
    def uninstall(cls, package: Package) -> None:
        run_cmd([cls.COMMAND, "uninstall", package.identifier])

    @classmethod
    def update_all(cls) -> None:
        run_cmd([cls.COMMAND, "update"])  # Syncs formulae
        run_cmd([cls.COMMAND, "upgrade"])  # Upgrades packages


class Yay(PackageManager):
    PLATFORM = "linux"
    COMMAND = "yay"

    @classmethod
    def install(cls, packages: list[Package]) -> None:
        identifiers = [package.identifier for package in packages]
        run_cmd([cls.COMMAND, "--sync", "--needed", "--noconfirm", *identifiers])

    @classmethod
    def uninstall(cls, package: Package) -> None:
        run_cmd(
            [
                cls.COMMAND,
                "--remove",
                "--cascade",
                "--recursive",
                "--nosave",
                package.identifier,
            ]
        )

    @classmethod
    def update_all(cls) -> None:
        run_cmd([cls.COMMAND, "--sync", "--refresh", "--sysupgrade"])


class Chocolatey(PackageManager):
    PLATFORM = "win32"
    COMMAND = "choco"

    @classmethod
    def install(cls, packages: list[Package]) -> None:
        # TODO: investigate if choco has bulk install
        for package in packages:
            run_cmd([cls.COMMAND, "upgrade", package.identifier])

    @classmethod
    def uninstall(cls, package: Package) -> None:
        run_cmd([cls.COMMAND, "uninstall", package.identifier])

    @classmethod
    def update_all(cls) -> None:
        run_cmd([cls.COMMAND, "upgrade", "all", "--confirm"])


class Git(PackageManager):
    PLATFORM = None
    COMMAND = "git"

    @classmethod
    def install(cls, packages: list[Package]) -> None:
        for package in packages:
            if not package.destination:
                log.error(f"Package {package.identifier!r} requires a 'destination'.")
                continue

            try:
                if (package.destination / ".git").exists():
                    # Update logic
                    repo = Repo(package.destination)
                    origin = repo.remotes.origin

                    commit_before = repo.head.commit.hexsha
                    origin.pull()
                    commit_after = repo.head.commit.hexsha

                    # Check if changes were actually pulled
                    if commit_before != commit_after:
                        log.info(
                            f"- {package.name!r} was updated from "
                            f"{commit_before[:7]} to {commit_after[:7]}"
                        )
                else:
                    # Fresh clone logic
                    Repo.clone_from(
                        package.identifier, package.destination, recurse_submodules=True
                    )
                    log.info(f"- {package.name!r} was installed.")

            except Exception as e:
                log.error(f"Unable to install {package.name!r}: {e}")

    @classmethod
    def uninstall(cls, package: Package) -> None:
        if package.destination and package.destination.exists():
            shutil.rmtree(package.destination)

    @classmethod
    def update_all(cls) -> None:
        pass


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

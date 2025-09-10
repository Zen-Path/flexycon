import logging
import platform
import shutil
import subprocess
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Type

from common.logger import logger, setup_logging


def run_command(command: List[str]) -> int:
    """Execute a shell command with error handling."""
    try:
        subprocess.run(command, check=True)
        logger.info("Command executed successfully: %s", " ".join(command))
    except subprocess.CalledProcessError as e:
        logger.error("Command failed: %s | Error: %s", " ".join(command), e)
    except Exception as e:
        logger.exception(
            "Unexpected error while running command: %s", " ".join(command)
        )
    return 0


class PackageInstaller(ABC):
    """Abstract base class for package installers."""

    def __init__(self, name: str):
        self.name = name  # e.g., "brew", "apt", "pacman"

    @abstractmethod
    def install(self, package_identifier: str) -> None:
        """Install a package by its identifier."""
        pass

    @abstractmethod
    def uninstall(self, package_identifier: str) -> None:
        """Uninstall a package by its identifier."""
        pass

    def __repr__(self) -> str:
        return f"PackageInstaller(name='{self.name}')"


class BrewInstaller(PackageInstaller):
    def __init__(self):
        super().__init__("brew")

    def install(self, package_identifier: str) -> None:
        logger.info("Installing '%s' with brew...", package_identifier)
        run_command(["brew", "install", package_identifier])

    def uninstall(self, package_identifier: str) -> None:
        logger.info("Uninstalling '%s' with brew...", package_identifier)
        run_command(["brew", "uninstall", package_identifier])


class AptInstaller(PackageInstaller):
    def __init__(self):
        super().__init__("apt")

    def install(self, package_identifier: str) -> None:
        logger.info("Installing '%s' with apt...", package_identifier)
        run_command(["sudo", "apt", "install", "-y", package_identifier])

    def uninstall(self, package_identifier: str) -> None:
        logger.info("Uninstalling '%s' with apt...", package_identifier)
        run_command(["sudo", "apt", "remove", "-y", package_identifier])


class PacmanInstaller(PackageInstaller):
    def __init__(self):
        super().__init__("pacman")

    def install(self, package_identifier: str) -> None:
        logger.info("Installing '%s' with pacman...", package_identifier)
        run_command(["sudo", "pacman", "-S", "--noconfirm", package_identifier])

    def uninstall(self, package_identifier: str) -> None:
        logger.info("Uninstalling '%s' with pacman...", package_identifier)
        run_command(["sudo", "pacman", "-R", "--noconfirm", package_identifier])


def detect_installer() -> Optional[PackageInstaller]:
    """Detect the package manager based on the user's system."""
    system = platform.system()
    logger.info("Detecting package manager for system: %s", system)

    if system == "Darwin" and shutil.which("brew"):
        return BrewInstaller()
    elif system == "Linux":
        if shutil.which("apt"):
            return AptInstaller()
        elif shutil.which("pacman"):
            return PacmanInstaller()

    logger.warning("No supported package manager detected.")
    return None


class Package:
    """Represents a software package with metadata and installation details."""

    def __init__(
        self,
        name: str,
        identifier_map: Dict[str, List[str]],
        installer: PackageInstaller,
        purpose: str = "",
        tags: Optional[List[str]] = None,
    ):
        """
        Parameters:
            name (str): Human-readable name of the package.
            identifier_map (dict): Mapping of identifiers to the list of package managers that use them.
            installer (PackageInstaller): Installer instance.
            purpose (str, optional): Description of the package's purpose.
            tags (List[str], optional): Tags for categorizing the package.
        """
        self.name = name
        self.identifier_map = identifier_map
        self.installer = installer
        self.purpose = purpose
        self.tags = tags or []

    def get_identifier(self) -> str:
        """Select the correct identifier based on the installer's name."""
        for identifier, managers in self.identifier_map.items():
            if not managers or self.installer.name in managers:
                return identifier
        raise ValueError(
            f"No valid identifier found for installer '{self.installer.name}'."
        )

    def install(self) -> None:
        identifier = self.get_identifier()
        logger.info(
            "Starting installation for '%s' with identifier '%s'...",
            self.name,
            identifier,
        )
        self.installer.install(identifier)

    def uninstall(self) -> None:
        identifier = self.get_identifier()
        logger.info(
            "Starting uninstallation for '%s' with identifier '%s'...",
            self.name,
            identifier,
        )
        self.installer.uninstall(identifier)

    def __repr__(self) -> str:
        return (
            f"Package(name='{self.name}', identifier_map={self.identifier_map}, "
            f"purpose='{self.purpose}', tags={self.tags})"
        )


# Example usage
if __name__ == "__main__":
    setup_logging(logger, logging.INFO)

    installer = detect_installer()

    print(installer)

    if installer:
        packages = [
            Package(
                name="Python",
                identifier_map={
                    "python3": ["brew"],
                    "python3.14": ["apt", "chocolaty"],
                    "python": [],  # Default for other installers
                },
                installer=installer,
                purpose="Python programming language",
                tags=["language", "development"],
            ),
            Package(
                name="fzf",
                identifier_map={"fzf": []},  # Same identifier for all installers
                installer=installer,
                purpose="Fuzzy finder for terminal searching",
                tags=["terminal", "productivity"],
            ),
        ]

        # Install all packages
        # for package in packages:
        # package.install()
    else:
        logger.error(
            "No suitable installer found. Cannot proceed with package installation."
        )

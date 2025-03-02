from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from utils import run_command


class PackageManager(ABC):
    """Abstract base class for package managers."""

    @staticmethod
    @abstractmethod
    def install(package: Package) -> None:
        """Install a package by its identifier."""
        pass

    @staticmethod
    @abstractmethod
    def uninstall(package: Package) -> None:
        """Uninstall a package by its identifier."""
        pass


class PacMan(PackageManager):
    """PacMan package manager implementation."""

    @staticmethod
    def install(package: Package) -> None:
        run_command(["sudo", "pacman", "--sync", package.id])

    @staticmethod
    def uninstall(package: Package) -> None:
        run_command(
            [
                "sudo",
                "pacman",
                "--remove",
                "--cascade",
                "--recursive",
                "--nosave",
                package.id,
            ]
        )


class Package:
    """Represents a software package with metadata and installation details."""

    def __init__(
        self,
        id_map: Dict[str, List[str]],
        description: str = "",
        name: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ):
        """
        Parameters:
            id_map: Mapping of identifiers to the list of package managers that use them.
            description: Description of the package.
            name: Human-readable name of the package. Same as 'id' if not provided.
            tags: Tags for categorizing the package.
        """



        self.name = name
        self.id_map = id_map
        self.description = description
        self.tags = tags or []

    def get_identifier(self) -> str:
        """Select the correct identifier based on the installer's name."""
        for identifier, managers in self.id_map.items():
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
            f"Package(name='{self.name}', identifier_map={self.id_map}, "
            f"purpose='{self.description}', tags={self.tags})"
        )


# if __name__ == "__main__":
#     PacMan.install("fzf")
#     PacMan.uninstall("fzf")

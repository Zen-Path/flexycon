from abc import ABC, abstractmethod, abstractproperty
from typing import Dict, List, Optional, Type

from utils import run_command


class PackageManager(ABC):
    """Abstract base class for package managers."""

    @classmethod
    @abstractmethod
    def install(cls, package_ids: List[str]) -> None:
        """Install a package by its identifier."""
        pass

    @classmethod
    @abstractmethod
    def uninstall(cls, package_ids: List[str]) -> None:
        """Uninstall a package by its identifier."""
        pass


class PacMan(PackageManager):
    """PacMan package manager implementation."""

    @classmethod
    def install(cls, package_ids: List[str]) -> None:
        run_command(["sudo", "pacman", "--sync", "--noconfirm", *package_ids])

    @classmethod
    def uninstall(cls, package_ids: List[str]) -> None:
        run_command(
            [
                "sudo",
                "pacman",
                "--remove",
                "--cascade",
                "--recursive",
                "--nosave",
                *package_ids,
            ]
        )


class Yay(PackageManager):
    """Yay package manager implementation."""

    @classmethod
    def install(cls, package_ids: List[str]) -> None:
        run_command(["yay", "--sync", "--noconfirm", *package_ids])

    @classmethod
    def uninstall(cls, package_ids: List[str]) -> None:
        run_command(
            [
                "yay",
                "--remove",
                "--cascade",
                "--recursive",
                "--nosave",
                *package_ids,
            ]
        )


class Package:
    """Represents a software package with metadata"""

    def __init__(
        self,
        id: str,
        manager: Type[PackageManager],
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ):
        """
        Parameters:
            id: The package identifier used by the manager
            manager: A package manager
            name: Human-readable name of the package. Same as 'id' if not provided.
            description: Description of the package.
            tags: Tags for categorizing the package.
        """

        self.id = id
        self.manager = manager
        self.name = name or id
        self.description = description
        self.tags = tags

    def __repr__(self) -> str:
        return (
            f"Package(id={self.id}, name='{self.name}', "
            f"description='{self.description}', tags={self.tags})"
        )

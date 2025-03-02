from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Type

from utils import run_command


class PackageManager(ABC):
    """Abstract base class for package managers."""

    @staticmethod
    @abstractmethod
    def install(package_id: str) -> None:
        """Install a package by its identifier."""
        pass

    @staticmethod
    @abstractmethod
    def uninstall(package_id: str) -> None:
        """Uninstall a package by its identifier."""
        pass

    @staticmethod
    @abstractmethod
    def is_available() -> bool:
        """Return True if the package manager is available on the system."""
        pass

    @classmethod
    def all_subclasses(cls) -> List[Type]:
        """Recursively collect all subclasses of PackageManager."""
        subclasses = set()
        work = [cls]
        while work:
            parent = work.pop()
            for child in parent.__subclasses__():
                if child not in subclasses:
                    subclasses.add(child)
                    work.append(child)
        return list(subclasses)

    @classmethod
    def available_managers(cls) -> List[Type]:
        """Return a list of available package manager classes (those for which is_available() returns True)."""
        return [pm for pm in cls.all_subclasses() if pm.is_available()]


class PacMan(PackageManager):
    """PacMan package manager implementation."""

    @staticmethod
    def install(package_id: str) -> None:
        run_command(["sudo", "pacman", "--sync", package_id])

    @staticmethod
    def uninstall(package_id: str) -> None:
        run_command(
            [
                "sudo",
                "pacman",
                "--remove",
                "--cascade",
                "--recursive",
                "--nosave",
                package_id,
            ]
        )


class Yay(PackageManager):
    """Yay package manager implementation."""

    @staticmethod
    def install(package_id: str) -> None:
        run_command(["sudo", "yay", "--sync", package_id])

    @staticmethod
    def uninstall(package_id: str) -> None:
        run_command(
            [
                "sudo",
                "yay",
                "--remove",
                "--cascade",
                "--recursive",
                "--nosave",
                package_id,
            ]
        )


class Package:
    """Represents a software package with metadata"""

    def __init__(
        self,
        id_map: Dict[str, List[str]],
        name: Optional[str] = None,
        description: str = "",
        tags: Optional[List[str]] = None,
    ):
        """
        Parameters:
            id_map: Mapping of identifiers to the list of package managers that use them.
            name: Human-readable name of the package. Same as 'id' if not provided.
            description: Description of the package.
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


if __name__ == "__main__":
    print(PackageManager.all_subclasses())
    print(Yay())
#     PacMan.install("fzf")
#     PacMan.uninstall("fzf")

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Type

from utils import run_command


class Package:
    """Represents a software package with metadata"""

    def __init__(
        self,
        id_map: Dict[str, List[Type[PackageManager]]],
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

    def __repr__(self) -> str:
        return (
            f"Package(id_map={self.id_map}, name='{self.name}', "
            f"description='{self.description}', tags={self.tags})"
        )


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

    @classmethod
    def choose_package_manager(
        cls, package: Package, available_pms: Optional[List[Type]] = None
    ):
        """
        Given a package, choose an appropriate package manager and package id to use.

        The package's id_map is expected to be a dict where:
          - keys are the package ids to be used for installation,
          - values are lists of package manager classes that support that id.

        If the list for a given id is empty, it is assumed that the package is supported by any package manager.
        The lower index in the list is preferred.

        Parameters:
            package: The Package to install.
            available_pms: Optionally, a pre-computed list of available package manager classes.

        Returns:
            A tuple (package_id, package_manager_class).

        Raises:
            RuntimeError: if no suitable package manager is available.
        """
        if available_pms is None:
            available_pms = cls.available_managers()

        for pkg_id, pm_list in package.id_map.items():
            if not pm_list:
                # If the list is empty, assume this id works with any available PM.
                if available_pms:
                    return pkg_id, available_pms[0]
            else:
                # Check in order which package manager is available.
                for pm in pm_list:
                    if pm in available_pms:
                        return pkg_id, pm

        return None, None


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

    @staticmethod
    def is_available(cls):
        return True


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

    @staticmethod
    def is_available(cls):
        return False


if __name__ == "__main__":
    print(PackageManager.all_subclasses())
    print(Yay())

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Type

from common.helpers import run_command


class PackageManager(ABC):
    PLATFORM: str

    @classmethod
    @abstractmethod
    def install(cls, identifiers: List[str]) -> None:
        """Install packages by identifiers."""
        pass

    @classmethod
    @abstractmethod
    def uninstall(cls, identifiers: List[str]) -> None:
        """Uninstall packages by identifiers."""
        pass


class Brew(PackageManager):
    PLATFORM = "Darwin"

    @classmethod
    def install(cls, identifiers: List[str]) -> None:
        run_command(["brew", "install", *identifiers])

    @classmethod
    def uninstall(cls, identifiers: List[str]) -> None:
        run_command(["brew", "uninstall", *identifiers])


class Yay(PackageManager):
    PLATFORM = "Linux"

    @classmethod
    def install(cls, identifiers: List[str]) -> None:
        run_command(["yay", "--sync", "--noconfirm", *identifiers])

    @classmethod
    def uninstall(cls, identifiers: List[str]) -> None:
        run_command(
            [
                "yay",
                "--remove",
                "--cascade",
                "--recursive",
                "--nosave",
                *identifiers,
            ]
        )


class Chocolatey(PackageManager):
    PLATFORM = "Windows"

    @classmethod
    def install(cls, identifiers: List[str]) -> None:
        run_command(["choco", "install", *identifiers])

    @classmethod
    def uninstall(cls, identifiers: List[str]) -> None:
        run_command(["choco", "uninstall", *identifiers])


@dataclass
class Package:
    """Represents a software package with metadata."""

    identifier: str
    manager: Type["PackageManager"]
    name: Optional[str] = None
    description: Optional[str] = None
    condition: bool = True

    def __post_init__(self):
        if self.name is None:
            self.name = self.identifier

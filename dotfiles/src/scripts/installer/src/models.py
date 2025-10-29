from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Type

from common.helpers import run_command


class PackageManager(ABC):
    PLATFORM: str

    @classmethod
    @abstractmethod
    def install(cls, package: Package) -> None:
        """Install package using manager."""
        pass

    @classmethod
    @abstractmethod
    def uninstall(cls, package: Package) -> None:
        """Uninstall package using manager."""
        pass


class Brew(PackageManager):
    PLATFORM = "Darwin"

    @classmethod
    def install(cls, package: Package) -> None:
        command = ["brew", "install"]
        if package.is_gui:
            command.append("--cask")
        command.append(package.identifier)
        run_command(command)

    @classmethod
    def uninstall(cls, package: Package) -> None:
        run_command(["brew", "uninstall", package.identifier])


class Yay(PackageManager):
    PLATFORM = "Linux"

    @classmethod
    def install(cls, package: Package) -> None:
        run_command(["yay", "--sync", "--noconfirm", package.identifier])

    @classmethod
    def uninstall(cls, package: Package) -> None:
        run_command(
            [
                "yay",
                "--remove",
                "--cascade",
                "--recursive",
                "--nosave",
                package.identifier,
            ]
        )


class Chocolatey(PackageManager):
    PLATFORM = "Windows"

    @classmethod
    def install(cls, package: Package) -> None:
        run_command(["choco", "install", package.identifier])

    @classmethod
    def uninstall(cls, package: Package) -> None:
        run_command(["choco", "uninstall", package.identifier])


@dataclass
class Package:
    """Represents a software package with metadata."""

    identifier: str
    manager: Type["PackageManager"]
    name: Optional[str] = None
    description: Optional[str] = None
    is_gui: Optional[bool] = False
    condition: bool = True

    def __post_init__(self):
        if self.name is None:
            self.name = self.identifier

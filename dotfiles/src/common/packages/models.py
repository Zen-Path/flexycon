from __future__ import annotations

import platform
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Type

from common.helpers import resolve_path


class ClipboardUtility(ABC):
    """Abstract class for clipboard utilities."""

    command: str  # Command to execute the clipboard utility

    @classmethod
    @abstractmethod
    def text(cls, text: str):
        """Copy text to the clipboard."""
        pass

    @classmethod
    @abstractmethod
    def file(cls, file_path: str):
        """Copy a file to the clipboard."""
        pass

    @classmethod
    def can_handle(cls) -> bool:
        """Check if this utility is available on the system."""
        return shutil.which(cls.command) is not None

    @classmethod
    def get_instance(cls):
        """Detect the available clipboard utility and return an instance."""
        for subclass in cls.__subclasses__():
            if subclass.can_handle():
                return subclass()

        raise EnvironmentError("No known clipboard utility is available.")


@dataclass
class Package:
    """Represents a software package with metadata."""

    identifier: str
    managers: List[Type[PackageManager]]
    name: Optional[str] = None
    description: Optional[str] = None
    is_gui: Optional[bool] = False
    destination: Optional[List[str]] = None
    condition: bool = True

    def __post_init__(self):
        if self.name is None:
            self.name = self.identifier

    @property
    def resolved_path(self) -> Optional[str]:
        return resolve_path(self.destination) if self.destination else None


class PackageManager(ABC):
    COMMAND: str
    PLATFORM: str

    @classmethod
    def check_availability(cls) -> bool:
        """Check if the package manager is available on the system."""
        return (
            platform.system() == cls.PLATFORM and shutil.which(cls.COMMAND) is not None
        )

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

    @classmethod
    @abstractmethod
    def update_all(cls) -> None:
        """Update all packages."""
        pass

from __future__ import annotations

import shutil
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from common.helpers import resolve_path


@dataclass
class Package:
    """Represents a software package with metadata."""

    identifier: str
    managers: list[type[PackageManager]]
    name: str | None = None
    description: str | None = None
    is_gui: bool | None = False
    destination: list[str] | None = None
    condition: bool = True

    def __post_init__(self):
        if self.name is None:
            self.name = self.identifier

    @property
    def resolved_path(self) -> Path | None:
        return resolve_path(self.destination) if self.destination else None


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

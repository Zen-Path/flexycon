from __future__ import annotations

import platform
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Type

from common.helpers import resolve_path


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
    def resolved_path(self) -> Optional[Path]:
        return resolve_path(self.destination) if self.destination else None


class PackageManager(ABC):
    COMMAND: str
    # When platform is None, it means it's available on all platforms
    PLATFORM: str | None

    @classmethod
    def check_availability(cls) -> bool:
        """Check if the package manager is available on the system."""
        is_platform_same = cls.PLATFORM is None or platform.system() == cls.PLATFORM
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

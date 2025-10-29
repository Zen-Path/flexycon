from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Type


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

    @classmethod
    @abstractmethod
    def update_all(cls) -> None:
        """Update all packages."""
        pass

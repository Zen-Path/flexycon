from typing import Optional, List
from abc import ABC, abstractmethod
import subprocess

class PackageInstaller(ABC):
    CMD = None

    def __init__(self):
        pass

    @abstractmethod
    def install(self, package_identifier: str):
        pass

    @abstractmethod
    def uninstall(self, package_identifier: str):
        pass

class Brew(PackageInstaller):
    CMD = "brew"

    def install(self, package_identifier: str):
        subprocess.run(self.CMD, "install", package_identifier)

    def uninstall(self, package_identifier: str):
        subprocess.run(self.CMD, "uninstall", package_identifier)

class Package:
    def __init__(
        self,
        name: str,
        identifier: str,
        installer: PackageInstaller,
        purpose: str = "",
        tags: Optional[List[str]] = None
    ):
        """
        Represents a software package with metadata and installation details.

        Parameters:
            name (str): Human-readable name of the package.
            identifier (str): Repository or unique package identifier.
            installer (Installer): Installer instance to handle package installation.
            purpose (str, optional): Description of the package's purpose. Defaults to an empty string.
            tags (List[str], optional): Tags for categorizing the package. Defaults to an empty list.
        """
        self.name = name
        self.identifier = identifier
        self.installer = installer
        self.purpose = purpose
        self.tags = tags or []

    def install(self):
        self.installer(self.identifier)

    def __repr__(self):
        return f"Package(name='{self.name}', identifier='{self.identifier}', purpose='{self.purpose}', tags={self.tags})"

brew = Brew()

packages = [
    Package("fzf", "fzf", brew, "fuzzy searching", ["terminal"])
]

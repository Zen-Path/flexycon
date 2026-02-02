import shutil

from common.helpers import run_command
from common.logger import logger
from common.packages.models import Package, PackageManager


class Brew(PackageManager):
    PLATFORM = "Darwin"
    COMMAND = "brew"

    @classmethod
    def install(cls, package: Package) -> None:
        command = [cls.COMMAND, "install"]
        if package.is_gui:
            command.append("--cask")
        command.append(package.identifier)
        run_command(command)

    @classmethod
    def uninstall(cls, package: Package) -> None:
        run_command([cls.COMMAND, "uninstall", package.identifier])

    @classmethod
    def update_all(cls) -> None:
        run_command([cls.COMMAND, "update"])  # Syncs formulae
        run_command([cls.COMMAND, "upgrade"])  # Upgrades packages


class Yay(PackageManager):
    PLATFORM = "Linux"
    COMMAND = "yay"

    @classmethod
    def install(cls, package: Package) -> None:
        run_command(
            [cls.COMMAND, "--sync", "--needed", "--noconfirm", package.identifier]
        )

    @classmethod
    def uninstall(cls, package: Package) -> None:
        run_command(
            [
                cls.COMMAND,
                "--remove",
                "--cascade",
                "--recursive",
                "--nosave",
                package.identifier,
            ]
        )

    @classmethod
    def update_all(cls) -> None:
        run_command([cls.COMMAND, "--sync", "--refresh", "--sysupgrade"])


class Chocolatey(PackageManager):
    PLATFORM = "Windows"
    COMMAND = "choco"

    @classmethod
    def install(cls, package: Package) -> None:
        run_command([cls.COMMAND, "upgrade", package.identifier])

    @classmethod
    def uninstall(cls, package: Package) -> None:
        run_command([cls.COMMAND, "uninstall", package.identifier])

    @classmethod
    def update_all(cls) -> None:
        run_command([cls.COMMAND, "upgrade", "all", "--confirm"])


class Git(PackageManager):
    PLATFORM = None
    COMMAND = "git"

    @classmethod
    def install(cls, package: Package) -> None:
        if not package.resolved_path:
            logger.error(
                f"Package {package.identifier} requires a 'destination' for Git "
                "operations."
            )
            return

        if package.resolved_path.exists() and (package.resolved_path / ".git").exists():
            # Pull changes for "update" logic
            run_command([cls.COMMAND, "-C", str(package.resolved_path), "pull"])
        else:
            # Fresh clone
            run_command(
                [
                    cls.COMMAND,
                    "clone",
                    "--recurse-submodules",
                    package.identifier,
                    str(package.resolved_path),
                ]
            )

    @classmethod
    def uninstall(cls, package: Package) -> None:
        if package.resolved_path and package.resolved_path.exists():
            shutil.rmtree(package.resolved_path)

    @classmethod
    def update_all(cls) -> None:
        pass

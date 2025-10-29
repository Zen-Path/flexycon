from common.helpers import run_command
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
        run_command([cls.COMMAND, "upgrade"])


class Yay(PackageManager):
    PLATFORM = "Linux"
    COMMAND = "yay"

    @classmethod
    def install(cls, package: Package) -> None:
        run_command([cls.COMMAND, "--sync", "--noconfirm", package.identifier])

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
        run_command([cls.COMMAND, "install", package.identifier])

    @classmethod
    def uninstall(cls, package: Package) -> None:
        run_command([cls.COMMAND, "uninstall", package.identifier])

    @classmethod
    def update_all(cls) -> None:
        run_command([cls.COMMAND, "upgrade", "all"])

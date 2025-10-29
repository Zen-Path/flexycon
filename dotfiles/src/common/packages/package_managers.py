from common.helpers import run_command
from common.packages.models import Package, PackageManager


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

    @classmethod
    def update_all(cls) -> None:
        run_command(["brew", "upgrade"])


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

    @classmethod
    def update_all(cls) -> None:
        run_command(["yay", "--sync", "--refresh", "--sysupgrade"])


class Chocolatey(PackageManager):
    PLATFORM = "Windows"

    @classmethod
    def install(cls, package: Package) -> None:
        run_command(["choco", "install", package.identifier])

    @classmethod
    def uninstall(cls, package: Package) -> None:
        run_command(["choco", "uninstall", package.identifier])

    @classmethod
    def update_all(cls) -> None:
        run_command(["choco", "upgrade", "all"])

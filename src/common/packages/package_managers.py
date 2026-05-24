import re
import shutil

from common.cmd_utilities import run_cmd
from common.logger import log
from common.packages.models import Package, PackageManager


class Brew(PackageManager):
    PLATFORM = "darwin"
    COMMAND = "brew"

    check_pattern = re.compile(
        r"^Warning: ([^ ]+) .* is already installed and up-to-date\.$"
    )
    update_outdated_pattern = re.compile(
        r"([^ ]+) .* is already installed but outdated"
    )
    update_action_pattern = re.compile(r"^==> Upgrading ([^ ]+)$")
    install_pattern = re.compile(r"^==> Installing ([^ ]+)$")

    @classmethod
    def process_output(cls, output: str):
        for line in output.splitlines():
            if not line:
                continue

            # Updates
            match = cls.update_outdated_pattern.match(
                line
            ) or cls.update_action_pattern.match(line)
            if match:
                log.info(f"- {match.group(1)} was updated.")
                continue

            # Installs
            match = cls.install_pattern.match(line)
            if match:
                log.info(f"- {match.group(1)} was installed.")
                continue

    @classmethod
    def install(cls, package: Package) -> None:
        command = [cls.COMMAND, "install"]
        if package.is_gui:
            command.append("--cask")
        command.append(package.identifier)
        result = run_cmd(command)

        cls.process_output(result.output)

    @classmethod
    def uninstall(cls, package: Package) -> None:
        run_cmd([cls.COMMAND, "uninstall", package.identifier])

    @classmethod
    def update_all(cls) -> None:
        run_cmd([cls.COMMAND, "update"])  # Syncs formulae
        run_cmd([cls.COMMAND, "upgrade"])  # Upgrades packages


class Yay(PackageManager):
    PLATFORM = "linux"
    COMMAND = "yay"

    @classmethod
    def install(cls, package: Package) -> None:
        run_cmd([cls.COMMAND, "--sync", "--needed", "--noconfirm", package.identifier])

    @classmethod
    def uninstall(cls, package: Package) -> None:
        run_cmd(
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
        run_cmd([cls.COMMAND, "--sync", "--refresh", "--sysupgrade"])


class Chocolatey(PackageManager):
    PLATFORM = "win32"
    COMMAND = "choco"

    @classmethod
    def install(cls, package: Package) -> None:
        run_cmd([cls.COMMAND, "upgrade", package.identifier])

    @classmethod
    def uninstall(cls, package: Package) -> None:
        run_cmd([cls.COMMAND, "uninstall", package.identifier])

    @classmethod
    def update_all(cls) -> None:
        run_cmd([cls.COMMAND, "upgrade", "all", "--confirm"])


class Git(PackageManager):
    PLATFORM = None
    COMMAND = "git"

    @classmethod
    def install(cls, package: Package) -> None:
        if not package.destination:
            log.error(
                f"Package {package.identifier!r} requires a 'destination' for Git "
                "operations."
            )
            return

        if package.destination.exists() and (package.destination / ".git").exists():
            # Pull changes for "update" logic
            run_cmd([cls.COMMAND, "-C", package.destination, "pull"])
        else:
            # Fresh clone
            run_cmd(
                [
                    cls.COMMAND,
                    "clone",
                    "--recurse-submodules",
                    package.identifier,
                    package.destination,
                ]
            )

    @classmethod
    def uninstall(cls, package: Package) -> None:
        if package.destination and package.destination.exists():
            shutil.rmtree(package.destination)

    @classmethod
    def update_all(cls) -> None:
        pass

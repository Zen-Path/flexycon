import re
import shutil

from git import Repo

from common.cmd_utilities import run_cmd
from common.logger import log
from common.packages.models import Package, PackageManager


class Brew(PackageManager):
    PLATFORM = "darwin"
    COMMAND = "brew"

    update_outdated_pattern = re.compile(
        r"([^ ]+) .* is already installed but outdated"
    )
    update_action_pattern = re.compile(r"^==> Upgrading ([^ ]+)$")
    install_success_pattern = re.compile(
        r"^🍺\s+/opt/homebrew/(?:Cellar|Caskroom)/([^/]+)"
    )

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
            match = cls.install_success_pattern.match(line)
            if match:
                log.info(f"- {match.group(1)} was installed.")
                continue

    @classmethod
    def install(cls, packages: list[Package]) -> None:
        if not packages:
            return

        formulas: list[str] = []
        casks: list[str] = []
        for package in packages:
            if package.is_gui:
                casks.append(package.identifier)
            else:
                formulas.append(package.identifier)

        # Batch all regular formulas together
        if formulas:
            cmd = [cls.COMMAND, "install"] + formulas
            result = run_cmd(cmd)
            cls.process_output(result.output)

        # Batch all GUI casks together
        if casks:
            cmd = [cls.COMMAND, "install", "--cask"] + casks
            result = run_cmd(cmd)
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
    def install(cls, packages: list[Package]) -> None:
        identifiers = [package.identifier for package in packages]
        run_cmd([cls.COMMAND, "--sync", "--needed", "--noconfirm", *identifiers])

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
    def install(cls, packages: list[Package]) -> None:
        # TODO: investigate if choco has bulk install
        for package in packages:
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
    def install(cls, packages: list[Package]) -> None:
        for package in packages:
            if not package.destination:
                log.error(f"Package {package.identifier!r} requires a 'destination'.")
                continue

            try:
                if (package.destination / ".git").exists():
                    # Update logic
                    repo = Repo(package.destination)
                    origin = repo.remotes.origin

                    commit_before = repo.head.commit.hexsha
                    origin.pull()
                    commit_after = repo.head.commit.hexsha

                    # Check if changes were actually pulled
                    if commit_before != commit_after:
                        log.info(
                            f"- {package.name!r} was updated from "
                            f"{commit_before[:7]} to {commit_after[:7]}"
                        )
                else:
                    # Fresh clone logic
                    Repo.clone_from(
                        package.identifier, package.destination, recurse_submodules=True
                    )
                    log.info(f"- {package.name!r} was installed.")

            except Exception as e:
                log.error(f"Unable to install {package.name!r}: {e}")

    @classmethod
    def uninstall(cls, package: Package) -> None:
        if package.destination and package.destination.exists():
            shutil.rmtree(package.destination)

    @classmethod
    def update_all(cls) -> None:
        pass

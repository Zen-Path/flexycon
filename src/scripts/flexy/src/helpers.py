import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, NamedTuple

from common.cmd_utilities import run_cmd
from common.logger import log
from common.variables import FLEXYCON_CONFIG, FLEXYCON_DATA, FLEXYCON_HOME

VENV_DIR = Path(".venv")
VENV_BIN = VENV_DIR / ("Scripts" if sys.platform == "win32" else "bin")
PIP_BIN = VENV_BIN / "pip"
PYTHON_BIN = shutil.which("python3") or "python"

USER_VARIABLES_PATH = Path("uservariables.yaml")


class Action(NamedTuple):
    name: str
    description: str
    fn: Callable[..., Any]


def remove_flexycon_data():
    log.info("💀 Removing flexycon data...")

    if FLEXYCON_DATA.exists():
        try:
            shutil.rmtree(FLEXYCON_DATA, ignore_errors=True)
            log.info("Removed flexycon local data directory")
        except Exception as e:
            log.warning(e)


def clean_precommit():
    log.info("💀 Cleaning up pre-commit hooks...")

    precommit_bin = VENV_BIN / "pre-commit"
    if not precommit_bin.exists():
        log.error("pre-commit not found")
        return

    try:
        run_cmd([precommit_bin, "clean"])
    except subprocess.CalledProcessError as e:
        log.error(e)


def init_submodules():
    if not Path(".gitmodules").exists():
        log.error("No git submodules found. Skipping.")
        return

    log.info("Initializing submodules...")
    run_cmd(["git", "submodule", "init"])

    log.info("Updating submodules...")
    run_cmd(["git", "submodule", "update", "--recursive", "--remote"])


def get_dotdrop_profile() -> str | None:
    """
    Resolve the active dotdrop profile from the environment or user variables
    file.
    """
    profile = os.getenv("DOTDROP_PROFILE")
    if profile:
        return profile

    if not USER_VARIABLES_PATH.exists():
        log.info("Installing bootstrap profile to generate user variables file.")
        try:
            run_cmd([VENV_BIN / "dotdrop", "install", "--profile", "bootstrap"])
        except KeyboardInterrupt:
            sys.exit(0)

    if USER_VARIABLES_PATH.exists():
        with USER_VARIABLES_PATH.open() as f:
            import yaml

            data = yaml.safe_load(f)
            profile = data.get("variables", {}).get("active_dotdrop_profile")

    if not profile:
        log.error("Could not resolve dotdrop profile.")
        return None

    log.debug(f"Active dotdrop profile: {profile}")
    return profile


def install_dotfiles_to_temp(profile: str | None) -> Path:
    """Install dotdrop profile's dotfiles to a temp directory and return the its path."""
    cmd = [f"{VENV_BIN}/dotdrop", "install", "--temp", "--force"]
    if profile:
        cmd.extend(["--profile", profile])

    result = run_cmd(cmd)
    if not result.success:
        log.error(f"Dotdrop output:\n{result.output}")
        raise RuntimeError("Installing temporary dotdrop profile failed.")

    match = re.search(r'installed to tmp "([^"]+)"', result.output)
    if not match:
        raise RuntimeError("Could not find temporary install path in output.")

    temp_path = Path(match.group(1))
    log.debug(f"Temp path {str(temp_path)!r}")
    return temp_path


def copy_dotfiles_from_temp(temp_path: Path):
    """Copy .zprofile from a temp directory with dotfiles to the user's home."""
    home = Path.home()
    src = temp_path / home.relative_to(home.anchor) / ".zprofile"
    dst = home / ".zprofile"
    shutil.copy2(src, dst)
    log.debug(f"Copied {str(src)!r} -> {str(dst)!r}")


def format_yazi_packages_file():
    log.info("🧼 Formatting yazi packages file...")
    try:
        run_cmd(
            [
                "taplo",
                "fmt",
                "--config",
                FLEXYCON_HOME / ".taplo.toml",
                FLEXYCON_CONFIG / "yazi" / "package.toml",
            ]
        )
    except Exception as e:
        log.error(f"Unable to format yazi packages: {e}")
        return False


def upgrade_yazi_packages() -> bool:
    log.info("📦 Upgrading yazi packages...")

    try:
        result = run_cmd(["ya", "pkg", "upgrade"]).success
        log.info(f"Yazi upgrade {'successful' if result else 'failed'}.")
        format_yazi_packages_file()
        return result

    except KeyboardInterrupt:
        sys.exit(1)

    except Exception as e:
        log.error(f"Unable to upgrade yazi packages: {e}")
        return False

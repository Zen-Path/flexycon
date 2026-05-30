import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, NamedTuple

import yaml

from common.cmd_utilities import run_cmd
from common.logger import log
from common.variables import FLEXYCON_CONFIG, FLEXYCON_DATA, FLEXYCON_HOME, HOME

VENV_DIR = FLEXYCON_HOME / ".venv"
VENV_BIN = VENV_DIR / ("Scripts" if sys.platform == "win32" else "bin")
PIP_BIN = VENV_BIN / "pip"
PYTHON_BIN = shutil.which("python3") or "python"

USER_VARIABLES_PATH = FLEXYCON_HOME / "uservariables.yaml"
DOTDROP_CONFIG = FLEXYCON_HOME / "config.yaml"


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
    try:
        run_cmd([precommit_bin, "clean"])
    except subprocess.CalledProcessError as e:
        log.error(e)


def git_update_submodules():
    log.info("[git] Initializing submodules...")

    if not Path(".gitmodules").exists():
        log.error("[git] File '.gitmodules' not found.")
        return False

    result = run_cmd(["git", "submodule", "init"])
    if not result.success:
        log.error("[git] Initializing submodules failed.")
        return False

    log.info("[git] Updating submodules...")
    result = run_cmd(["git", "submodule", "update", "--recursive", "--remote"])
    if not result.success:
        log.error("[git] Updating submodules failed.")

    return result.success


def get_actual_dotdrop_profiles() -> list[str]:
    with DOTDROP_CONFIG.open() as f:
        data = yaml.safe_load(f)

    return [
        profile
        for profile in data.get("profiles", {}).keys()
        if not profile.startswith("meta") and profile != "bootstrap"
    ]


def get_dotdrop_profile() -> str | None:
    """
    Resolve the active dotdrop profile from the environment or user variables
    file.
    """
    profile = os.getenv("DOTDROP_PROFILE")
    if profile:
        return profile

    if not USER_VARIABLES_PATH.exists():
        log.info(
            "[dotdrop] Installing bootstrap profile to generate user variables file."
        )

        try:
            run_cmd(
                [
                    VENV_BIN / "dotdrop",
                    "install",
                    "--profile",
                    "bootstrap",
                    "--cfg",
                    DOTDROP_CONFIG,
                ]
            )
        except Exception as e:
            log.error(f"[dotdrop] Unable to install bootstrap profile: {e}")
            return None

    try:
        log.debug(f"[dotdrop] User variables file: {str(USER_VARIABLES_PATH)!r}")

        with USER_VARIABLES_PATH.open() as f:
            data = yaml.safe_load(f)
            profile = data.get("variables", {}).get("active_dotdrop_profile")

    except Exception as e:
        log.error(f"[dotdrop] Unable to read user variables file: {e}")
        return None

    if not profile:
        log.error("[dotdrop] Unable to resolve active dotdrop profile")
        return None

    log.debug(f"[dotdrop] Active profile: {profile!r}")
    return profile


def install_dotfiles_to_temp(profile: str | None) -> Path:
    """Install dotdrop profile's dotfiles to a temp directory and return the its path."""

    cmd: list[str | Path] = [
        VENV_BIN / "dotdrop",
        "install",
        "--temp",
        "--force",
        "--cfg",
        DOTDROP_CONFIG,
    ]
    if profile:
        cmd.extend(["--profile", profile])

    result = run_cmd(cmd)
    log.debug(f"[dotdrop] Output:\n{result.output}")

    if not result.success:
        raise RuntimeError("[dotdrop] Installing temporary profile failed.")

    match = re.search(r'installed to tmp "([^"]+)"', result.output)
    if not match:
        raise RuntimeError("[dotdrop] Could not find temporary install path in output.")

    temp_path = Path(match.group(1))
    log.debug(f"[dotdrop] Temp path {str(temp_path)!r}")

    return temp_path


def copy_dotfiles_from_temp(temp_path: Path):
    """Copy .zprofile from a temp directory with dotfiles to the user's home."""

    src = temp_path / HOME.relative_to(HOME.anchor) / ".zprofile"
    dst = HOME / ".zprofile"
    shutil.copy2(src, dst)

    log.debug(f"[dotdrop] Copied {str(src)!r} -> {str(dst)!r}")


def yazi_format_packages_file() -> bool:
    log.info("[yazi] Formatting packages file...")

    package_file = FLEXYCON_CONFIG / "yazi" / "package.toml"
    log.debug(f"[yazi] Packages file path: {str(package_file)!r}")

    try:
        result = run_cmd(
            [
                "taplo",
                "fmt",
                "--config",
                FLEXYCON_HOME / ".taplo.toml",
                package_file,
            ]
        )
    except Exception as e:
        log.error(f"[yazi] Unable to format packages file: {e}")
        return False

    if not result.success:
        log.info("[yazi] Formatting packages file failed.")

    return result.success


def yazi_upgrade_packages() -> bool:
    log.info("[yazi] Upgrading packages...")

    try:
        # Add '--discard' to prevent errors if there's been any changes to the packages
        result = run_cmd(["ya", "pkg", "upgrade", "--discard"])
    except Exception as e:
        log.error(f"[yazi] Unable to upgrade packages: {e}")
        return False

    packages = re.findall(r"Upgrading package `([^`]+)`", result.output)
    for pkg in packages:
        log.info(f"- Upgrading package {pkg!r}")

    if not result.success:
        log.error("[yazi] Upgrading packages failed.")

    # Formatting regardless of success status in case the upgrade was partially
    # successful and made changes to the file.
    yazi_format_packages_file()

    return result.success


def get_sip_status() -> bool | None:
    log.info("👀 Checking System Integrity Protection status.")

    if sys.platform != "Darwin":
        return None

    try:
        result = run_cmd(["csrutil", "status"])
    except Exception:
        return None

    match = re.search(r"status:\s*(\w+)", result.output)
    if match:
        status = match.group(1)
        return status != "disabled"

    return None


def npm_install_packages() -> bool:
    log.info("[npm] Installing packages...")

    try:
        result = run_cmd(["npm", "install"])
    except Exception as e:
        log.error(f"[npm] Unable to install packages: {e}.")
        return False

    if not result.success:
        log.error("[npm] Installing packages failed.")

    return result.success


def playwright_install() -> bool:
    # log.info(msg="📦 Installing playwright...")

    try:
        # We don't have any tests that require playwright at the moment
        result = True or run_cmd(["playwright", "install"])
    except Exception as e:
        log.error(f"Unable to install playwright: {e}")
        return False

    if not result:
        log.error("Installing playwright failed.")

    return result

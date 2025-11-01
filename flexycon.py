#!/usr/bin/env python3

import argparse
import logging
import os
import platform
import shutil
import subprocess
from pathlib import Path

from common.helpers import run_command
from common.logger import logger, setup_logging
from common.variables import flex_data_path
from scripts.installer.data.packages import packages
from scripts.installer.main import process_packages
from scripts.user_shortcuts.data.shortcuts import shortcuts
from scripts.user_shortcuts.main import AVAILABLE_RENDERERS

VENV_DIR = Path("venv")
VENV_BIN = VENV_DIR / ("Scripts" if platform.system() == "Windows" else "bin")
PIP_BIN = str(VENV_BIN / "pip")
PYTHON_BIN = shutil.which("python3") or "python"

REQUIREMENTS_FILE = Path("requirements.txt")
USER_VARIABLES_PATH = Path("uservariables.yaml")

UNINSTALL_TARGETS = [
    ".venv",
    "venv",
]

CLEAN_TARGETS = [
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    "dist",
    "build",
    "*.egg-info",
    "node_modules",
    ".DS_Store",
]

EMPTY_EXCLUDE_TARGETS = [".git"]


# === HELPER ===


# Registry to store all decorated functions
TARGETS = {}


def target(name=None, description=None):
    """Decorator to mark functions as CLI targets."""

    def decorator(func):
        target_name = (name or func.__name__).replace(" ", "_")

        description_fmt = (description or func.__doc__ or "").strip()
        if description_fmt:
            description_fmt = description_fmt[:1].lower() + description_fmt[1:]

        if target_name in TARGETS:
            raise ValueError(f"Duplicate target name: {target_name}")

        TARGETS[target_name] = {
            "name": target_name,
            "description": description_fmt,
            "fn": func,
        }
        return func

    return decorator


def remove_targets(targets):
    for target in targets:
        for path in Path(".").rglob(target):
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                logger.debug(f"Removed {path}")
            except Exception as e:
                logger.warning(e)


def remove_flexycon_data():
    logger.info("💀 Removing flexycon data...")

    if flex_data_path.exists():
        try:
            shutil.rmtree(flex_data_path, ignore_errors=True)
            logger.info("Removed flexycon local data directory")
        except Exception as e:
            logger.warning(e)


def clean_precommit():
    logger.info("💀 Cleaning up pre-commit hooks...")

    precommit_bin = VENV_BIN / "pre-commit"
    if not precommit_bin.exists():
        logger.error("pre-commit not found")
        return

    try:
        run_command([str(precommit_bin), "clean"])
    except subprocess.CalledProcessError as e:
        logger.error(e)


def remove_empty_dirs():
    logger.info("🧹 Removing empty directories.")

    empty_dirs = []
    for root, dirs, files in os.walk(".", topdown=True):
        # modify dirs in-place to prevent walking excluded folders
        dirs[:] = [d for d in dirs if d not in EMPTY_EXCLUDE_TARGETS]

        for d in dirs:
            dir_path = Path(root) / d
            if not any(dir_path.iterdir()):
                empty_dirs.append(dir_path)

    for d in empty_dirs:
        try:
            d.rmdir()
            logger.debug(f"Removed {d}")
        except Exception as e:
            logger.warning(e)


def init_submodules():
    if not Path(".gitmodules").exists():
        logger.error("No git submodules found. Skipping.")
        return

    logger.info("Initializing submodules...")
    run_command(["git", "submodule", "init"])

    logger.info("Updating submodules...")
    run_command(["git", "submodule", "update", "--recursive", "--remote"])


# === TARGETS ===


@target()
def setup_virtual_env():
    """Create and setup a virtual environment"""
    logger.info("⚙️ Create virtual environment if it doesn't exist...")

    if not VENV_DIR.exists():
        logger.info(f"🐍 Creating Python venv in '{VENV_DIR}'...")
        run_command([PYTHON_BIN, "-m", "venv", "VENV_DIR"])

    logger.info("♻️ Updating pip...")
    run_command([PIP_BIN, "install", "--upgrade", "pip"])

    logger.info("📦 Installing Python dependencies...")
    if REQUIREMENTS_FILE.exists():
        run_command([PIP_BIN, "install", "-r", str(REQUIREMENTS_FILE)])
    else:
        logger.warning("Python dependencies not found.")

    logger.info("🔧 Installing current project in editable mode...")
    run_command([PIP_BIN, "install", "-e", "."])


@target()
def setup():
    """Setup project and install dependencies"""
    logger.info("📦 Installing system packages...")

    system = platform.system()
    if system == "Darwin" and shutil.which("brew") is None:
        logger.warning(
            "Homebrew is not installed. Please install it from https://brew.sh/"
        )
    else:
        process_packages(packages)

    logger.info("⑂ Initializing git submodules...")
    init_submodules()

    setup_virtual_env()

    logger.info("📦 Installing npm packages...")
    if shutil.which("npm"):
        run_command(["npm", "install"])
    else:
        logger.warning("npm not found. Skipping npm installation.")

    logger.info("📦 Installing pre-commit hooks...")
    precommit_bin = VENV_BIN / "pre-commit"
    if precommit_bin.exists():
        run_command([str(precommit_bin), "install", "--install-hooks"])
    else:
        logger.warning("pre-commit not found. Skipping hook installation.")


@target()
def install():
    """Install and apply configuration"""
    import yaml

    if not VENV_DIR.exists():
        logger.error(f"Missing venv at '{VENV_DIR}'. Run the 'setup' target first.")
        return

    logger.info("⚙️ Generating shortcuts...")
    for renderer in AVAILABLE_RENDERERS:
        renderer.process(shortcuts)

    logger.info("⚙️ Installing configuration...")

    # When installing for the first, flexycon's env vars will not be
    # set, but we can extract the profile from the user variables file
    dotdrop_profile = os.getenv("DOTDROP_PROFILE")
    if not dotdrop_profile and USER_VARIABLES_PATH.exists():
        with open(USER_VARIABLES_PATH) as f:
            data = yaml.safe_load(f)
            dotdrop_profile = data["variables"]["active_dotdrop_profile"]

    if dotdrop_profile:
        logger.debug(f"Active dotdrop profile: {dotdrop_profile}")
        subprocess.run(["dotdrop", "install", "--profile", dotdrop_profile])

    # TODO: Apply macOS default here


@target()
def clean():
    """Remove caches and temporary files"""
    logger.info("🧹 Removing clean targets...")
    remove_targets(CLEAN_TARGETS)

    remove_empty_dirs()


@target()
def uninstall():
    """Clean project and remove flexycon's data"""
    clean()

    clean_precommit()

    logger.info("🔪 Removing uninstall targets...")
    remove_targets(UNINSTALL_TARGETS)

    remove_flexycon_data()


# === MAIN ===


def build_parser(targets):
    parser = argparse.ArgumentParser(description="Help utility for managing flexycon.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Dynamically add subcommands
    for name, meta in targets.items():
        subparsers.add_parser(name, help=meta["description"])

    parser.add_argument("--verbose", action="store_true", help="enable debug output")

    return parser


def main():
    args = build_parser(TARGETS).parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.INFO)

    if args.command in TARGETS:
        TARGETS[args.command]["fn"]()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import argparse
import logging
import platform
import shutil
import subprocess
from pathlib import Path

from common.helpers import run_command
from common.logger import logger, setup_logging

VENV_DIR = Path("venv")
VENV_BIN = VENV_DIR / ("Scripts" if platform.system() == "Windows" else "bin")

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

    flexycon_data_path = Path.home() / ".local" / "share" / "flexycon"
    if flexycon_data_path.exists():
        try:
            shutil.rmtree(flexycon_data_path, ignore_errors=True)
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

    empty_dirs = [
        p for p in Path(".").rglob("*") if p.is_dir() and not any(p.iterdir())
    ]
    for d in empty_dirs:
        try:
            d.rmdir()
            logger.debug(f"Removed {d}")
        except Exception as e:
            logger.warning(e)


def setup():
    """Setup project and init git submodules"""
    pass


def install():
    """Create Python venv, install Python, project dependencies"""
    pass


def uninstall():
    """Remove all flexycon config and data"""
    logger.info("🧹 Removing clean targets...")
    remove_targets(CLEAN_TARGETS)

    logger.info("🔪 Removing uninstall targets...")
    remove_targets(UNINSTALL_TARGETS)

    clean_precommit()
    remove_flexycon_data()


def clean():
    """Remove temporary/project files and venv"""
    logger.info("🧹 Removing clean targets...")
    remove_targets(CLEAN_TARGETS)

    remove_empty_dirs()


def describe_functions(functions):
    return {
        f.__name__: {
            "description": (f.__doc__ or "").strip(),
            "fn": f,
        }
        for f in functions
    }


def build_parser(targets):
    parser = argparse.ArgumentParser(description="Help utility for managing flexycon.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Dynamically add subcommands
    for name, meta in targets.items():
        subparsers.add_parser(name, help=meta["description"])

    parser.add_argument("--verbose", action="store_true", help="enable debug output")

    return parser


def main():
    targets = describe_functions([setup, install, uninstall, clean])

    args = build_parser(targets).parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.INFO)

    if args.command in targets:
        targets[args.command]["fn"]()


if __name__ == "__main__":
    main()

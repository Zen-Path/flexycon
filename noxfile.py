import platform
import shutil
import subprocess
from pathlib import Path

import nox

BREW_DEPS = ["python3", "node", "dotdrop"]


def sh(cmd):
    print(f"🔧 {cmd}")
    subprocess.run(cmd, shell=True, check=True)


@nox.session
def install(session):
    """Setup system deps, npm, and pre-commit hooks."""

    # System deps
    system = platform.system()
    match system:
        case "Darwin":
            print("🖥️ macOS detected")
            if not shutil.which("brew"):
                session.error("❌ Homebrew not found. Install it from https://brew.sh/")

            for dep in BREW_DEPS:
                if not shutil.which(dep):
                    ans = (
                        input(f"🔍 '{dep}' not found. Install it now? [y/N]: ")
                        .strip()
                        .lower()
                    )
                    if ans == "y":
                        sh(f"brew install {dep}")
                    else:
                        print(f"⚠️ Skipping '{dep}'")
                else:
                    print(f"✅ '{dep}' is already installed")
        case _:
            print(f"System {system} is not supported")

    # npm deps
    if Path("package.json").exists():
        sh("npm install")
    else:
        print("⚠️ No package.json found")

    # pre-commit hooks
    if shutil.which("pre-commit"):
        sh("pre-commit install --install-hooks")
    else:
        session.error("❌ pre-commit not found")


@nox.session
def clean(session):
    """Clean up project build and cache files."""
    paths = [
        "build",
        "dist",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "*.egg-info",
        "__pycache__",
        "node_modules",
    ]
    for pattern in paths:
        for path in Path(".").rglob(pattern):
            try:
                if path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    path.unlink()
            except Exception as e:
                print(f"⚠️ Could not remove {path}: {e}")
    print("🧹 Project cleanup complete.")


@nox.session
def init_submodules(session):
    """Initialize and update git submodules."""
    if not Path(".gitmodules").exists():
        print("ℹ️ No .gitmodules found. Skipping submodule init.")
        return
    print("🔄 Initializing and updating git submodules...")
    sh("git submodule init")
    sh("git submodule update --recursive --remote")


@nox.session
def setup(session):
    """Run full setup: submodules + install."""
    session.notify("init_submodules")
    session.notify("install")

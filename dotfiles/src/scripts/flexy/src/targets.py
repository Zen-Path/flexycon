import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, TypedDict, TypeVar

from common.helpers import remove_files_by_pattern, run_command
from common.logger import logger
from common.variables import flex_data_path
from scripts.package_installer.data.packages import packages
from scripts.package_installer.main import process_packages
from scripts.user_shortcuts.main import AVAILABLE_RENDERERS, get_active_shortcuts

VENV_DIR = Path(".venv")
VENV_BIN = VENV_DIR / ("Scripts" if sys.platform == "win32" else "bin")
PIP_BIN = str(VENV_BIN / "pip")
PYTHON_BIN = shutil.which("python3") or "python"

USER_VARIABLES_PATH = Path("uservariables.yaml")


# === HELPER ===


class TargetInfo(TypedDict):
    name: str
    description: str
    fn: Callable[..., Any]


TARGETS: dict[str, TargetInfo] = {}

F = TypeVar("F", bound=Callable[..., Any])


def target(name: str | None = None, description: str | None = None) -> Callable[[F], F]:
    """Decorator to mark functions as CLI targets."""

    def decorator(func: F) -> F:
        # Use provided name or fall back to function name
        target_name: str = (name or func.__name__).replace(" ", "_")

        # Format description from argument or docstring
        raw_doc: str = description or func.__doc__ or ""
        description_fmt: str = raw_doc.strip()

        if description_fmt:
            # Lowercase the first letter for consistent CLI formatting
            description_fmt = description_fmt[:1].lower() + description_fmt[1:]

        if target_name in TARGETS:
            raise ValueError(f"Duplicate target name {target_name!r}.")

        TARGETS[target_name] = {
            "name": target_name,
            "description": description_fmt,
            "fn": func,
        }

        return func

    return decorator


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


def remove_empty_dirs(
    base_dir: str | Path = ".",
    global_excludes: set[str] | None = None,
    protected_roots: set[Path] | None = None,
) -> None:
    """
    Removes empty directories bottom-up, respecting global name exclusions
    and specific protected root paths.

    :param base_dir: The root directory to start the cleanup from.
    :param global_excludes: Set of exact directory names to ignore everywhere.
    :param protected_roots: Set of exact Path roots to protect.
    """
    if global_excludes is None:
        global_excludes = set()

    if protected_roots is None:
        protected_roots = set()

    # Normalize base_path and protected roots for safety
    base_path = Path(base_dir).resolve()
    resolved_protected = {p.resolve() for p in protected_roots}

    logger.info(f"🧹 Removing empty directories in '{base_path}'.")

    # topdown=False ensures we process leaf directories before their parents
    for root, dirs, _files in os.walk(base_path, topdown=False):
        root_path = Path(root).resolve()

        # SKIP LOGIC A: Is the current tree protected?
        if any(root_path.is_relative_to(prot) for prot in resolved_protected):
            continue

        if any(part in global_excludes for part in root_path.parts):
            continue

        for d in dirs:
            dir_path = root_path / d

            # SKIP LOGIC B: Is this specific subdirectory protected?
            if any(dir_path.is_relative_to(prot) for prot in resolved_protected):
                continue

            if d in global_excludes:
                continue

            # ATTEMPT REMOVAL
            try:
                # iterdir() yields all contents (including hidden files and broken symlinks)
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    logger.debug(f"Removed empty directory {str(dir_path)!r}")
            except OSError as e:
                logger.warning(f"Could not remove {str(dir_path)!r}: {e}")


def init_submodules():
    if not Path(".gitmodules").exists():
        logger.error("No git submodules found. Skipping.")
        return

    logger.info("Initializing submodules...")
    run_command(["git", "submodule", "init"])

    logger.info("Updating submodules...")
    run_command(["git", "submodule", "update", "--recursive", "--remote"])


def get_dotdrop_profile() -> str | None:
    """
    Resolve the active dotdrop profile from the environment or user variables
    file.
    """
    profile = os.getenv("DOTDROP_PROFILE")
    if profile:
        return profile

    if not USER_VARIABLES_PATH.exists():
        logger.info("Installing bootstrap profile to generate user variables file.")
        try:
            run_command(
                [str(VENV_BIN / "dotdrop"), "install", "--profile", "bootstrap"]
            )
        except KeyboardInterrupt:
            sys.exit(0)

    if USER_VARIABLES_PATH.exists():
        with USER_VARIABLES_PATH.open() as f:
            import yaml

            data = yaml.safe_load(f)
            profile = data.get("variables", {}).get("active_dotdrop_profile")

    if not profile:
        logger.error("Could not resolve dotdrop profile.")
        return None

    logger.debug(f"Active dotdrop profile: {profile}")
    return profile


def install_temp_profile() -> Path:
    """Install dotdrop profile to a temporary directory and return the temp path."""
    output = run_command([f"{VENV_BIN}/dotdrop", "install", "--temp", "--force"]).output
    match = re.search(r'installed to tmp "([^"]+)"', output)
    if not match:
        logger.debug(f"Dotdrop output:\n{output}")
        raise RuntimeError("Could not find temporary install path in output.")

    temp_path = Path(match.group(1))
    logger.debug(f"Temp path {str(temp_path)!r}")
    return temp_path


def copy_shell_profile_from_temp(temp_path: Path):
    """Copy .zprofile from the temporary dotdrop install to the user's home."""
    home = Path.home()
    src = temp_path / home.relative_to(home.anchor) / ".zprofile"
    dst = home / ".zprofile"
    shutil.copy2(src, dst)
    logger.debug(f"Copied {str(src)!r} -> {str(dst)!r}")


# === TARGETS ===


@target()
def setup_virtual_env():
    """Create and setup a virtual environment"""
    logger.info("⚙️ Create virtual environment if it doesn't exist...")

    if not VENV_DIR.exists():
        logger.info(f"🐍 Creating Python venv in {str(VENV_DIR)!r}...")
        run_command([PYTHON_BIN, "-m", "venv", str(VENV_DIR)])

    logger.info("♻️ Updating pip...")
    run_command([PIP_BIN, "install", "--upgrade", "pip"])

    logger.info("📦 Installing current project and dependencies...")
    run_command([PIP_BIN, "install", "-e", "."])


@target()
def install_system_packages():
    """Setup project and install dependencies"""
    logger.info("📦 Installing system packages...")

    system = sys.platform
    if system == "darwin" and shutil.which("brew") is None:
        logger.warning(
            "Homebrew is not installed. Please install it from https://brew.sh/"
        )
    elif system == "win32" and shutil.which("choco") is None:
        logger.warning(
            "Chocolatey is not installed. Please install it from https://chocolatey.org/install"
        )
    else:
        process_packages(packages)


@target()
def setup():
    install_system_packages()

    logger.info("⑂ Initializing git submodules...")
    init_submodules()

    setup_virtual_env()

    # playwright
    if shutil.which("playwright"):
        # We don't have any tests that require it at the moment
        # run_command(["playwright", "install"])
        pass
    else:
        logger.error("'playwright' not found. Skipping installation.")

    # npm
    logger.info("📦 Installing npm packages...")
    if shutil.which("npm"):
        run_command(["npm", "install"])
    else:
        logger.error("'npm' not found. Skipping installation.")

    # pre-commit
    logger.info("📦 Installing pre-commit hooks...")
    precommit_bin = VENV_BIN / "pre-commit"
    if precommit_bin.exists():
        # Install the standard commit hook
        run_command([str(precommit_bin), "install"])

        # Install the push hook (required for the UI tests)
        run_command([str(precommit_bin), "install", "--hook-type", "pre-push"])

        # Pre-install the environments so the first commit isn't slow
        run_command([str(precommit_bin), "install-hooks"])
    else:
        logger.error("'pre-commit' not found. Skipping installation.")


@target()
def install():
    """Install and apply configuration"""

    if not VENV_DIR.exists():
        logger.error(
            f"Missing venv at {str(VENV_DIR)!r}. Run the 'setup' target first."
        )
        return

    logger.info("⚙️ Generating shortcuts...")
    active_shortcuts = get_active_shortcuts()
    for renderer in AVAILABLE_RENDERERS:
        renderer.process(active_shortcuts)

    logger.info("⚙️ Installing configuration...")

    profile = get_dotdrop_profile()
    if not profile:
        return

    # We have 2 choices: either we first install profile that only contains the
    # shell profile, or we install the full profile to a temporary directory
    # and manually copy the shell config to the right place. The latter
    # has the advantage that we can set per-profile config in the shell config.
    temp_path = install_temp_profile()
    copy_shell_profile_from_temp(temp_path)

    # TODO: add windows and other shells support
    cmd = (
        f'zsh -c "source ~/.zprofile && '
        f"{VENV_BIN}/dotdrop compare --profile {profile!r} ; "
        f'{VENV_BIN}/dotdrop install --profile {profile!r}"'
    )
    try:
        subprocess.run(cmd, shell=True, check=True)
    except KeyboardInterrupt:
        sys.exit(0)

    # TODO: Apply macOS default here


@target()
def clean():
    """Remove caches and temporary files"""
    logger.info("🧹 Removing clean targets...")
    remove_files_by_pattern(
        patterns={
            ".mypy_cache",
            ".pytest_cache",
            ".ruff_cache",
            "__pycache__",
            "dist",
            "build",
            "*.egg-info",
            "node_modules",
            ".DS_Store",
        },
        global_excludes={".git", ".venv"},
    )

    remove_empty_dirs(
        global_excludes={".git", "__pycache__", "node_modules", ".venv"},
        protected_roots=None,
    )


@target()
def uninstall():
    """Clean project and remove flexycon's data"""
    clean()

    clean_precommit()

    logger.info("🔪 Removing uninstall targets...")
    remove_files_by_pattern(patterns={".venv"}, global_excludes={".git"})

    remove_flexycon_data()

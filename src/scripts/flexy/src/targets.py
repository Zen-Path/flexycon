import shutil
import subprocess
import sys

from common.cmd_utilities import run_cmd
from common.io_utilities import remove_empty_dirs, remove_files_by_pattern
from common.logger import log
from scripts.flexy.src.helpers import (
    PIP_BIN,
    PYTHON_BIN,
    VENV_BIN,
    VENV_DIR,
    clean_precommit,
    copy_dotfiles_from_temp,
    get_dotdrop_profile,
    init_submodules,
    install_dotfiles_to_temp,
    remove_flexycon_data,
    upgrade_yazi_packages,
)
from scripts.package_installer.data.packages import packages
from scripts.package_installer.main import process_packages
from scripts.user_shortcuts.main import AVAILABLE_RENDERERS, get_active_shortcuts


def setup_virtual_env():
    log.info("⚙️ Create virtual environment if it doesn't exist...")

    if not VENV_DIR.exists():
        log.info(f"🐍 Creating Python venv in {str(VENV_DIR)!r}...")
        run_cmd([PYTHON_BIN, "-m", "venv", str(VENV_DIR)])

    log.info("♻️ Updating pip...")
    run_cmd([PIP_BIN, "install", "--upgrade", "pip"])

    log.info("📦 Installing current project and dependencies...")
    run_cmd([PIP_BIN, "install", "-e", "."])


def install_system_packages():
    log.info("📦 Installing system packages...")

    system = sys.platform
    if system == "darwin" and shutil.which("brew") is None:
        log.warning(
            "Homebrew is not installed. Please install it from https://brew.sh/"
        )
    elif system == "win32" and shutil.which("choco") is None:
        log.warning(
            "Chocolatey is not installed. Please install it from https://chocolatey.org/install"
        )
    else:
        process_packages(packages)


def setup():
    install_system_packages()

    log.info("⑂ Initializing git submodules...")
    init_submodules()

    setup_virtual_env()

    # playwright
    if shutil.which("playwright"):
        # We don't have any tests that require it at the moment
        # run_command(["playwright", "install"])
        pass
    else:
        log.error("'playwright' not found. Skipping installation.")

    # npm
    log.info("📦 Installing npm packages...")
    if shutil.which("npm"):
        run_cmd(["npm", "install"])
    else:
        log.error("'npm' not found. Skipping installation.")

    # pre-commit
    log.info("📦 Installing pre-commit hooks...")
    precommit_bin = VENV_BIN / "pre-commit"
    if precommit_bin.exists():
        # Install the standard commit hook
        run_cmd([str(precommit_bin), "install"])

        # Install the push hook (required for the UI tests)
        run_cmd([str(precommit_bin), "install", "--hook-type", "pre-push"])

        # Pre-install the environments so the first commit isn't slow
        run_cmd([str(precommit_bin), "install-hooks"])
    else:
        log.error("'pre-commit' not found. Skipping installation.")

    upgrade_yazi_packages()


def install():
    if not VENV_DIR.exists():
        log.error(f"Missing venv at {str(VENV_DIR)!r}. Run the 'setup' target first.")
        return

    log.info("⚙️ Generating shortcuts...")
    active_shortcuts = get_active_shortcuts()
    for renderer in AVAILABLE_RENDERERS:
        renderer.process(active_shortcuts)

    log.info("⚙️ Installing configuration...")

    profile = get_dotdrop_profile()
    if not profile:
        return

    # We have 2 choices: either we first install profile that only contains the
    # shell profile, or we install the full profile to a temporary directory
    # and manually copy the shell config to the right place. The latter
    # has the advantage that we can set per-profile config in the shell config.
    temp_path = install_dotfiles_to_temp(profile)
    copy_dotfiles_from_temp(temp_path)

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


def clean():
    log.info("🧹 Removing clean targets...")
    remove_files_by_pattern(
        patterns={
            ".mypy_cache",
            ".pytest_cache",
            ".ruff_cache",
            "__pycache__",
            "dist",
            "build",
            "*.egg-info",
            "htmlcov",
            ".DS_Store",
        },
        global_excludes={
            ".git",
            ".venv",
            "node_modules",
            "deps",
        },
    )

    log.info("🧹 Removing empty directories...")
    remove_empty_dirs(
        global_excludes={
            ".git",
            ".venv",
            "__pycache__",
            "node_modules",
            "deps",
        },
        protected_roots=None,
    )


def uninstall():
    clean()

    clean_precommit()

    log.info("🔪 Removing uninstall targets...")
    remove_files_by_pattern(
        patterns={
            ".venv",
            "node_modules",
        },
        global_excludes={
            ".git",
        },
    )

    remove_flexycon_data()

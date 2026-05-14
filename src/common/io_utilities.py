import json
import os
import shutil
from pathlib import Path

from common.logger import logger
from common.prompt_utilities import prompt_bool


def write_to_file(content: str, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

    logger.debug(
        f"Wrote contents {content[:20].replace('\n', ' ')!r} to file {str(path)!r}"
    )


def load_json(path: Path) -> str | None:
    """Load a JSON file if it exists."""
    if not path.is_file():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(e)
        return None


def ensure_directory_interactive(path: Path) -> bool:
    """
    Interactively ensure all directories leading to the path exist.
    """
    # Check the directory part, since 'path' might be a file
    directory = path if path.suffix == "" else path.parent

    if directory.exists():
        return True

    logger.info(f"Directory {str(directory)!r} does not exist.")

    user_resp = prompt_bool("Create the directory?", default=True)

    if user_resp is True:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory!r}")
        return True
    else:
        logger.debug("Operation cancelled by user.")
        return False


def remove_files_by_pattern(
    patterns: set[str],
    base_dir: str | Path = ".",
    global_excludes: set[str] | None = None,
) -> None:
    """
    Recursively deletes files and directories matching glob patterns,
    unless they are part of a globally excluded directory tree.

    :param patterns: Set of glob patterns (e.g., {'*.tmp', 'build'}).
    :param base_dir: Root directory to start the search.
    :param global_excludes: Directory names to ignore anywhere in the path.
    """
    if global_excludes is None:
        global_excludes = set()

    base_path = Path(base_dir).resolve()

    for pattern in patterns:
        # rglob handles the recursion for the pattern matching
        for path in base_path.rglob(pattern):
            # Existence check (handles overlapping pattern matches)
            if not path.exists() and not path.is_symlink():
                continue

            # SKIP LOGIC: Check if any segment of the path is in global_excludes
            # This protects the folder itself and everything inside it.
            if any(part in global_excludes for part in path.parts):
                continue

            try:
                # DELETION LOGIC
                if path.is_dir() and not path.is_symlink():
                    shutil.rmtree(path)
                else:
                    # missing_ok=True handles race conditions
                    path.unlink(missing_ok=True)

                logger.debug(f"Removed {str(path)!r}")
            except Exception as e:
                logger.warning(f"Failed to remove {str(path)!r}: {e}")


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

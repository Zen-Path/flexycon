#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import random
import sys
from pathlib import Path

from common.helpers import NotificationSystem, get_version, set_wallpaper
from common.io_utilities import get_images_from_path
from common.logger import log, setup_logging
from common.variables import XDG_DATA_HOME

WALL_LINK = XDG_DATA_HOME / "bg"


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="wallpaper_setter",
        description="Set a specific or random wallpaper.",
    )

    parser.add_argument(
        "paths", nargs="*", type=Path, help="files or directories to pick from"
    )
    parser.add_argument(
        "--no-notify",
        dest="notify",
        action="store_false",
        default=True,
        help="do not notify user of updated wallpaper",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    return parser


def main():
    args = build_parser().parse_args()

    setup_logging(log, logging.DEBUG if args.verbose else logging.ERROR)
    log.debug(args)

    # Resolve current wallpaper
    current_wall: Path | None = None
    if WALL_LINK.exists() and WALL_LINK.is_file(follow_symlinks=True):
        current_wall = WALL_LINK.resolve()
        log.debug(f"Current wallpaper: {str(current_wall)!r}")

    # Determine candidate pool
    candidates: list[Path] = []
    if args.paths:
        for p in args.paths:
            candidates.extend(get_images_from_path(p))
    elif current_wall:
        candidates = [current_wall]

    if not candidates:
        log_msg = "No valid images found."
        log.error(log_msg)

        if args.notify:
            NotificationSystem.run("❌ Wallpaper Error", log_msg)

        sys.exit(1)

    # If multiple candidates, pick a wallpaper that is different from the current one
    if len(candidates) > 1 and current_wall:
        available = [c for c in candidates if c.resolve() != current_wall]
        if available:
            candidates = available

    chosen = random.choice(candidates)

    # Update the symlink
    try:
        WALL_LINK.parent.mkdir(parents=True, exist_ok=True)
        if WALL_LINK.exists() or WALL_LINK.is_symlink():
            WALL_LINK.unlink()
        WALL_LINK.symlink_to(chosen)
    except OSError as e:
        log.warning(f"Could not update symlink: {e}")

    if set_wallpaper(chosen):
        log_msg = f"Wallpaper set to {str(chosen)!r}"
        log.info(log_msg)

        if args.notify:
            NotificationSystem.run(
                title="🏞️ Wallpaper Updated",
                message=log_msg,
                icon_path=chosen,
                open_image_onclick=True,
            )
    else:
        log_msg = f"Failed to set wallpaper to {str(chosen)!r}"
        log.error(log_msg)

        if args.notify:
            NotificationSystem.run("❌ Wallpaper Error", log_msg)


if __name__ == "__main__":
    main()

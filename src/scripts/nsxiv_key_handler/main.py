#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import sys
from functools import partial
from pathlib import Path

from common.helpers import get_version
from common.logger import log, setup_logging
from scripts.nsxiv_key_handler.src.core import (
    Action,
    ActionsMap,
    a_copy_file,
    a_copy_file_paths,
    a_flip_images,
    a_get_file_info,
    a_group_files,
    a_open_images_in_editor,
    a_open_in_new_windows,
    a_rotate_images,
    a_set_images_as_wallpaper,
    a_show_help,
    a_trash_files,
    a_trash_files_interactive,
    get_help_text,
)

ACTIONS: ActionsMap = {
    "d": Action(
        description="trash files (interactive)",
        fn=a_trash_files_interactive,
    ),
    "D": Action(
        description="trash files (non-interactive)",
        fn=a_trash_files,
    ),
    "e": Action(
        description="open images in editor",
        fn=a_open_images_in_editor,
    ),
    "f": Action(
        description="flip image",
        fn=a_flip_images,
    ),
    "g": Action(
        description="group files",
        fn=a_group_files,
    ),
    "i": Action(
        description="get file info",
        fn=a_get_file_info,
    ),
    "o": Action(
        description="open in new windows",
        fn=a_open_in_new_windows,
    ),
    "r": Action(
        description="rotate images by 90 deg clockwise",
        fn=partial(a_rotate_images, degrees=90),
    ),
    "R": Action(
        description="rotate images by 90 deg counterclockwise",
        fn=partial(a_rotate_images, degrees=-90),
    ),
    "w": Action(
        description="set images as the wallpaper",
        fn=a_set_images_as_wallpaper,
    ),
    "y": Action(
        description="copy file to clipboard",
        fn=a_copy_file,
    ),
    "Y": Action(
        description="copy file paths to clipboard",
        fn=a_copy_file_paths,
    ),
}

ACTIONS["h"] = Action(
    description="show help text",
    fn=partial(a_show_help, actions_map=ACTIONS),
)


def build_parser(actions_map: ActionsMap) -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="nsxiv_key_handler",
        description="Key handler for nsixv.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "action",
        choices=sorted(actions_map.keys(), key=str.lower),
        help="action to perform:\n" + get_help_text(actions_map),
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    return parser


def main() -> None:
    args = build_parser(ACTIONS).parse_args()

    setup_logging(log, logging.DEBUG if args.verbose else logging.WARNING)
    log.debug(args)

    # Read filenames from stdin
    files = [Path(line.strip()) for line in sys.stdin if line.strip()]
    if not files:
        log.error("No files given on stdin.")
        sys.exit(1)

    action = ACTIONS[args.action]
    log.info(f"Action: {action}")

    action.fn(files)


if __name__ == "__main__":
    main()

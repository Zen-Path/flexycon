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
    action_copy_image,
    action_copy_path,
    action_flip,
    action_get_info,
    action_group,
    action_interactive_trash,
    action_open_editor,
    action_open_in_new_windows,
    action_rotate,
    action_show_help,
    action_trash,
    action_update_wallpaper,
    get_help_text,
)

ACTIONS: ActionsMap = {
    "d": Action(
        description="interactive trash",
        fn=action_interactive_trash,
    ),
    "D": Action(
        description="non-interactive trash",
        fn=action_trash,
    ),
    "e": Action(
        description="open image editor",
        fn=action_open_editor,
    ),
    "f": Action(
        description="flip image",
        fn=action_flip,
    ),
    "g": Action(
        description="group photos",
        fn=action_group,
    ),
    "i": Action(
        description="get media info",
        fn=action_get_info,
    ),
    "o": Action(
        description="open in new windows",
        fn=action_open_in_new_windows,
    ),
    "r": Action(
        description="rotate by 90 deg clockwise",
        fn=partial(action_rotate, degrees=90),
    ),
    "R": Action(
        description="rotate by 90 deg counterclockwise",
        fn=partial(action_rotate, degrees=-90),
    ),
    "w": Action(
        description="set the image as the wallpaper",
        fn=action_update_wallpaper,
    ),
    "y": Action(
        description="copy image to clipboard",
        fn=action_copy_image,
    ),
    "Y": Action(
        description="copy path to clipboard",
        fn=action_copy_path,
    ),
}

ACTIONS["h"] = Action(
    description="show help text",
    fn=partial(action_show_help, actions_map=ACTIONS),
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

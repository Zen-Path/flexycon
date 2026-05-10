#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
from pathlib import Path
from typing import TypedDict

from common.helpers import Dmenu, PromptOption, ScreenshotUtility, get_version
from common.logger import logger, setup_logging


class ScreenshotOptions(TypedDict):
    output_dir: Path | None
    copy_output: bool


def prompt_user(options: list[PromptOption]) -> str | int | None:
    # Create a mapping of "Displayed String" -> "Original ID"
    lookup = {opt.display_text(): opt.id for opt in options}

    display_list = list(lookup.keys())
    choice = Dmenu.run(
        prompt="Screenshot", choices=display_list, list_view_item_count=-1
    )

    return lookup.get(choice)


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""
    global_parent = argparse.ArgumentParser(add_help=False)
    global_parent.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )

    parser = argparse.ArgumentParser(
        prog="screenshot_utility",
        description="Screenshot Utility",
        parents=[global_parent],
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    # SUBCOMMANDS
    cmd_parent = argparse.ArgumentParser(add_help=False)
    cmd_parent.add_argument(
        "--no-copy",
        dest="copy_output",
        action="store_false",
        default=True,
        help="do not copy screenshot to clipboard",
    )
    cmd_parent.add_argument("-d", "--output-directory", type=Path)

    subparsers = parser.add_subparsers(dest="action_id", help="Actions")

    subparsers.add_parser(
        "area", parents=[cmd_parent, global_parent], help="Capture area"
    )

    window_p = subparsers.add_parser(
        "window", parents=[cmd_parent, global_parent], help="Capture window"
    )
    window_p.add_argument("-w", "--window-id", type=int)
    window_p.add_argument(
        "--no-include-name",
        dest="include_name",
        action="store_false",
        default=True,
        help="do not include window name in file name",
    )

    screen_p = subparsers.add_parser(
        "screen", parents=[cmd_parent, global_parent], help="Capture screen"
    )
    screen_p.add_argument("-s", "--screen-id", type=int)

    subparsers.add_parser(
        "full", parents=[cmd_parent, global_parent], help="Capture all"
    )

    return parser


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.WARNING)
    logger.debug(args)

    common: ScreenshotOptions = {
        "output_dir": (
            Path(getattr(args, "output_directory"))
            if hasattr(args, "output_directory")
            else None
        ),
        "copy_output": getattr(args, "copy_output", True),
    }

    options = [
        PromptOption("area", "Area", "🔳", lambda: ScreenshotUtility.area(**common)),
        PromptOption(
            "window",
            "Window",
            "🪟",
            lambda: ScreenshotUtility.window(
                window=getattr(args, "window_id", None),
                include_window_name=getattr(args, "include_name", True),
                **common,
            ),
        ),
        PromptOption(
            "screen",
            "Screen",
            "🖥️",
            lambda: ScreenshotUtility.screen(
                screen=getattr(args, "screen_id", None), **common
            ),
        ),
        PromptOption(
            "full", "Full Screen", "🌍", lambda: ScreenshotUtility.full_screen(**common)
        ),
    ]

    action_id = args.action_id or prompt_user(options)

    if not action_id:
        logger.debug("No action was chosen.")
        return

    selected = next((opt for opt in options if opt.id == action_id), None)

    if selected and selected.action:
        logger.debug(f"Executing action {selected.id!r}.")
        selected.action()
    else:
        logger.error(f"Unknown action {action_id!r}.")


if __name__ == "__main__":
    main()

#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
from pathlib import Path

from common.helpers import Dmenu, PromptOption, ScreenshotUtility, get_version
from common.logger import logger, setup_logging


def prompt_user(options: list[PromptOption]) -> str | int | None:
    # Create a mapping of "Displayed String" -> "Original ID"
    lookup = {opt.display_text(): opt.id for opt in options}

    display_list = list(lookup.keys())
    choice = Dmenu.run(
        prompt="Screenshot", choices=display_list, list_view_item_count=-1
    )

    return lookup.get(choice)


def build_parser():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Screenshot Utility")

    # Create subparsers for actions
    subparsers = parser.add_subparsers(dest="action", help="Screenshot action")

    # Area action
    subparsers.add_parser("area", help="Capture a selected area")

    # Window action
    window_parser = subparsers.add_parser(
        "window", help="Capture the active or specified window"
    )
    window_parser.add_argument(
        "-w", "--window-id", type=int, help="Specify a window ID"
    )
    window_parser.add_argument(
        "-n",
        "--include-name",
        action="store_true",
        help="Include window name in the file name",
    )

    # Screen action
    screen_parser = subparsers.add_parser(
        "screen", help="Capture the active or specified screen"
    )
    screen_parser.add_argument(
        "-s", "--screen-id", type=int, help="Specify the screen ID"
    )

    # Full action
    subparsers.add_parser("full", help="Capture all screens")

    # Global options
    parser.add_argument(
        "--no-copy",
        dest="copy_output",
        action="store_false",
        default=True,
        help="Do not copy the screenshot to the clipboard",
    )

    parser.add_argument(
        "-d",
        "--output-directory",
        type=Path,
        default=None,
        help="Set the output directory for screenshots",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    return parser


ACTIONS = [
    PromptOption("area", "Area", "🔳"),
    PromptOption("window", "Window", "🪟"),
    PromptOption("screen", "Screen", "🖥️"),
    PromptOption("full", "Full Screen", "🌍"),
]


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.WARNING)

    action = args.action or prompt_user(ACTIONS)

    if not action:
        return

    common = {"output_dir": args.output_directory, "copy_output": args.copy_output}

    match action:
        case "area":
            ScreenshotUtility.area(**common)
        case "window":
            ScreenshotUtility.window(
                window=args.window_id,
                include_window_name=args.include_name,
                **common,
            )
        case "screen":
            ScreenshotUtility.screen(screen=args.screen_id, **common)
        case "full":
            ScreenshotUtility.full_screen(**common)
        case _:
            raise ValueError(f"Unknown action: {args.action}")


if __name__ == "__main__":
    main()

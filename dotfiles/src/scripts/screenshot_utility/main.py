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

    subparsers = parser.add_subparsers(dest="action", help="Actions")

    area_p = subparsers.add_parser("area", help="Capture area")

    window_p = subparsers.add_parser("window", help="Capture window")
    window_p.add_argument("-w", "--window-id", type=int)
    window_p.add_argument(
        "--no-include-name",
        dest="include_name",
        action="store_false",
        default=True,
        help="do not include window name in file name",
    )

    screen_p = subparsers.add_parser("screen", help="Capture screen")
    screen_p.add_argument("-s", "--screen-id", type=int)

    full_p = subparsers.add_parser("full", help="Capture all")

    for sp in [area_p, window_p, screen_p, full_p]:
        sp.add_argument(
            "--no-copy",
            dest="copy_output",
            action="store_false",
            default=True,
            help="do not copy screenshot to clipboard",
        )
        sp.add_argument("-d", "--output-directory", type=Path)

        sp.add_argument(
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

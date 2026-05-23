#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import sys

from common.helpers import get_version
from common.logger import log, setup_logging
from scripts.keyboard_manager.data.layouts import KB_LAYOUTS_FULL_NAME
from scripts.keyboard_manager.src.core import (
    get_available_layouts,
    get_current_layout,
    prompt_layout,
    restart_remapd,
    set_keymap_layout,
)


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="keyboard_manager",
        description="Manage keyboard and select layout.",
    )

    parser.add_argument(
        "-c",
        "--current-layout",
        action="store_true",
        help="fetch current keymap layout",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    return parser


def main() -> None:
    args = build_parser().parse_args()

    setup_logging(log, logging.DEBUG if args.verbose else logging.INFO)
    log.debug(args)

    current_layout = get_current_layout()
    if args.current_layout:
        if current_layout:
            print(f"⌨ {current_layout}")
        else:
            print("⌨ Unknown")
        return

    available_layouts = get_available_layouts()
    if not available_layouts:
        sys.exit(1)

    layout_code = prompt_layout(available_layouts, KB_LAYOUTS_FULL_NAME, current_layout)
    if not layout_code:
        log.warning("Missing or invalid layout.")
        sys.exit(1)

    if not set_keymap_layout(layout_code):
        log.error("Could not set keymap layout.")
        sys.exit(1)

    log.info(f"Keymap layout set to {layout_code!r}.")

    if sys.platform == "linux":
        restart_remapd()


if __name__ == "__main__":
    main()

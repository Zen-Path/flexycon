#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import sys

from common.helpers import get_version
from common.logger import logger, setup_logging
from scripts.keyboard_manager.data.layouts import KB_LAYOUTS_FULL_NAME
from scripts.keyboard_manager.src.core import (
    format_layouts,
    get_available_layouts,
    get_current_layout,
    prompt_layout,
    restart_remapd,
    set_keyboard_layout,
)


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="keyboard_manager",
        description="Manage keyboard and select layout.",
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

    setup_logging(logger, logging.DEBUG if args.verbose else logging.INFO)
    logger.debug(args)

    available_layouts = get_available_layouts()
    if not available_layouts:
        sys.exit(1)

    current_layout = get_current_layout()
    formatted_layouts = format_layouts(available_layouts, KB_LAYOUTS_FULL_NAME)

    prompt_result = prompt_layout(formatted_layouts, current_layout)
    if not prompt_result:
        logger.warning("No layout chosen.")
        sys.exit(1)

    _idx, layout = prompt_result

    layout_code = layout.split(" - ")[0]
    if layout_code not in available_layouts:
        logger.error(f"Invalid layout selected {layout_code!r}.")
        sys.exit(1)

    if not set_keyboard_layout(layout_code):
        logger.error("Could not set keyboard layout.")
        sys.exit(1)

    logger.info(f"Keyboard layout set to {layout_code!r}.")

    if sys.platform == "linux":
        restart_remapd()


if __name__ == "__main__":
    main()

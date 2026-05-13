#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import shutil
import subprocess
import sys

from common.cmd_utilities import run_cmd
from common.helpers import NotificationSystem, get_version
from common.logger import logger, setup_logging
from common.prompt_utilities import prompt_options

# Map of keyboard layouts with their full names
layout_full_names = {
    "us": "English (US)",
    "ro": "Romanian",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "it": "Italian",
    "cz": "Czech",
    "ca": "Canadian",
    # Add more layouts as needed
}


def get_current_layout() -> str | None:
    """Fetch the current keyboard layout."""
    try:
        result = run_cmd(["setxkbmap", "-query"])
        for line in result.output.splitlines():
            if line.startswith("layout:"):
                return line.split()[1]

    except subprocess.CalledProcessError:
        logger.error("Unable to get current layout.")

    return None


def get_available_layouts() -> list[str] | None:
    """Get the available keyboard layouts using localectl."""
    try:
        result = run_cmd(["localectl", "list-x11-keymap-layouts"])
        return result.output.splitlines()

    except subprocess.CalledProcessError:
        logger.error("Unable to list x11 keymap layouts.")

    return None


def format_layouts(
    available_layouts: list[str], layout_full_names: dict[str, str]
) -> list[str]:
    """Combine the shorthand and long names if available."""
    formatted_layouts: list[str] = []
    for layout in available_layouts:
        if layout in layout_full_names:
            formatted_layouts.append(f"{layout} - {layout_full_names[layout]}")
        else:
            formatted_layouts.append(layout)

    return formatted_layouts


def prompt_layout(
    formatted_layouts: list[str], current_layout: str | None
) -> tuple[int, str] | None:
    """Prompt the user to select a layout, displaying the current layout."""
    current_layout_fmt = f" (current: {current_layout})" if current_layout else ""
    return prompt_options(
        prompt=f"Select Keyboard Layout{current_layout_fmt}",
        options=formatted_layouts,
        list_view_item_count=15,
    )


def restart_remapd() -> bool:
    """Restart the remapd service if it's available."""
    if not shutil.which("remapd"):
        logger.error("Binary 'remapd' not found.")
        return False

    try:
        run_cmd(["killall", "remapd"])
        logger.debug("Killed 'remapd'.")

        subprocess.Popen(["remapd"])
        logger.debug("Restarted 'remapd'.")
        return True

    except Exception as e:
        logger.error(f"Failed to restart 'remapd': {e}")

    return False


def set_keyboard_layout(layout: str) -> bool:
    """Set the chosen keyboard layout."""
    try:
        result = run_cmd(["setxkbmap", layout]).success
        if result:
            NotificationSystem.run(f"Keyboard layout changed to {layout!r}")
        return result

    except subprocess.CalledProcessError:
        logger.error(f"Unable to set layout to {layout!r}.")

    return False


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="keyboard_selector",
        description="Select keyboard layout.",
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
    formatted_layouts = format_layouts(available_layouts, layout_full_names)

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
    restart_remapd()  # Call restart_remapd from here


if __name__ == "__main__":
    main()

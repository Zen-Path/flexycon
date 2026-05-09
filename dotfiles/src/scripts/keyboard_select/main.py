#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import shutil
import subprocess
import sys

from common.helpers import Dmenu, NotificationSystem, get_version, run_command
from common.logger import logger, setup_logging

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


def get_current_layout():
    """Fetch the current keyboard layout."""
    try:
        result = run_command(["setxkbmap", "-query"])
        for line in result.output.splitlines():
            if line.startswith("layout:"):
                return line.split()[1]
    except subprocess.CalledProcessError:
        logger.error("Unable to get current layout.")
        sys.exit(1)


def get_available_layouts():
    """Get the available keyboard layouts using localectl."""
    try:
        result = run_command(
            ["localectl", "list-x11-keymap-layouts"],
        )
        layouts = result.output.splitlines()
        return layouts
    except subprocess.CalledProcessError:
        logger.error("Unable to list x11 keymap layouts.")
        sys.exit(1)


def format_layouts(available_layouts, layout_full_names):
    """Combine the shorthand and long names if available."""
    formatted_layouts = []
    for layout in available_layouts:
        if layout in layout_full_names:
            formatted_layouts.append(f"{layout} - {layout_full_names[layout]}")
        else:
            formatted_layouts.append(layout)
    return formatted_layouts


def prompt_layout(formatted_layouts, current_layout):
    """Prompt the user to select a layout, displaying the current layout."""
    try:
        return Dmenu.run(
            prompt=f"Select Keyboard Layout (current: {current_layout})",
            choices=formatted_layouts,
            list_view_item_count=15,
        )
    except subprocess.CalledProcessError:
        logger.error("dmenu failed to run.")
        sys.exit(1)


def restart_remapd():
    """Restart the remapd service if it's available."""
    if shutil.which("remapd"):
        try:
            run_command(["killall", "remapd"])
            logger.debug("remapd killed successfully.")
            # Restart remapd if necessary (customize based on how you restart it)
            subprocess.Popen(["remapd"])
            logger.debug("remapd restarted successfully.")
        except subprocess.CalledProcessError:
            logger.error("Failed to restart remapd.")
    else:
        logger.error("remapd is not available in this environment.")


def set_keyboard_layout(layout):
    """Set the chosen keyboard layout."""
    try:
        run_command(["setxkbmap", layout])
        NotificationSystem.run(f"Keyboard layout changed to {layout!r}")
    except subprocess.CalledProcessError:
        logger.error(f"Unable to set layout to {layout!r}.")
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="keyboard_selector", description="Select keyboard layout."
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

    setup_logging(logger, logging.DEBUG if args.verbose else logging.INFO)

    current_layout = get_current_layout()
    available_layouts = get_available_layouts()

    formatted_layouts = format_layouts(available_layouts, layout_full_names)
    chosen_layout = prompt_layout(formatted_layouts, current_layout)

    if chosen_layout:
        layout_code = chosen_layout.split(" - ")[0]
        if layout_code in available_layouts:
            set_keyboard_layout(layout_code)
            logger.info(f"Keyboard layout set to {layout_code!r}.")
            restart_remapd()  # Call restart_remapd from here
        else:
            logger.error("Invalid layout selected.")
    else:
        logger.warning("No layout chosen.")


if __name__ == "__main__":
    main()

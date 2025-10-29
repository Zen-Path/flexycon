#!/usr/bin/env python3

import argparse
import logging
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from common.helpers import notify, run_command
from common.logger import logger, setup_logging
from common.packages.clipboard_utilities import XClip


def prompt_dmenu(prompt: str, options: Optional[list[str]] = None) -> Optional[str]:
    result = subprocess.run(
        ["dmenu", "-i", "-p", prompt],
        input="\n".join(options if options else []),
        capture_output=True,
        text=True,
    ).stdout.strip()
    return result


def get_help_text():
    return ";\n".join(
        f"{k}: {v['desc']}"
        for k, v in sorted(ACTIONS.items(), key=lambda item: item[0].lower())
    )


def action_interactive_trash(paths):
    for path in paths:
        choice = prompt_dmenu(f"Really trash '{path}'?", ["Yes", "No", "Cancel"])

        if choice == "Cancel":
            break

        if choice == "Yes":
            run_command(["trash-put", str(path)])
            notify("Trash complete", f"{path} trashed.")


def action_trash(paths):
    run_command(["trash-put", *[str(path) for path in paths]])


def action_open_editor(paths):
    if shutil.which("gimp"):
        run_command(["gimp", str(path)])


def action_flip(paths):
    for path in paths:
        run_command(["magick", str(path), "-flop", str(path)])


def action_group(paths):
    default_name = datetime.now().strftime("%F_%T")
    choice = prompt_dmenu("Group file(s) where?", [default_name])
    if not choice:
        notify("No directory entered, cancelled.")
        sys.exit(1)

    destdir = Path.cwd() / choice
    destdir.mkdir(parents=True, exist_ok=True)
    notify("Directory created", f"Located at '{destdir}'")

    for path in paths:
        shutil.move(path, destdir)

    if len(paths) == 1:
        notify(
            "Move complete",
            f"{paths[0].name} moved to {destdir.parent}.",
            icon=str(Path(destdir, paths[0].name)),
        )


def action_show_help(paths):
    notify("nsxiv actions", get_help_text())


def action_get_info(paths):
    mediainfo = run_command(["mediainfo", str(paths[0])]).output
    formatted = []
    for line in mediainfo.splitlines():
        line = line.replace(":", ": <b>", 1) + "</b>"
        formatted.append(line)
    notify("File information", "\n".join(formatted))


def action_rotate(paths, degrees: int = 90):
    for path in paths:
        run_command(["magick", str(path), "-rotate", str(degrees), str(path)])


def action_update_wallpaper(paths):
    result = run_command(["setbg", str(paths[0])])


def action_copy_image(paths):
    XClip.file(str(paths[0]))
    notify("Image copied", f"Image {paths[0]} copied to clipboard")


def action_copy_path(paths):
    XClip.text(str(paths[0]))
    notify("Path copied", f"Path {paths[0]} copied to clipboard")


ACTIONS = {
    "d": {
        "desc": "Interactive trash",
        "func": action_interactive_trash,
    },
    "D": {
        "desc": "Non-interactive trash",
        "func": action_trash,
    },
    "e": {
        "desc": "Open image editor",
        "func": action_open_editor,
    },
    "f": {
        "desc": "Flip",
        "func": action_flip,
    },
    "g": {
        "desc": "Group photos",
        "func": action_group,
    },
    "h": {
        "desc": "Show help text",
        "func": action_show_help,
    },
    "i": {
        "desc": "Get media info",
        "func": action_get_info,
    },
    "r": {
        "desc": "Rotate by 90 deg clockwise",
        "func": lambda paths: action_rotate(paths, degrees=90),
    },
    "R": {
        "desc": "Rotate by 90 deg counterclockwise",
        "func": lambda paths: action_rotate(paths, degrees=-90),
    },
    "w": {
        "desc": "Set the image as the wallpaper",
        "func": action_update_wallpaper,
    },
    "y": {
        "desc": "Copy image to clipboard",
        "func": action_copy_image,
    },
    "Y": {
        "desc": "Copy path to clipboard",
        "func": action_copy_path,
    },
}


def build_parser():
    parser = argparse.ArgumentParser(description="Key handler for nsixv.")

    parser.add_argument(
        "action",
        choices=sorted(ACTIONS.keys(), key=str.lower),
        help="action to perform. " + get_help_text(),
    )
    parser.add_argument("--verbose", action="store_true", help="enable debug output")

    return parser


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.WARNING)

    # Read filenames from stdin
    files = [Path(line.strip()) for line in sys.stdin if line.strip()]
    if not files:
        logger.error("No files given on stdin.")
        sys.exit(1)

    action = ACTIONS[args.action]
    logger.info(f"Action: {action}")
    action["func"](files)


if __name__ == "__main__":
    main()

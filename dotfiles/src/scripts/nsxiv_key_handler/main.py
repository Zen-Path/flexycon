#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

from common.helpers import (
    Dmenu,
    NotificationSystem,
    run_command,
    run_command_background,
)
from common.logger import logger, setup_logging
from common.packages.clipboard_utilities import copy_file, copy_text


def get_help_text():
    return ";\n".join(
        f"{k}: {v['desc']}"
        for k, v in sorted(ACTIONS.items(), key=lambda item: item[0].lower())
    )


def action_interactive_trash(paths: list[Path]):
    for path in paths:
        choice = Dmenu.run(
            prompt=f"Confirm trash {str(path)!r}?", choices=["Yes", "No", "Cancel"]
        ).lower()

        if choice == "yes":
            run_command(["trash-put", str(path)])
            NotificationSystem.run("File trashed", f"Trashed {str(path)!r}.")

        elif choice == "cancel":
            break


def action_trash(paths: list[Path]):
    run_command(["trash-put", *[str(path) for path in paths]])


def action_open_editor(paths: list[Path]):
    if shutil.which("gimp"):
        run_command_background(["gimp", *[str(path) for path in paths]])


def action_flip(paths: list[Path]):
    for path in paths:
        run_command(["magick", str(path), "-flop", str(path)])


def action_group(paths: list[Path]):
    default_name = datetime.now().strftime("%F_%T")
    choice = Dmenu.run(prompt="Group file(s) where?", choices=[default_name])
    if not choice:
        NotificationSystem.run("No directory entered, cancelled.")
        return

    destdir = Path.cwd() / choice
    destdir.mkdir(parents=True, exist_ok=True)
    NotificationSystem.run("Directory created", f"Located at {str(destdir)}")

    for path in paths:
        shutil.move(path, destdir)

    if len(paths) == 1:
        NotificationSystem.run(
            "Move complete",
            f"{paths[0].name} moved to {destdir.parent}.",
            icon_path=Path(destdir, paths[0].name),
            open_image_onclick=True,
        )


def action_show_help(paths: list[Path]):
    NotificationSystem.run("nsxiv actions", get_help_text())


def action_get_info(paths):
    mediainfo = run_command(["mediainfo", str(paths[0])]).output
    formatted = []
    for line in mediainfo.splitlines():
        line = line.replace(":", ": <b>", 1) + "</b>"
        formatted.append(line)
    NotificationSystem.run("File information", "\n".join(formatted))


def action_rotate(paths: list[Path], degrees: int = 90):
    for path in paths:
        run_command(["magick", str(path), "-rotate", str(degrees), str(path)])


def action_update_wallpaper(paths: list[Path]):
    run_command(["setbg", str(paths[0])])


def action_copy_image(paths: list[Path]):
    copy_file(paths[0])
    NotificationSystem.run("Image copied", f"Image {paths[0]} copied to clipboard")


def action_copy_path(paths: list[Path]):
    copy_text(str(paths[0]))
    NotificationSystem.run("Path copied", f"Path {paths[0]} copied to clipboard")


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

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )

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

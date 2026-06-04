#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable, TypedDict

from common.clipboard_utilities import ClipboardManager
from common.cmd_utilities import run_cmd, run_cmd_background
from common.helpers import get_version
from common.logger import log, setup_logging
from common.media import flip_image
from common.notification_utilities import Notification
from common.prompt_utilities import prompt_options

ActionFunc = Callable[[list[Path]], None]


class Action(TypedDict):
    desc: str
    func: ActionFunc


def get_help_text():
    return "\n".join(
        f"{k} - {v['desc']}"
        for k, v in sorted(ACTIONS.items(), key=lambda item: item[0].lower())
    )


def action_interactive_trash(paths: list[Path]):
    for path in paths:
        choice = prompt_options(
            prompt=f"Confirm trash {str(path)!r}?", options=["Yes", "No", "Cancel"]
        )

        if choice is None:
            continue

        choice = choice.lower()

        if choice == "cancel":
            break

        if choice == "yes":
            run_cmd(["trash-put", path])
            Notification("File trashed", f"Trashed {str(path)!r}.").send()


def action_trash(paths: list[Path]):
    run_cmd(["trash-put", *paths])


def action_open_editor(paths: list[Path]):
    if shutil.which("gimp"):
        run_cmd_background(["gimp", *paths])


def action_flip(paths: list[Path]):
    for path in paths:
        flip_image(path)


def action_group(paths: list[Path]):
    current_dirs = [str(p.name) for p in Path(".").iterdir() if p.is_dir()]
    temp_dir = f"temp_{datetime.now().strftime('%F_%T')}"
    options = [temp_dir] + current_dirs + ["Cancel"]

    choice = prompt_options(
        prompt="Group file(s) where?", options=options, default=temp_dir
    )

    if not choice or choice.lower() == "cancel":
        log.error("Could not group files due to empty selection.")
        Notification("❌ File Grouping", "Operation cancelled.").send()
        return

    destdir = Path.cwd() / choice
    if not destdir.exists():
        destdir.mkdir(parents=True, exist_ok=True)
        Notification("File Grouping", f"Created directory {str(destdir)}").send()

    for path in paths:
        shutil.move(path, destdir)

    notification = Notification("File Grouping")
    if len(paths) == 1:
        notification.message = f"File {paths[0].name!r} moved to {str(destdir)!r}."
    else:
        notification.message = f"Moved {len(paths)} files to {str(destdir)!r}."

    notification.send(icon_path=destdir / paths[0].name, open_image_onclick=True)


def action_show_help(paths: list[Path]):
    Notification("nsxiv actions", get_help_text()).send()


def action_get_info(paths: list[Path]):
    mediainfo = run_cmd(["mediainfo", paths[0]]).output
    formatted: list[str] = []
    for line in mediainfo.splitlines():
        line = line.replace(":", ": <b>", 1) + "</b>"
        formatted.append(line)
    Notification("File information", "\n".join(formatted)).send()


def action_open_in_new_windows(paths: list[Path]):
    opener = "xdg-open" if sys.platform == "linux" else "open"
    for path in paths:
        run_cmd([opener, path])


def action_rotate(paths: list[Path], degrees: int = 90):
    for path in paths:
        run_cmd(["magick", path, "-rotate", degrees, path])


def action_update_wallpaper(paths: list[Path]):
    run_cmd(["wallpaper_setter", paths[0]])


def action_copy_image(paths: list[Path]):
    ClipboardManager.copy_file(paths[0])
    Notification("Image copied", f"Image {paths[0]} copied to clipboard").send()


def action_copy_path(paths: list[Path]):
    ClipboardManager.copy_text(str(paths[0]))
    Notification("Path copied", f"Path {paths[0]} copied to clipboard").send()


ACTIONS: dict[str, Action] = {
    "d": {
        "desc": "interactive trash",
        "func": action_interactive_trash,
    },
    "D": {
        "desc": "non-interactive trash",
        "func": action_trash,
    },
    "e": {
        "desc": "open image editor",
        "func": action_open_editor,
    },
    "f": {
        "desc": "flip image",
        "func": action_flip,
    },
    "g": {
        "desc": "group photos",
        "func": action_group,
    },
    "h": {
        "desc": "show help text",
        "func": action_show_help,
    },
    "i": {
        "desc": "get media info",
        "func": action_get_info,
    },
    "o": {
        "desc": "open in new windows",
        "func": action_open_in_new_windows,
    },
    "r": {
        "desc": "rotate by 90 deg clockwise",
        "func": lambda paths: action_rotate(paths, degrees=90),
    },
    "R": {
        "desc": "rotate by 90 deg counterclockwise",
        "func": lambda paths: action_rotate(paths, degrees=-90),
    },
    "w": {
        "desc": "set the image as the wallpaper",
        "func": action_update_wallpaper,
    },
    "y": {
        "desc": "copy image to clipboard",
        "func": action_copy_image,
    },
    "Y": {
        "desc": "copy path to clipboard",
        "func": action_copy_path,
    },
}


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="nsxiv_key_handler",
        description="Key handler for nsixv.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "action",
        choices=sorted(ACTIONS.keys(), key=str.lower),
        help="action to perform:\n" + get_help_text(),
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

    setup_logging(log, logging.DEBUG if args.verbose else logging.WARNING)
    log.debug(args)

    # Read filenames from stdin
    files = [Path(line.strip()) for line in sys.stdin if line.strip()]
    if not files:
        log.error("No files given on stdin.")
        sys.exit(1)

    action = ACTIONS[args.action]
    log.info(f"Action: {action}")
    action["func"](files)


if __name__ == "__main__":
    main()

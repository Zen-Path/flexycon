import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable, NamedTuple

from common.clipboard_utilities import ClipboardManager
from common.cmd_utilities import run_cmd, run_cmd_background
from common.logger import log
from common.media import flip_image
from common.notification_utilities import Notification
from common.prompt_utilities import prompt_options


class Action(NamedTuple):
    description: str
    fn: Callable[[list[Path]], bool]


ActionsMap = dict[str, Action]


def get_help_text(actions_map: ActionsMap) -> str:
    return "\n".join(
        f"{k} - {v.description}"
        for k, v in sorted(actions_map.items(), key=lambda item: item[0].lower())
    )


# ACTIONS


def action_copy_image(paths: list[Path]) -> bool:
    result = ClipboardManager.copy_file(paths[0])
    Notification("Image copied", f"Image {paths[0]} copied to clipboard").send()

    return result


def action_copy_paths(paths: list[Path]) -> bool:
    paths_str = "\n".join([str(path) for path in paths])
    result = ClipboardManager.copy_text(paths_str)

    if len(paths) == 1:
        Notification(
            "Path copied", f"Copied path {str(paths[0])!r} to clipboard"
        ).send()
    else:
        Notification("Paths copied", f"Copied {len(paths)} paths to clipboard").send()

    return result


def action_flip(paths: list[Path]) -> bool:
    for path in paths:
        flip_image(path)
    return True


def action_get_info(paths: list[Path]) -> bool:
    cmd_result = run_cmd(["mediainfo", paths[0]])

    if not cmd_result.success:
        return False

    formatted: list[str] = []
    for line in cmd_result.output.splitlines():
        line = line.replace(":", ": <b>", 1) + "</b>"
        formatted.append(line)

    Notification("File information", "\n".join(formatted)).send()

    return True


def action_group(paths: list[Path]) -> bool:
    current_dirs = [str(p.name) for p in Path(".").iterdir() if p.is_dir()]
    temp_dir = f"temp_{datetime.now().strftime('%F_%T')}"
    options = [temp_dir] + current_dirs + ["Cancel"]

    choice = prompt_options(
        prompt="Group file(s) where?", options=options, default=temp_dir
    )

    if not choice or choice.lower() == "cancel":
        log.error("Could not group files due to empty selection.")
        Notification("❌ File Grouping", "Operation cancelled.").send()
        return False

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

    return True


def action_interactive_trash(paths: list[Path]) -> bool:
    results: list[bool] = []

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
            results.append(run_cmd(["trash-put", path]).success)
            Notification("File trashed", f"Trashed {str(path)!r}.").send()

    return all(results)


def action_open_editor(paths: list[Path]) -> bool:
    if shutil.which("gimp"):
        run_cmd_background(["gimp", *paths])
        return True

    return False


def action_open_in_new_windows(paths: list[Path]) -> bool:
    opener = "xdg-open" if sys.platform == "linux" else "open"
    return all([run_cmd([opener, path]).success for path in paths])


def action_rotate(paths: list[Path], degrees: int = 90) -> bool:
    return all(
        [run_cmd(["magick", path, "-rotate", degrees, path]).success for path in paths]
    )


def action_show_help(paths: list[Path], actions_map: ActionsMap) -> bool:
    Notification("nsxiv actions", get_help_text(actions_map)).send()
    return True


def action_trash(paths: list[Path]) -> bool:
    return run_cmd(["trash-put", *paths]).success


def action_update_wallpaper(paths: list[Path]) -> bool:
    return run_cmd(["wallpaper_setter", paths[0]]).success

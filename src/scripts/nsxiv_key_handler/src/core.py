import shutil
from datetime import datetime
from pathlib import Path
from typing import Callable, NamedTuple

from common.clipboard_utilities import ClipboardManager
from common.cmd_utilities import run_cmd, run_cmd_background
from common.io_utilities import trash_files, trash_files_interactive
from common.logger import log
from common.media import flip_image, rotate_image
from common.notification_utilities import Notification
from common.prompt_utilities import prompt_options
from common.variables import OPENER


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


def a_copy_file(paths: list[Path]) -> bool:
    if len(paths) > 1:
        Notification("⚠️ Copy Notice", "Only one file can be copied at a time.").send()

    result = ClipboardManager.copy_file(paths[0])

    if result:
        Notification(
            "✅ File Copied", f"Copied file {str(paths[0])!r} to clipboard"
        ).send(icon_path=paths[0], open_image_onclick=True)
    else:
        Notification(
            "❌ Copy Failed", f"Unable to copy file {str(paths[0])!r} to clipboard."
        ).send()

    return result


def a_copy_file_paths(paths: list[Path]) -> bool:
    paths_str = "\n".join([str(path) for path in paths])
    result = ClipboardManager.copy_text(paths_str)

    if not result:
        Notification(
            "❌ Copy Failed", f"Unable to copy {len(paths)} paths to clipboard."
        ).send()
        return False

    notification = Notification("✅ Paths Copied")
    if len(paths) == 1:
        notification.message = f"Copied path {str(paths[0])!r} to clipboard."
    else:
        notification.message = f"Copied {len(paths)} paths to clipboard."

    notification.send()

    return True


def a_flip_images(paths: list[Path]) -> bool:
    for path in paths:
        flip_image(path)
    return True


def a_get_file_info(paths: list[Path]) -> bool:
    cmd_result = run_cmd(["mediainfo", paths[0]])

    if not cmd_result.success:
        Notification(
            "❌ File Information",
            f"Unable to fetch information for file {str(paths[0])!r}",
        ).send()
        return False

    formatted: list[str] = []
    for line in cmd_result.output.splitlines():
        line = line.replace(":", ": <b>", 1) + "</b>"
        formatted.append(line)

    Notification("ℹ️ File Information", "\n".join(formatted)).send()

    return True


def a_group_files(paths: list[Path]) -> bool:
    current_dirs = [str(p.name) for p in Path(".").iterdir() if p.is_dir()]
    temp_dir = f"temp_{datetime.now().strftime('%F_%T')}"
    options = [temp_dir] + current_dirs + ["Cancel"]

    choice = prompt_options(
        prompt="Group files where?", options=options, default=temp_dir
    )

    if not choice or choice.lower() == "cancel":
        log.error("Could not group files due to empty selection.")
        Notification("❌ File Grouping", "Operation cancelled.").send()
        return False

    destdir = Path.cwd() / choice
    if not destdir.exists():
        destdir.mkdir(parents=True, exist_ok=True)
        Notification("✅ File Grouping", f"Created directory {str(destdir)}").send()

    for path in paths:
        shutil.move(path, destdir)

    notification = Notification("✅ File Grouping")
    if len(paths) == 1:
        notification.message = f"File {paths[0].name!r} moved to {str(destdir)!r}."
    else:
        notification.message = f"Moved {len(paths)} files to {str(destdir)!r}."

    notification.send(icon_path=destdir / paths[0].name, open_image_onclick=True)

    return True


def a_open_images_in_editor(paths: list[Path]) -> bool:
    if shutil.which("gimp"):
        run_cmd_background(["gimp", *paths])
        return True

    Notification("❌ Open Images in Editor", "Unable to find an image editor.").send()
    return False


def a_open_in_new_windows(paths: list[Path]) -> bool:
    return all([run_cmd([OPENER, path]).success for path in paths])


def a_rotate_images(paths: list[Path], degrees: int = 90) -> bool:
    for path in paths:
        rotate_image(path, degrees)
    return True


def a_show_help(paths: list[Path], actions_map: ActionsMap) -> bool:
    Notification("ℹ️ nsxiv Actions", get_help_text(actions_map)).send()
    return True


def a_trash_files(paths: list[Path]) -> bool:
    return trash_files(paths)


def a_trash_files_interactive(paths: list[Path]) -> bool:
    return trash_files_interactive(paths)


def a_set_images_as_wallpaper(paths: list[Path]) -> bool:
    return run_cmd(["wallpaper_setter", *paths]).success

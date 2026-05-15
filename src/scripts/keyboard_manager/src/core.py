import shutil
import subprocess

from common.cmd_utilities import run_cmd
from common.helpers import NotificationSystem
from common.logger import log
from common.prompt_utilities import prompt_options


def get_current_layout() -> str | None:
    """Fetch the current keyboard layout."""
    try:
        result = run_cmd(["setxkbmap", "-query"])
        for line in result.output.splitlines():
            if line.startswith("layout:"):
                return line.split()[1]

    except subprocess.CalledProcessError:
        log.error("Unable to get current layout.")

    return None


def get_available_layouts() -> list[str] | None:
    """Get the available keyboard layouts using localectl."""
    try:
        result = run_cmd(["localectl", "list-x11-keymap-layouts"])
        return result.output.splitlines()

    except subprocess.CalledProcessError:
        log.error("Unable to list x11 keymap layouts.")

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
        log.error("Binary 'remapd' not found.")
        return False

    try:
        run_cmd(["killall", "remapd"])
        log.debug("Killed 'remapd'.")

        subprocess.Popen(["remapd"])
        log.debug("Restarted 'remapd'.")
        return True

    except Exception as e:
        log.error(f"Failed to restart 'remapd': {e}")

    return False


def set_keyboard_layout(layout: str) -> bool:
    """Set the chosen keyboard layout."""
    try:
        result = run_cmd(["setxkbmap", layout]).success
        if result:
            NotificationSystem.run(f"Keyboard layout changed to {layout!r}")
        return result

    except subprocess.CalledProcessError:
        log.error(f"Unable to set layout to {layout!r}.")

    return False

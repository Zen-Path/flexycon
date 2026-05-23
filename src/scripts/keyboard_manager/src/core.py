import shutil
import subprocess

from common.cmd_utilities import run_cmd
from common.helpers import NotificationSystem
from common.logger import log
from common.prompt_utilities import prompt_options


def get_current_layout() -> str | None:
    """Fetch the current keymap layout code."""
    try:
        result = run_cmd(["setxkbmap", "-query"])
        for line in result.output.splitlines():
            if line.startswith("layout:"):
                return line.split()[1]

    except subprocess.CalledProcessError:
        pass

    log.error("Unable to get current layout.")
    return None


def get_available_layouts() -> list[str] | None:
    """Fetch list of available keymap layouts."""
    try:
        result = run_cmd(["localectl", "list-x11-keymap-layouts"])
        return result.output.splitlines()

    except subprocess.CalledProcessError:
        log.error("Unable to find keymap layouts.")

    return None


def process_layouts(
    available_layouts: list[str],
    layout_full_names: dict[str, str],
    current_layout: str | None,
) -> list[str]:
    """
    Formats layouts with full names, ensures 'us' is at the top,
    and removes the current active layout entirely.
    """

    if not available_layouts:
        return []

    formatted_layouts: list[str] = []
    us_layout_formatted: str | None = None

    for layout in available_layouts:
        if current_layout and layout == current_layout:
            continue

        display_name = layout_full_names.get(layout, layout)

        if layout == "us":
            us_layout_formatted = display_name
        else:
            formatted_layouts.append(display_name)

    if us_layout_formatted:
        formatted_layouts.insert(0, us_layout_formatted)

    return formatted_layouts


def prompt_layout(
    available_layouts: list[str],
    layout_full_names: dict[str, str],
    current_layout: str | None,
) -> str | None:
    """Processes layouts and prompts the user to select one."""

    if not available_layouts:
        return None

    options = process_layouts(available_layouts, layout_full_names, current_layout)
    current_layout_fmt = f" (current: {current_layout})" if current_layout else ""

    choice = prompt_options(
        prompt=f"Keymap layout{current_layout_fmt}",
        options=options,
        row_count=15,
    )

    if not choice:
        return None

    layout_code = choice.split(" - ")[0]
    log.info(f"Chosen layout: {layout_code!r}")
    if layout_code not in available_layouts:
        return None

    return layout_code


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


def set_keymap_layout(layout: str) -> bool:
    """Set the chosen keymap layout."""
    try:
        result = run_cmd(["setxkbmap", layout]).success
        if result:
            NotificationSystem.run(f"Keymap layout changed to {layout!r}")
        return result

    except subprocess.CalledProcessError:
        log.error(f"Unable to set layout to {layout!r}.")

    return False

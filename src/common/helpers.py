import os
import shutil
import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Generator, Literal

import psutil

from common.cmd_utilities import run_cmd, run_cmd_background
from common.logger import log
from common.system_utilities import get_display_server


def get_version() -> str:
    pyproject_path = Path(__file__).resolve().parent.parent.parent / "pyproject.toml"

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        version = data["project"]["version"]
    except Exception:
        version = "0.0.0-dev"

    return version


def resolve_path(path_parts: list[str]) -> Path:
    """Resolve a list of path parts into a single expanded path."""
    return Path(os.path.expandvars(os.path.join(*path_parts)))


def parse_range(range_raw: str) -> tuple[tuple[int, int] | None, str | None]:
    """Parse 'start:end' string into two integers."""
    if not range_raw or ":" not in range_raw:
        return None, "'range' must be a non-empty string of the form 'start:end'"

    parts = range_raw.split(":")
    if len(parts) != 2:
        return None, "'range' must be of the form 'start:end'"

    try:
        return (int(parts[0]), int(parts[1])), None
    except ValueError:
        return None, "'range' values must be integers"


def get_parent_process_chain(start_pid: int | None = None) -> list[tuple[str, int]]:
    """
    Traverse the parent chain of the current process (or a given process) and collect
    a list of tuples (process_name, pid).

    Args:
        start_pid (int, optional): PID of the process to start traversal from.
                                   Defaults to the current process.

    Returns:
        list of tuple: [(name, pid), ...]
    """

    process_chain: list[tuple[str, int]] = []
    current_process: psutil.Process | None = (
        psutil.Process(start_pid) if start_pid else psutil.Process()
    )

    while current_process:
        process_chain.append((current_process.name(), current_process.pid))
        current_process = current_process.parent()

    return process_chain


class NotificationSystem:
    @classmethod
    def run(
        cls,
        title: str,
        message: str | None = None,
        urgency: Literal["low", "normal", "critical"] = "normal",
        icon_path: Path | None = None,
        callback: Callable[[], None] | None = None,
        open_image_onclick: bool = False,
    ):
        """
        Send a desktop notification. Accepts either a custom callback OR
        an action to open the image (icon), but not both.
        """

        # Enforce mutual exclusivity
        if callback and open_image_onclick:
            raise ValueError(
                "You cannot provide both a 'callback' and 'open_image_onclick'."
            )

        cmd: list[str | Path] = ["notify-send", title.strip(), "--urgency", urgency]

        if message is not None:
            cmd.append(message.rstrip())

        if icon_path:
            cmd.extend(["-i", icon_path])

        # Determine which action to use, if any
        action_token = None
        if open_image_onclick and icon_path:
            action_token = "open_image"
            cmd.append(f"--action={action_token}=Open Image")
        elif callback:
            action_token = "custom_callback"
            cmd.append(f"--action={action_token}=Click Me")

        log.debug(f"Sending notification:\ntitle={title!r}\nmessage='{message}'")

        try:
            # If no action was defined, fire and forget (non-blocking)
            if not action_token:
                subprocess.Popen(cmd)
                return

            # If an action exists, block and wait for user input
            cmd_output = run_cmd(cmd).output

            if cmd_output == "open_image" and icon_path:
                subprocess.Popen(["xdg-open", icon_path])

            elif cmd_output == "custom_callback" and callback:
                callback()

        except Exception as e:
            log.error(f"Notification failed: {e}")

    @classmethod
    def get_paused(cls) -> bool | None:
        if not shutil.which("dunstctl"):
            return None

        result = run_cmd(["dunstctl", "is-paused"])
        if not result.success:
            return None

        return result.output.strip().lower() == "true"

    @classmethod
    def set_paused(cls, status: bool | Literal["toggle"]) -> bool | None:
        if not shutil.which("dunstctl"):
            return None

        status_str = ""
        if status == "toggle":
            status_str = "toggle"
        else:
            status_str = str(status).lower()

        result = run_cmd(["dunstctl", "set-paused", status_str])
        if not result.success:
            return None

        return result.success


@dataclass
class Color:
    r: float = 0.0
    g: float = 0.0
    b: float = 0.0
    a: float = 1.0

    @classmethod
    def from_hex(cls, hex_str: str):
        """Creates a Color object from #RRGGBB or #RRGGBBAA strings."""
        hex_str = hex_str.lstrip("#")
        lv = len(hex_str)

        # Default alpha to 1.0 if not provided in hex
        alpha = 1.0

        if lv == 6:
            r, g, b = tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4))
        elif lv == 8:
            r, g, b, a_int = tuple(int(hex_str[i : i + 2], 16) for i in (0, 2, 4, 6))
            alpha = round(a_int / 255.0, 2)
        else:
            raise ValueError(f"Invalid hex color: {hex_str}")

        return cls(float(r), float(g), float(b), alpha)

    def to_tuple(self) -> tuple[float, float, float, float]:
        return (self.r, self.g, self.b, self.a)

    def __str__(self) -> str:
        return f"{self.r:.1f},{self.g:.1f},{self.b:.1f},{self.a:.1f}"

    def __iter__(self) -> Generator[float]:
        yield from self.to_tuple()


@dataclass
class Window:
    id: int
    name: str | None = None

    @classmethod
    def get_active_window(cls) -> Window | None:
        # TODO: check on Linux
        result = run_cmd(["xdotool", "getactivewindow"])
        if not result.success:
            return None

        window_id = int(result.output)
        return Window(window_id)

    @classmethod
    def get_window_name(cls, window_id: int) -> str | None:
        # TODO: check on Linux
        result = run_cmd(["xdotool", "getwindowname", window_id])
        if not result.success:
            return None

        return result.output


class SoundUtility:
    @classmethod
    def get_volume(cls) -> tuple[int, bool] | None:
        """Returns the volume and mute status, or None."""
        # Should return something like this:
        # - 'Volume: 0.55'
        # - 'Volume: 0.50 [MUTED]'
        result = run_cmd(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"])
        if not result.success:
            return None

        volume_info = result.output
        if volume_info.startswith("Could not connect to"):
            return None

        is_muted = "[MUTED]" in volume_info

        return (round(float(volume_info.split(" ")[1]) * 100), is_muted)

    @classmethod
    def update_volume(cls, diff: int) -> bool:
        """
        Usage:
            - update_volume(2) to increase volume by 2
            - update_volume(-2) to decrease it by 2
        """
        return run_cmd(
            [
                "wpctl",
                "set-volume",
                "@DEFAULT_SINK@",
                f"{abs(diff)}%{'-' if diff < 0 else '+'}",
            ]
        ).success

    @classmethod
    def toggle_mute(cls):
        run_cmd(["wpctl", "set-mute", "@DEFAULT_SINK@", "toggle"])


def set_wallpaper(image_path: Path) -> bool:
    """Sets the wallpaper based on the current environment."""
    image_path = image_path.resolve()

    match get_display_server():
        case "X11":
            run_cmd(["xwallpaper", "--clear", "--zoom", image_path])

        case "Wayland":
            if shutil.which("swaybg"):
                # Note: swaybg typically runs as a daemon; this kills previous instances
                run_cmd(["pkill", "swaybg"])
                run_cmd_background(["swaybg", "-i", image_path, "-m", "fill"])

            elif shutil.which("hyprpaper"):
                run_cmd(["hyprpaper", "preload", image_path])
                run_cmd(["hyprpaper", "wallpaper", f", {image_path}"])

        case "macOS":
            script = f'tell application "System Events" to set picture of every desktop to "{image_path}"'
            run_cmd(["osascript", "-e", script])

        case _:
            log.error("Could not find program to set the wallpaper.")
            return False

    return True

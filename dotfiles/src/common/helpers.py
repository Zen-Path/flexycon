import json
import os
import re
import secrets
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal, Sequence

import psutil
from common.logger import logger


@dataclass
class CommandResult:
    return_code: int
    output: str

    @property
    def success(self) -> bool:
        return self.return_code == 0

    def __str__(self) -> str:
        return self.output


def resolve_path(path_parts: list[str]) -> Path:
    """Resolve a list of path parts into a single expanded path."""
    return Path(os.path.expandvars(os.path.join(*path_parts)))


def run_command(command: list[str]) -> CommandResult:
    """Run a shell command and return its result."""
    cmd_identifier = secrets.token_hex(5)  # 8 hex chars

    logger.debug(f"Running {command} with id '{cmd_identifier}'")

    output = []
    with subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
    ) as process:
        if process.stdout is not None:
            for line in process.stdout:
                output.append(line)
                logger.debug(line.strip())

        return_code = process.wait()

    logger.debug(
        f"Command with id '{cmd_identifier}' finished with return code {return_code}"
    )

    return CommandResult(return_code=return_code, output="\n".join(output))


def run_command_background(command: list[str]):
    """Launch a process and move on immediately."""
    logger.debug(f"Running {command} in background.")

    subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,  # detach from the current process group (Unix)
        shell=False,
    )


def write_to_file(content: str, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

    logger.debug(
        f"Wrote contents {content[:20].replace('\n', ' ')!r} to file {str(path)!r}"
    )


def prompt_bool(prompt: str, default: bool | None = None) -> bool | None:
    """
    Prompts the user for a yes/no response.

    Args:
        prompt: The question to display.
        default: The value to return if input is invalid or interrupted.

    Returns:
        True if 'y', 'yes', '1', False if 'n', 'no', '0', otherwise the default value.
    """
    if default is True:
        hint = "Y/n"
    elif default is False:
        hint = "y/N"
    else:
        hint = "y/n"

    try:
        user_input = input(f"{prompt} ({hint}): ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        return default

    if user_input in ("y", "yes", "1"):
        return True
    if user_input in ("n", "no", "0"):
        return False

    return default


def notify(
    title: str,
    message: str | None = None,
    urgency: Literal["low", "normal", "critical"] = "normal",
    icon_path: str | Path | None = None,
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

    cmd = ["notify-send", title, "--urgency", urgency]

    if message:
        cmd.append(message)

    if icon_path:
        icon_path = str(icon_path)
        cmd.extend(["-i", icon_path])

    # Determine which action to use, if any
    action_token = None
    if open_image_onclick and icon_path:
        action_token = "open_image"
        cmd.append(f"--action={action_token}=Open Image")
    elif callback:
        action_token = "custom_callback"
        cmd.append(f"--action={action_token}=Click Me")

    try:
        # If no action was defined, fire and forget (non-blocking)
        if not action_token:
            subprocess.Popen(cmd)
            return

        # If an action exists, block and wait for user input
        result = subprocess.check_output(cmd, text=True).strip()

        if result == "open_image" and icon_path:
            subprocess.Popen(["xdg-open", icon_path])

        elif result == "custom_callback" and callback:
            callback()

    except Exception as e:
        logger.error(f"Notification failed: {e}")


def get_notifications_paused_status() -> bool:
    return run_command(["dunstctl", "is-paused"]).output.strip().lower() == "true"


def set_notifications_status(status: Literal["true", "false", "toggle"]) -> int:
    return run_command(["dunstctl", "set-paused", status]).success


def ensure_directory_interactive(path: Path):
    """
    Interactively ensure all directories leading to the path exist.
    """
    # Check the directory part, since 'path' might be a file
    directory = path if path.suffix == "" else path.parent

    if not directory.exists():
        print(f":: The directory '{directory}' does not exist.")

        user_resp = prompt_bool("Create the directory?", default=True)

        if user_resp is True:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"\n:: Created directory: {directory}")
        else:
            print("\n:: Operation cancelled by user.")
            sys.exit(1)


def remove_files_by_pattern(patterns: Sequence[str]) -> None:
    """
    Recursively deletes files and directories matching the given glob patterns.
    """
    for pattern in patterns:
        for path in Path(".").rglob(pattern):
            try:
                if path.is_dir() and not path.is_symlink():
                    shutil.rmtree(path)
                else:
                    # Using missing_ok for unlinking to avoid race conditions
                    path.unlink(missing_ok=True)

                logger.debug(f"Removed {path!r}.")
            except Exception as e:
                logger.warning(f"Failed to remove {path!r}: {e}")


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


def load_json(path: Path) -> str | None:
    """Load a JSON file if it exists."""
    if not os.path.isfile(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(e)
        return None


def truncate(
    text: str,
    max_length: int,
    placeholder: str = "…",
    truncate_from_end: bool = True,
) -> str:
    """
    Truncate a string to max_length.

    Parameters:
    - text: the original string
    - max_length: maximum length including placeholder
    - placeholder: string to indicate truncation
    - truncate_start: if True, truncate the start; else truncate the end

    Returns:
    - truncated string with placeholder if necessary
    """
    if len(text) <= max_length:
        return text

    if max_length == 0:
        return ""

    if len(placeholder) >= max_length:
        return truncate(placeholder, max_length, "", truncate_from_end)

    truncated_length = max_length - len(placeholder)
    if truncate_from_end:
        return text[:truncated_length] + placeholder
    else:
        return placeholder + text[-truncated_length:]


def get_display_server() -> Literal["X11", "Wayland"] | None:
    """
    Returns the display server currently in use, or ``None`` if it can't
    be detected.
    """
    display_env_val = os.environ.get("DISPLAY")

    if os.environ.get("WAYLAND_DISPLAY"):
        return "Wayland"
    elif display_env_val and display_env_val != "needs-to-be-defined":
        return "X11"
    else:
        return None


def split_acronyms(token: str) -> list[str]:
    """
    Handle acronyms.
    If there's no uppercase letter, return the token as-is. Otherwise, detect
    sequences of 2+ uppercase chars (acronyms). If an acronym is immediately
    followed by a lowercase letter, the last capital joins the lowercase word.

    Examples:
    - HTMLParser → HTML + Parser
    - parseURLString → parse + URL + String
    """
    if not re.search(r"[A-Z]", token):
        return [token]

    parts = []
    i = 0
    n = len(token)

    while i < n:
        # Match acronym (2+ uppercase letters)
        match = re.match(r"[A-Z]{2,}", token[i:])
        if match:
            acronym = match.group(0)
            end = i + len(acronym)

            # If next char exists and is lowercase, merge last capital with next word
            if end < n and token[end].islower():
                parts.append(acronym[:-1])
                i = end - 1  # start new word from last uppercase
            else:
                parts.append(acronym)
                i = end
        else:
            # Otherwise, grab the next "normal" word segment
            match = re.match(r"[A-Z][a-z]+|[a-z]+|\d+", token[i:])
            if match:
                parts.append(match.group(0))
                i += len(match.group(0))
            else:
                # fallback: add single char (rare, safety net)
                parts.append(token[i])
                i += 1

    return parts


def split_into_words(name: str, boundaries: list[str] = [" ", "-", "_"]) -> list[str]:
    """
    Split a string into words in multiple stages.
    """
    if not name:
        return []

    tokens: list[str]
    if boundaries:
        pattern = "|".join(map(re.escape, boundaries))
        tokens = [t for t in re.split(pattern, name) if t]
    else:
        tokens = [name]

    def split_tokens(tokens: list[str], splitter) -> list[str]:
        result = []
        for token in tokens:
            result.extend(splitter(token))
        return [t for t in result if t]

    def split_numbers(token: str) -> list[str]:
        # Split between digit and non-digit boundaries
        return re.split(r"(?<=\D)(?=\d)|(?<=\d)(?=\D)", token)

    tokens = split_tokens(tokens, split_numbers)

    def split_camel_case(token: str) -> list[str]:
        # Insert space between lowercase and uppercase letter boundaries
        return re.split(r"(?<=[a-z])(?=[A-Z])", token)

    tokens = split_tokens(tokens, split_camel_case)

    tokens = split_tokens(tokens, split_acronyms)

    return tokens


@dataclass
class ScreenLocker:
    cmd: list[str]
    req_wayland: bool = False
    req_x11: bool = False


class System:
    """
    Represents a user-space system.
    """

    SCREEN_LOCKER_REGISTRY = {
        "slock": ScreenLocker(["slock"], req_x11=True),
        "i3lock": ScreenLocker(["i3lock"], req_x11=True),
        "xlock": ScreenLocker(["xlock"], req_x11=True),
        "swaylock": ScreenLocker(["swaylock"], req_wayland=True),
        "hyprlock": ScreenLocker(["hyprlock"], req_wayland=True),
        "xdg-screensaver": ScreenLocker(["xdg-screensaver", "lock"]),
        "gnome-screensaver": ScreenLocker(["gnome-screensaver-command", "-l"]),
        "loginctl": ScreenLocker(["loginctl", "lock-session"]),
    }

    @classmethod
    def _get_linux_controller(cls) -> Literal["systemctl", "loginctl"] | None:
        """
        Determines the system's controller based on the init system in use.
        Returns 'systemctl' if systemd is detected, otherwise 'loginctl'.
        """
        if sys.platform != "linux":
            logger.warning(f"Method isn't supported for {sys.platform!r}")
            return None

        init_path = os.path.realpath("/sbin/init")
        return "systemctl" if "systemd" in init_path else "loginctl"

    @classmethod
    def _get_lock_cmd(cls) -> list[str] | None:
        """Determines the appropriate lock command based on environment and availability."""
        if sys.platform == "darwin":
            # Note: doesn't immediately lock the screen unless "Require password after
            # screen saver begins or display is turned off" is set to "Immediately" in
            # the user's settings
            return ["pmset", "displaysleepnow"]

        session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
        is_wayland = (session_type == "wayland") or ("WAYLAND_DISPLAY" in os.environ)
        is_x11 = (session_type == "x11") or ("DISPLAY" in os.environ)

        for locker in cls.SCREEN_LOCKER_REGISTRY.values():
            if not shutil.which(locker.cmd[0]):
                continue

            if locker.req_x11 and not is_x11:
                continue

            if locker.req_wayland and not is_wayland:
                continue

            return locker.cmd

        return None

    @classmethod
    def lock_screen(cls):
        """Lock the screen."""
        cmd = cls._get_lock_cmd()
        if cmd:
            run_command(cmd)
        else:
            logger.error("No screen locker found.")

    @classmethod
    def sleep(cls):
        """Put the system to sleep."""
        if sys.platform == "darwin":
            run_command(["pmset", "sleepnow"])
        elif sys.platform == "linux":
            if cmd := cls._get_linux_controller():
                run_command([cmd, "suspend", "-i"])
        else:
            logger.warning(f"Method isn't supported for {sys.platform!r}")

    @classmethod
    def power_off(cls):
        """Power off the system."""
        if sys.platform == "darwin":
            run_command(
                ["osascript", "-e", 'tell app "loginwindow" to «event aevtrsdn»']
            )
        elif sys.platform == "linux":
            if cmd := cls._get_linux_controller():
                run_command([cmd, "poweroff", "-i"])
        else:
            logger.warning(f"Method isn't supported for {sys.platform!r}")

    @classmethod
    def reboot(cls):
        """Reboot the system."""
        if sys.platform == "darwin":
            run_command(
                ["osascript", "-e", 'tell app "loginwindow" to «event aevtrrst»']
            )
        elif sys.platform == "linux":
            if cmd := cls._get_linux_controller():
                run_command([cmd, "reboot", "-i"])
        else:
            logger.warning(f"Method isn't supported for {sys.platform!r}")

    @classmethod
    def hibernate(cls):
        """Hibernate the system."""
        if sys.platform == "darwin":
            # Standard hibernation isn't exposed gracefully in macOS user-space.
            # We use sleep as a safe default.
            run_command(["pmset", "sleepnow"])
        elif sys.platform == "linux":
            if cmd := cls._get_linux_controller():
                run_command([cmd, "hibernate", "-i"])
        else:
            logger.warning(f"Method isn't supported for {sys.platform!r}")


def get_parent_process_chain(start_pid=None):
    """
    Traverse the parent chain of the current process (or a given process) and collect
    a list of tuples (process_name, pid).

    Args:
        start_pid (int, optional): PID of the process to start traversal from.
                                   Defaults to the current process.

    Returns:
        list of tuple: [(name, pid), ...]
    """

    process_chain = []
    current_process = psutil.Process(start_pid) if start_pid else psutil.Process()

    while current_process:
        process_chain.append((current_process.name(), current_process.pid))
        current_process = current_process.parent()

    return process_chain


class Dmenu:
    @classmethod
    def run(
        cls,
        prompt: str,
        choices: list[str],
        case_insensitive: bool = True,
        list_view_item_count: int | None = None,
    ) -> str:
        cmd = ["dmenu", "-p", prompt]

        if case_insensitive:
            cmd.append("-i")

        if list_view_item_count is not None:
            # TODO: check this logic on linux
            cmd.append("-l")

            if list_view_item_count > 0:
                cmd.append(str(list_view_item_count))

        result = subprocess.run(
            cmd,
            input="\n".join(choices),
            capture_output=True,
            text=True,
        )

        return result.stdout.strip()

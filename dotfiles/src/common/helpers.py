import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tomllib
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Generator, Literal

import psutil
from common.logger import logger


def get_version() -> str:
    pyproject_path = (
        Path(__file__).resolve().parent.parent.parent.parent / "pyproject.toml"
    )

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        version = data["project"]["version"]
    except Exception:
        version = "0.0.0-dev"

    return version


@dataclass
class CommandResult:
    return_code: int
    raw_output: str

    @property
    def output(self) -> str:
        return self.raw_output.strip()

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

    logger.debug(f"Running {command} with id {cmd_identifier!r}")

    output: list[str] = []
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
        f"Command with id {cmd_identifier!r} finished with return code {return_code}"
    )

    return CommandResult(return_code=return_code, raw_output="\n".join(output))


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


def prompt_options(
    prompt: str,
    options: list[str],
    default: int | None = None,
    prefer_gui: bool = True,
    list_view_item_count: int = 0,
) -> tuple[int, str] | None:
    """
    Prompts the user to select an option from a list with an optional default.

    Args:
        prompt: The question to display.
        options: List of strings to choose from.
        default: The index of the default option (0-based). Negative indexes are allowed.
        prefer_gui: Display the options with a GUI or in the terminal
        list_view_item_count: For Dmenu, how many list items will be displayed at once

    Returns:
        A tuple of (index, choice_str). If input is empty or invalid,
        returns the default tuple. Returns None if no default exists.
    """
    if not options:
        return None

    # Normalize default index
    resolved_default = None
    if default is not None:
        if 0 <= default < len(options):
            resolved_default = default
        elif -len(options) <= default < 0:
            resolved_default = len(options) + default

    # Display hint as 1-based for the user (-1 on a list of 3 becomes [3])
    hint = f" [{resolved_default + 1}]" if resolved_default is not None else ""

    prompt_fmt = prompt.strip(" :")

    if prefer_gui:
        selection = None

        if shutil.which("dmenu"):
            selection = Dmenu.run(
                prompt=prompt_fmt,
                choices=options,
                list_view_item_count=list_view_item_count,
            )

        # TODO: implement an interface
        if shutil.which("choose"):
            try:
                selection = subprocess.run(
                    "choose",
                    input="\n".join(options),
                    capture_output=True,
                    text=True,
                ).stdout
            except Exception as e:
                logger.error(e)
                pass

        if selection:
            try:
                # Find the index of the selected string
                idx = options.index(selection)
                return (idx, options[idx])
            except ValueError:
                pass

        # If user hit Esc or selection failed, try default
        if resolved_default is not None:
            return (resolved_default, options[resolved_default])

    print(f":: {prompt_fmt}:")
    for i, option in enumerate(options, 1):
        suffix = " (default)" if (i - 1) == resolved_default else ""
        print(f"{i}. {option}{suffix}")

    try:
        user_input = input(f"\n> Select an option{hint}: ").strip()
    except (KeyboardInterrupt, EOFError):
        user_input = ""

    # Handle empty input
    if not user_input and resolved_default is not None:
        return (resolved_default, options[resolved_default])

    # Handle numeric input
    if user_input.isdigit():
        idx = int(user_input) - 1
        if 0 <= idx < len(options):
            return (idx, options[idx])

    # Handle invalid input
    if resolved_default is not None:
        return (resolved_default, options[resolved_default])

    return None


def ensure_directory_interactive(path: Path) -> bool:
    """
    Interactively ensure all directories leading to the path exist.
    """
    # Check the directory part, since 'path' might be a file
    directory = path if path.suffix == "" else path.parent

    if directory.exists():
        return True

    logger.info(f"Directory {str(directory)!r} does not exist.")

    user_resp = prompt_bool("Create the directory?", default=True)

    if user_resp is True:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory!r}")
        return True
    else:
        logger.debug("Operation cancelled by user.")
        return False


def remove_files_by_pattern(
    patterns: set[str],
    base_dir: str | Path = ".",
    global_excludes: set[str] | None = None,
) -> None:
    """
    Recursively deletes files and directories matching glob patterns,
    unless they are part of a globally excluded directory tree.

    :param patterns: Set of glob patterns (e.g., {'*.tmp', 'build'}).
    :param base_dir: Root directory to start the search.
    :param global_excludes: Directory names to ignore anywhere in the path.
    """
    if global_excludes is None:
        global_excludes = set()

    base_path = Path(base_dir).resolve()

    for pattern in patterns:
        # rglob handles the recursion for the pattern matching
        for path in base_path.rglob(pattern):
            # Existence check (handles overlapping pattern matches)
            if not path.exists() and not path.is_symlink():
                continue

            # SKIP LOGIC: Check if any segment of the path is in global_excludes
            # This protects the folder itself and everything inside it.
            if any(part in global_excludes for part in path.parts):
                continue

            try:
                # DELETION LOGIC
                if path.is_dir() and not path.is_symlink():
                    shutil.rmtree(path)
                else:
                    # missing_ok=True handles race conditions
                    path.unlink(missing_ok=True)

                logger.debug(f"Removed {str(path)!r}")
            except Exception as e:
                logger.warning(f"Failed to remove {str(path)!r}: {e}")


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
    display_env_val = os.getenv("DISPLAY")

    if os.getenv("WAYLAND_DISPLAY"):
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

    parts: list[str] = []
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

    def split_tokens(
        tokens: list[str], splitter: Callable[[str], list[str]]
    ) -> list[str]:
        result: list[str] = []
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

        session_type = os.getenv("XDG_SESSION_TYPE", "").lower()
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


@dataclass
class PromptOption:
    id: str | int
    label: str
    symbol: str | None = None
    help_text: str | None = None
    action: Callable[[], Any] | None = None

    def display_text(self, separator: str = " ") -> str:
        """The human-readable string shown in the prompt."""
        if self.symbol:
            return f"{self.label}{separator}{self.symbol}"
        return self.label


class Dmenu:
    @classmethod
    def run(
        cls,
        prompt: str,
        choices: list[str],
        case_insensitive: bool = True,
        list_view_item_count: int = 0,
    ) -> str:
        """
        Prompt dmenu with a list of choices.

        NOTE: setting 'list_view_item_count' to '0' disables the vertical list view.
        """
        prompt_fmt = prompt.strip(" :")
        cmd = ["dmenu", "-p", prompt_fmt]

        if case_insensitive:
            cmd.append("-i")

        if list_view_item_count != 0:
            cmd.extend(["-l", str(list_view_item_count)])

        choices_fmt = list(filter(bool, map(str.strip, choices)))

        try:
            result = subprocess.run(
                cmd,
                input="\n".join(choices_fmt),
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()

        except FileNotFoundError:
            logger.error("Binary 'dmenu' not found.")
            return ""

        except Exception as e:
            logger.error(f"Command failed: {e}")
            return ""


class NotificationSystem:
    @classmethod
    def run(
        cls,
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
            cmd_output = run_command(cmd).output

            if cmd_output == "open_image" and icon_path:
                subprocess.Popen(["xdg-open", icon_path])

            elif cmd_output == "custom_callback" and callback:
                callback()

        except Exception as e:
            logger.error(f"Notification failed: {e}")

    @classmethod
    def get_paused(cls) -> bool | None:
        if not shutil.which("dunstctl"):
            return None

        result = run_command(["dunstctl", "is-paused"])
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

        result = run_command(["dunstctl", "set-paused", status_str])
        if not result.success:
            return None

        return result.success


def remove_diacritics(text: str) -> str:
    # Normalize to decompose characters (e.g., 'ă' becomes 'a' + '˘')
    normalized = unicodedata.normalize("NFD", text)

    # Filter out the "combining" marks (category 'Mn')
    result = "".join(c for c in normalized if unicodedata.category(c) != "Mn")

    return result


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
        result = run_command(["xdotool", "getactivewindow"])
        if not result.success:
            return None

        window_id = int(result.output)
        return Window(window_id)

    @classmethod
    def get_window_name(cls, window_id: int) -> str | None:
        # TODO: check on Linux
        result = run_command(["xdotool", "getwindowname", str(window_id)])
        if not result.success:
            return None

        return result.output


class Maim:
    @classmethod
    def run(
        cls,
        output_path: Path,
        select: bool = False,
        border_size: float = 4.0,
        padding: float = 0.0,
        tolerance: float = 20.0,
        color: Color = Color(100.0, 0.0, 0.0, 0.3),
        no_decorations: int = 2,
        hide_cursor: bool = True,
        quiet: bool = True,
        delay: float = 0.2,
        window: Window | None = None,
    ) -> bool:
        """
        Take screenshot of desktop and save to an image.
        """
        cmd = [
            "maim",
            f"--bordersize={border_size}",
            f"--padding={padding}",
            f"--tolerance={tolerance}",
            f"--color={color}",
            f"--nodecorations={no_decorations}",
        ]
        if hide_cursor:
            cmd.append("--hidecursor")
        if quiet:
            cmd.append("--quiet")
        if window:
            cmd.extend(["--window", str(window.id), "--capturebackground"])

        if select:
            cmd.extend(["--select", "--nodrag", "--highlight"])

        cmd.extend(["--delay", str(delay)])
        cmd.append(str(output_path))

        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            return run_command(cmd).success

        except FileNotFoundError:
            logger.error("Binary 'maim' not found.")
            return False

        except Exception as e:
            logger.error(f"Command failed: {e}")
            return False


class ScreenshotUtility:
    OUTPUT_DIR = (
        Path(os.getenv("XDG_PICTURES_DIR") or Path.home() / "Pictures") / "Screenshots"
    )

    @classmethod
    def _capture(
        cls,
        output_path: Path,
        copy_output: bool,
        select: bool = False,
        window: Window | None = None,
    ):
        success = Maim.run(output_path, select, window=window)

        if success and copy_output:
            # TODO: temporary, until sorting common logic structure to avoid circular
            # dependencies
            from common.packages.clipboard_utilities import copy_file

            copy_file(output_path)
            NotificationSystem.run(
                "Screenshot captured",
                f"Saved at {str(output_path)!r}",
                icon_path=output_path,
                open_image_onclick=True,
            )

        return success

    @classmethod
    def _compose_output_path(
        cls,
        capture_type: Literal["area", "window", "screen", "full"],
        output_dir: Path | None = None,
        name: str = "",
        ext: str = "png",
        include_timestamp: bool = True,
    ) -> Path:
        """Generate a file path to the output directory with the current timestamp."""
        name_fmt = name[:100]
        timestamp_fmt = (
            datetime.now().strftime("%Y-%m-%d_%H-%M-%S") if include_timestamp else ""
        )

        filename = "_".join(
            [part for part in [timestamp_fmt, name_fmt, capture_type] if part]
        )

        return Path(
            output_dir or cls.OUTPUT_DIR,
            f"{filename}.{ext}".lower(),
        )

    @classmethod
    def area(
        cls,
        output_dir: Path | None = None,
        copy_output: bool = False,
    ) -> bool:
        """Capture a selected area."""
        output_path = cls._compose_output_path("area", output_dir=output_dir)
        return cls._capture(output_path, copy_output, select=True)

    @classmethod
    def window(
        cls,
        window: Window | None = None,
        include_window_name: bool = False,
        output_dir: Path | None = None,
        copy_output: bool = False,
    ) -> bool:
        """Capture a window."""
        if window is None:
            window = Window.get_active_window()

        # If no window found, capture the screen
        if window is None:
            return cls.screen(output_dir=output_dir, copy_output=copy_output)

        window_name = ""
        if include_window_name:
            window_name = Window.get_window_name(window.id) or ""

        output_path = cls._compose_output_path(
            "window", name=window_name, output_dir=output_dir
        )

        return cls._capture(output_path, copy_output, window=window)

    @classmethod
    def screen(
        cls,
        screen: int | None = None,
        output_dir: Path | None = None,
        copy_output: bool = False,
    ) -> bool:
        """Capture a screen."""
        # TODO: Implement logic for targeting a single screen
        output_path = cls._compose_output_path("screen", output_dir=output_dir)
        return cls._capture(output_path, copy_output)

    @classmethod
    def full_screen(
        cls,
        output_dir: Path | None = None,
        copy_output: bool = False,
    ) -> bool:
        """Capture all screens."""
        output_path = cls._compose_output_path("full", output_dir=output_dir)
        return cls._capture(output_path, copy_output)


class SoundUtility:
    @classmethod
    def get_volume(cls) -> tuple[int, bool] | None:
        """Returns the volume and mute status, or None."""
        # Should return something like this:
        # - 'Volume: 0.55'
        # - 'Volume: 0.50 [MUTED]'
        result = run_command(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"])
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
        return run_command(
            [
                "wpctl",
                "set-volume",
                "@DEFAULT_SINK@",
                f"{abs(diff)}%{'-' if diff < 0 else '+'}",
            ]
        ).success

    @classmethod
    def toggle_mute(cls):
        run_command(["wpctl", "set-mute", "@DEFAULT_SINK@", "toggle"])

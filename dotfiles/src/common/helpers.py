import json
import os
import re
import secrets
import subprocess
import sys
from dataclasses import dataclass
from typing import List, Literal, Optional, Tuple

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


def resolve_path(path_parts: List[str]) -> str:
    """Resolve a list of path parts into a single expanded string path."""
    return os.path.expandvars(os.path.join(*path_parts))


def run_command(command: List[str]) -> CommandResult:
    """Run a shell command and return its result."""
    cmd_identifier = secrets.token_hex(5)  # 8 hex chars

    logger.info(f"Running {command} with id '{cmd_identifier}'")

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

    logger.info(
        f"Command with id '{cmd_identifier}' finished with return code {return_code}"
    )

    return CommandResult(return_code=return_code, output="\n".join(output))


def prompt_user(prompt, positive_resp=["y"], negative_resp=["n"], default="n"):
    possible_resp = positive_resp + negative_resp
    if default not in possible_resp:
        return False

    default_index = possible_resp.index(default)
    possible_resp[default_index] = possible_resp[default_index].upper()

    try:
        user_resp = input(f"> {prompt} ({'/'.join(possible_resp)}): ").strip().lower()
    except KeyboardInterrupt:
        exit()

    return user_resp in positive_resp


def notify(title: str, message: Optional[str] = None, icon: Optional[str] = None):
    """Send a desktop notification."""
    cmd = ["notify-send", title]
    if message:
        cmd.extend([message])

    if icon:
        cmd.extend(["-i", icon])

    return run_command(cmd)


def get_notifications_paused_status():
    return run_command(["dunstctl", "is-paused"])


def set_notifications_status(status: str):
    return run_command(["dunstctl", "set-paused", status])


def ensure_directory_interactive(path):
    if not os.path.exists(path):
        print(f":: The directory '{path}' does not exist.")
        user_resp = prompt_user("Would you like to create the directory?")
        if user_resp:
            os.makedirs(path)
        else:
            print(":: Operation cancelled by user.")
            sys.exit(1)


def ensure_directories_exist(file_path):
    """
    Ensure all directories leading to the given file path exist.
    """
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def parse_range(range_raw: str) -> Tuple[Optional[Tuple[int, int]], Optional[str]]:
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


def load_json(path):
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


def get_display_server() -> Optional[Literal["X11", "Wayland"]]:
    """
    Returns the display server currently in use, or ``None`` if it can't
    be detected.
    """
    if os.environ.get("WAYLAND_DISPLAY"):
        return "Wayland"
    elif os.environ.get("DISPLAY"):
        return "X11"
    else:
        return None


def split_acronyms(token: str) -> List[str]:
    """
    Handle acronyms.
    If there's no uppercase letter, return the token as-is. Otherwise, detect
    sequences of 2+ uppercase chars (acronyms). If an acronym is immediately followed by a lowercase letter, the last capital joins the lowercase word.

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


def split_into_words(name: str, boundaries: List[str] = [" ", "-", "_"]) -> List[str]:
    """
    Split a string into words in multiple stages.
    """
    if not name:
        return []

    tokens: List[str]
    if boundaries:
        pattern = "|".join(map(re.escape, boundaries))
        tokens = [t for t in re.split(pattern, name) if t]
    else:
        tokens = [name]

    def split_tokens(tokens: List[str], splitter) -> List[str]:
        result = []
        for token in tokens:
            result.extend(splitter(token))
        return [t for t in result if t]

    def split_numbers(token: str) -> List[str]:
        # Split between digit and non-digit boundaries
        return re.split(r"(?<=\D)(?=\d)|(?<=\d)(?=\D)", token)

    tokens = split_tokens(tokens, split_numbers)

    def split_camel_case(token: str) -> List[str]:
        # Insert space between lowercase and uppercase letter boundaries
        return re.split(r"(?<=[a-z])(?=[A-Z])", token)

    tokens = split_tokens(tokens, split_camel_case)

    tokens = split_tokens(tokens, split_acronyms)

    return tokens

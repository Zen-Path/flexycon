import shutil
import subprocess
from dataclasses import dataclass
from typing import Any, Callable

from common.logger import logger


class Dmenu:
    @classmethod
    def run(
        cls,
        prompt: str,
        choices: list[str],
        case_insensitive: bool = True,
        list_view_item_count: int = 0,
    ) -> str | None:
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
            return result.stdout.strip() if result.returncode == 0 else None

        except FileNotFoundError:
            logger.error("Binary 'dmenu' not found.")
            return None

        except Exception as e:
            logger.error(f"Command failed: {e}")
            return None


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

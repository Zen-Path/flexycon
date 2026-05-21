import shutil
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable

from common.logger import log


class BasePrompt(ABC):
    """Abstract base class defining the prompt interface structure."""

    @staticmethod
    def format_prompt(prompt: str) -> str:
        return prompt.strip(" :")

    @staticmethod
    def format_option(option: str) -> str:
        return option.strip()

    def _prepare_options(
        self, options: list[str], default: str | None, is_gui: bool
    ) -> tuple[list[str], dict[str, str]]:
        """
        Internal helper to filter out duplicates, format items, and position the default.
        Returns a tuple of (list_of_display_options, map_of_display_to_original).
        """

        if len(options) == 0:
            return ([], {})

        if default is not None and default not in options:
            raise ValueError("Default value should be a valid option.")

        mapping: dict[str, str] = {}
        cleaned_options: list[str] = []

        for option in options:
            opt_fmt = self.format_option(option)
            # Filter blank strings and prevent duplicate entries in the display list
            if opt_fmt and opt_fmt not in mapping:
                mapping[opt_fmt] = option
                cleaned_options.append(opt_fmt)

        if default is not None:
            fmt_default = self.format_option(default)

            # Remove existing default to prevent duplicates during positioning
            if fmt_default in cleaned_options:
                cleaned_options.remove(fmt_default)

            # GUI places default first, terminal places default last
            if is_gui:
                cleaned_options.insert(0, fmt_default)
            else:
                cleaned_options.append(fmt_default)

        return cleaned_options, mapping

    @abstractmethod
    def prompt(
        self,
        prompt: str,
        options: list[str],
        default: str | None = None,
    ) -> str | None:
        """
        Prompts the user with a list of options.
        Returns the original unformatted string chosen by the user, or the default.
        """
        pass


class DmenuPrompt(BasePrompt):
    """Dmenu implementation of the prompt interface."""

    def prompt(
        self,
        prompt: str,
        options: list[str],
        default: str | None = None,
        case_insensitive: bool = True,
        row_count: int = 0,
    ) -> str | None:
        if not options and not default:
            return None

        display_options, option_map = self._prepare_options(
            options, default, is_gui=True
        )

        cmd = ["dmenu", "-p", self.format_prompt(prompt)]

        if case_insensitive:
            cmd.append("-i")

        if row_count != 0:
            cmd.extend(["-l", str(row_count)])

        try:
            result = subprocess.run(
                cmd,
                input="\n".join(display_options),
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                selection = result.stdout.strip()
                return option_map.get(selection, default)
            return default

        except FileNotFoundError:
            log.error("Binary 'dmenu' not found.")
            return default
        except Exception as e:
            log.error(f"Dmenu command failed: {e}")
            return default


class ChoosePrompt(BasePrompt):
    """Choose implementation of the prompt interface."""

    def prompt(
        self,
        prompt: str,
        options: list[str],
        default: str | None = None,
        row_count: int = 10,
    ) -> str | None:
        if not options and not default:
            return None

        display_options, option_map = self._prepare_options(
            options, default, is_gui=True
        )

        cmd = ["choose", "-p", self.format_prompt(prompt)]

        if row_count != 0:
            cmd.extend(["-n", str(row_count)])

        try:
            result = subprocess.run(
                cmd,
                input="\n".join(display_options),
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                selection = result.stdout.strip()
                return option_map.get(selection, default)
            return default

        except FileNotFoundError:
            log.error("Binary 'choose' not found.")
            return default
        except Exception as e:
            log.error(f"Choose command failed: {e}")
            return default


class TerminalPrompt(BasePrompt):
    """Fallback standard terminal fallback implementation."""

    def prompt(
        self,
        prompt: str,
        options: list[str],
        default: str | None = None,
    ) -> str | None:
        if not options and not default:
            return None

        display_options, option_map = self._prepare_options(
            options, default, is_gui=False
        )

        options_str = "\n".join(
            [f"{i}. {option}" for i, option in enumerate(display_options)]
        )

        print(f":: {self.format_prompt(prompt)}:\n{options_str}")

        hint = f" [default: {default}]" if default else ""
        try:
            user_input = input(f"\n> Select an option{hint}: ").strip()
        except (KeyboardInterrupt, EOFError):
            return default

        if not user_input:
            return default

        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(display_options):
                return option_map.get(display_options[idx], default)

        # Allow fallback matching via typed string text
        return option_map.get(user_input, default)


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
    default: str | None = None,
    prefer_gui: bool = True,
    row_count: int = 0,
) -> str | None:
    """
    Orchestrates user prompting selection across GUI engines and standard terminal.
    """

    if not options and not default:
        return None

    if prefer_gui:
        if shutil.which("dmenu"):
            return DmenuPrompt().prompt(
                prompt=prompt,
                options=options,
                default=default,
                row_count=row_count,
            )
        if shutil.which("choose"):
            return ChoosePrompt().prompt(
                prompt=prompt,
                options=options,
                default=default,
                row_count=row_count,
            )

    return TerminalPrompt().prompt(
        prompt=prompt,
        options=options,
        default=default,
    )


def prompt_bool(
    prompt: str,
    default: bool | None = None,
    prefer_gui: bool = False,
) -> bool | None:
    """
    Prompts the user for a yes/no response.

    Returns:
        True if 'y', 'yes', '1', False if 'n', 'no', '0', otherwise the default value.
    """

    if prefer_gui:
        gui_default = None
        if default is True:
            gui_default = "Yes"
        elif default is False:
            gui_default = "No"

        user_input = prompt_options(
            prompt=prompt,
            options=["Yes", "No"],
            default=gui_default,
        )

        if user_input is None:
            return default

        user_input = user_input.lower()
    else:
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

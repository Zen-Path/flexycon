import os
from enum import Enum
from typing import Any, Callable

from common.logger import log

TERMINAL = os.getenv("TERMINAL", "alacritty")
EDITOR = os.getenv("EDITOR", "nvim")
STATUSBAR = os.getenv("STATUSBAR", "dwmblocks")


# TODO: Add more buttons
class MouseButton(Enum):
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    SCROLL_UP = 4
    SCROLL_DOWN = 5
    EXTRA_1 = 6
    EXTRA_2 = 7
    EXTRA_3 = 8


def handle_block_button(actions: dict[MouseButton, Callable[[], Any]]) -> bool:
    """Handle block button events."""
    block_button = os.getenv("BLOCK_BUTTON")
    if block_button is None:
        log.debug("Variable 'BLOCK_BUTTON' is not set.")
        return False

    try:
        button = MouseButton(int(block_button))
        log.debug(f"Handling button {button}.")
    except ValueError:
        log.warning(
            f"Invalid MouseButton value from 'BLOCK_BUTTON': {int(block_button)}."
        )
        return False

    action = actions.get(button)
    if not action:
        log.warning(f"Button {button} has no action defined.")
        return False

    action()

    return True

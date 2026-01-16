import os
from enum import Enum

from common.logger import logger

TERMINAL = os.environ.get("TERMINAL", "alacritty")
EDITOR = os.environ.get("EDITOR", "nvim")
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


def handle_block_button(actions):
    """Handle block button events."""
    block_button = os.environ.get("BLOCK_BUTTON")
    if not block_button:
        logger.debug("Variable BLOCK_BUTTON is not set.")
        return False

    try:
        button = MouseButton(int(block_button))
        logger.debug(f"Handling button {button}.")
    except ValueError:
        logger.warn(
            f"Value of BLOCK_BUTTON is {int(block_button)}, which is not a valid MouseButton value."
        )
        return False

    action = actions.get(button)
    if action:
        action()
    else:
        logger.warn(f"Button {button} doesn't have an associated action to it.")
        return False

    return True

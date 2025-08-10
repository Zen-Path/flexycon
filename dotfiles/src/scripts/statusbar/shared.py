import os
from enum import Enum

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

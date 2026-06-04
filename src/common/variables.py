import os
import sys
from enum import StrEnum
from pathlib import Path

# PATHS

# fmt: off
ROOT = Path("/")
HOME = Path.home()

# Home
XDG_DESKTOP_DIR     = HOME / "Desktop"
XDG_DOCUMENTS_DIR   = HOME / "Documents"
XDG_DOWNLOAD_DIR    = HOME / "Downloads"
XDG_MUSIC_DIR       = HOME / "Music"
XDG_PICTURES_DIR    = HOME / "Pictures"
XDG_VIDEOS_DIR      = HOME / "Movies" if sys.platform == "darwin" else HOME / "Videos"
XDG_PUBLICSHARE_DIR = HOME / "Public"

# Hidden
XDG_CACHE_HOME  = HOME / ".cache"
XDG_CONFIG_HOME = HOME / ".config"
XDG_BIN_HOME    = HOME / ".local" / "bin"
XDG_DATA_HOME   = HOME / ".local" / "share"
XDG_SRC_HOME    = HOME / ".local" / "src"

# Flexycon
FLEXYCON_HOME    = XDG_SRC_HOME  / "flexycon"
FLEXYCON_SCRIPTS = FLEXYCON_HOME / "src" / "scripts"
FLEXYCON_CONFIG  = FLEXYCON_HOME / "dotfiles" / "config"
FLEXYCON_DEPS    = FLEXYCON_HOME / "dotfiles" / "deps"
FLEXYCON_PRIVATE = XDG_SRC_HOME  / "flexycon-private"
FLEXYCON_DATA    = XDG_DATA_HOME / "flexycon"

JOURNAL_HOME    = XDG_DOCUMENTS_DIR / "Journal"
UNIVERSITY_HOME = HOME / "University"
# fmt: on

# When installing flexycon for the first time, env vars aren't set
# yet, so we want to provide a fallback, otherwise we want the
# shortcut consumer to decide weather to expand or not
flex_home_parts = (
    ["$FLEXYCON_HOME"]
    if os.getenv("FLEXYCON_HOME")
    else ["$HOME", ".local", "src", "flexycon"]
)

# COLORS

DARK_MODE = True
CONTRAST = "normal"


# fmt: off
class GB(StrEnum):
    DARK_0       = "#282828"
    DARK_0_HARD  = "#1d2021"
    DARK_0_SOFT  = "#32302f"
    DARK_1       = "#3c3836"
    DARK_2       = "#504945"
    DARK_3       = "#665c54"
    DARK_4       = "#7c6f64"
    #
    GRAY         = "#928374"
    #
    LIGHT_0      = "#fbf1c7"
    LIGHT_0_HARD = "#f9f5d7"
    LIGHT_0_SOFT = "#f2e5bc"
    LIGHT_1      = "#ebdbb2"
    LIGHT_2      = "#d5c4a1"
    LIGHT_3      = "#bdae93"
    LIGHT_4      = "#a89984"
    #
    BRIGHT_RED     = "#fb4934"
    BRIGHT_GREEN   = "#b8bb26"
    BRIGHT_YELLOW  = "#fabd2f"
    BRIGHT_BLUE    = "#83a598"
    BRIGHT_PURPLE  = "#d3869b"
    BRIGHT_AQUA    = "#8ec07c"
    BRIGHT_ORANGE  = "#fe8019"
    #
    NEUTRAL_RED    = "#cc241d"
    NEUTRAL_GREEN  = "#98971a"
    NEUTRAL_YELLOW = "#d79921"
    NEUTRAL_BLUE   = "#458588"
    NEUTRAL_PURPLE = "#b16286"
    NEUTRAL_AQUA   = "#689d6a"
    NEUTRAL_ORANGE = "#d65d0e"
    #
    FADED_RED      = "#9d0006"
    FADED_GREEN    = "#79740e"
    FADED_YELLOW   = "#b57614"
    FADED_BLUE     = "#076678"
    FADED_PURPLE   = "#8f3f71"
    FADED_AQUA     = "#427b58"
    FADED_ORANGE   = "#af3a03"

# fmt: on

COLOR_WHITE = "#FFFFFF"
COLOR_BLACK = "#000000"

# ENVIRONMENT VARIABLES

EDITOR = os.getenv("EDITOR", "nvim")
TERMINAL = os.getenv("TERMINAL", "alacritty")
STATUSBAR = os.getenv("STATUSBAR", "dwmblocks")

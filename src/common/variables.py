import os
from pathlib import Path

# fmt: off
HOME = Path.home()

# Home
XDG_DESKTOP_DIR     = HOME / "Desktop"
XDG_DOCUMENTS_DIR   = HOME / "Documents"
XDG_DOWNLOAD_DIR    = HOME / "Downloads"
XDG_MUSIC_DIR       = HOME / "Music"
XDG_PICTURES_DIR    = HOME / "Pictures"
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

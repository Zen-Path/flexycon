import os
import sys
from pathlib import Path

from common.variables import (
    FLEXYCON_CONFIG,
    FLEXYCON_DEPS,
    FLEXYCON_HOME,
    FLEXYCON_SCRIPTS,
    HOME,
    JOURNAL_HOME,
    ROOT,
    UNIVERSITY_HOME,
    XDG_BIN_HOME,
    XDG_CACHE_HOME,
    XDG_CONFIG_HOME,
    XDG_DATA_HOME,
    XDG_DESKTOP_DIR,
    XDG_DOCUMENTS_DIR,
    XDG_DOWNLOAD_DIR,
    XDG_MUSIC_DIR,
    XDG_PICTURES_DIR,
    XDG_SRC_HOME,
    XDG_VIDEOS_DIR,
)
from scripts.user_shortcuts.src.models import Shortcut
from scripts.user_shortcuts.src.renderers import YAZI

system = sys.platform


shortcuts: list[Shortcut] = [
    # Home
    Shortcut(
        type="d",
        path=HOME,
        alias_map={"default": ["h"]},
        description="home",
    ),
    Shortcut(
        type="d",
        path=XDG_CACHE_HOME,
        alias_map={"default": ["c", "a", "c"]},
        description="user cache",
    ),
    Shortcut(
        type="f",
        path=HOME / ".zprofile",
        alias_map={"default": ["c", "s", "p"]},
        description="shell profile",
    ),
    Shortcut(
        type="d",
        path=XDG_DESKTOP_DIR,
        alias_map={"default": ["d", "e", "s"], YAZI.name: ["D", "t"]},
        description="desktop",
    ),
    Shortcut(
        type="d",
        path=XDG_DOCUMENTS_DIR,
        alias_map={"default": ["d", "o", "c"], YAZI.name: ["d"]},
        description="documents",
    ),
    Shortcut(
        type="d",
        path=XDG_DOWNLOAD_DIR,
        alias_map={"default": ["d", "w", "n"], YAZI.name: ["D", "l"]},
        description="downloads",
    ),
    Shortcut(
        type="d",
        path=XDG_MUSIC_DIR,
        alias_map={"default": ["m", "u", "s"], YAZI.name: ["m"]},
        description="music",
    ),
    Shortcut(
        type="d",
        path=XDG_PICTURES_DIR,
        alias_map={"default": ["i", "m", "g"], YAZI.name: ["i"]},
        description="images",
    ),
    # TODO: For macOS - make sure
    # `defaults read com.apple.screencapture location`
    # returns '~/Pictures/Screenshots', otherwise set it.
    Shortcut(
        type="d",
        path=XDG_PICTURES_DIR / "Screenshots",
        alias_map={"default": ["i", "m", "g", "s"], YAZI.name: ["I", "s"]},
        description="screenshots",
    ),
    Shortcut(
        type="d",
        path=XDG_PICTURES_DIR / "Wallpapers",
        alias_map={"default": ["i", "m", "g", "w"], YAZI.name: ["I", "w"]},
        description="wallpapers",
    ),
    Shortcut(
        type="d",
        path=XDG_VIDEOS_DIR,
        alias_map={"default": ["v", "i", "d"], YAZI.name: ["v"]},
        description="videos",
    ),
    # University
    Shortcut(
        type="d",
        path=UNIVERSITY_HOME,
        alias_map={"default": ["u", "n", "i"], YAZI.name: ["U"]},
        activate_python_env=True,
        description="university",
    ),
    Shortcut(
        type="f",
        path=UNIVERSITY_HOME / "Timetable",
        alias_map={"default": ["u", "n", "i", "t"], YAZI.name: ["u", "t"]},
        description="university timetable",
    ),
    Shortcut(
        type="d",
        path=UNIVERSITY_HOME / "Semester",
        alias_map={"default": ["u", "n", "i", "s"], YAZI.name: ["u", "s"]},
        activate_python_env=True,
        description="university current semester",
    ),
    # Library
    Shortcut(
        type="d",
        path=HOME / "Library",
        alias_map={"default": ["l", "i", "b"], YAZI.name: ["L"]},
        description="library",
        condition=system == "darwin",
    ),
    Shortcut(
        type="d",
        path=HOME / "Library" / "Application Support",
        alias_map={"default": ["l", "i", "b", "s"], YAZI.name: ["l", "s"]},
        description="library application support",
        condition=system == "darwin",
    ),
    Shortcut(
        type="d",
        path=HOME / "Library" / "Application Support" / "Code",
        alias_map={"default": ["l", "i", "b", "v"], YAZI.name: ["l", "v"]},
        description="library vscode",
        condition=system == "darwin",
    ),
    Shortcut(
        type="d",
        path=HOME / "Library" / "Application Support" / "Firefox",
        alias_map={"default": ["l", "i", "b", "f"], YAZI.name: ["l", "f"]},
        description="library firefox",
        condition=system == "darwin",
    ),
    # User Config
    Shortcut(
        type="d",
        path=XDG_CONFIG_HOME,
        alias_map={"default": ["u", "c"], YAZI.name: ["C"]},
        description="user configs",
    ),
    ## Flexycon
    Shortcut(
        type="d",
        path=XDG_CONFIG_HOME / "flexycon",
        alias_map={"default": ["u", "c", "f"]},
        description="user config flexycon",
    ),
    Shortcut(
        type="d",
        path=XDG_CONFIG_HOME / "flexycon" / "userscripts",
        alias_map={"default": ["u", "c", "f", "u"]},
        description="user config flexycon processed userscripts",
    ),
    ## Firefox
    Shortcut(
        type="d",
        path=XDG_CONFIG_HOME / "firefox",
        alias_map={"default": ["u", "c", "F"]},
        description="user config firefox",
    ),
    ## Git
    Shortcut(
        type="d",
        path=XDG_CONFIG_HOME / "git",
        alias_map={"default": ["u", "c", "g"]},
        description="user config git",
    ),
    ## NeoVim
    Shortcut(
        type="d",
        path=XDG_CONFIG_HOME / "nvim",
        alias_map={"default": ["u", "c", "n"]},
        description="user config nvim",
    ),
    ## Newsraft
    Shortcut(
        type="d",
        path=XDG_CONFIG_HOME / "newsraft",
        alias_map={"default": ["u", "c", "N"]},
        description="user config newsraft",
    ),
    Shortcut(
        type="f",
        path=XDG_CONFIG_HOME / "newsraft" / "feeds",
        alias_map={"default": ["u", "c", "N", "f"]},
        description="user config newsraft feeds",
    ),
    ## Shell
    Shortcut(
        type="d",
        path=XDG_CONFIG_HOME / "shell",
        alias_map={"default": ["u", "c", "s"]},
        description="user config shell",
    ),
    ## Yazi
    Shortcut(
        type="d",
        path=XDG_CONFIG_HOME / "yazi",
        alias_map={"default": ["u", "c", "y"]},
        description="user config yazi",
    ),
    # Local
    Shortcut(
        type="d",
        path=XDG_BIN_HOME,
        alias_map={"default": ["b", "i", "n"], YAZI.name: ["b"]},
        description="local bins",
    ),
    Shortcut(
        type="d",
        path=XDG_DATA_HOME,
        alias_map={"default": ["d", "a", "t"], YAZI.name: ["l", "d"]},
        description="local data",
    ),
    # Sources
    Shortcut(
        type="d",
        path=XDG_SRC_HOME,
        alias_map={"default": ["s", "r", "c"], YAZI.name: ["S"]},
        description="user sources",
    ),
    Shortcut(
        type="d",
        path=XDG_SRC_HOME / "docs",
        alias_map={"default": ["s", "r", "c", "d"]},
        activate_python_env=True,
        description="documents source",
    ),
    Shortcut(
        type="d",
        path=XDG_SRC_HOME / "flexycon-private",
        alias_map={"default": ["p", "r", "v"], YAZI.name: ["P"]},
        activate_python_env=True,
        description="private config source",
    ),
    Shortcut(
        type="d",
        path=XDG_SRC_HOME / "media-server",
        alias_map={"default": ["m", "s", "r", "v"]},
        activate_python_env=True,
        description="flexycon dotfile scripts",
    ),
    # Flexycon
    Shortcut(
        type="d",
        path=FLEXYCON_HOME,
        alias_map={"default": ["f", "l", "x"], YAZI.name: ["F"]},
        activate_python_env=True,
        description="flexycon home",
    ),
    ## Config
    Shortcut(
        type="d",
        path=FLEXYCON_CONFIG,
        alias_map={"default": ["f", "l", "x", "c"], YAZI.name: ["f", "c"]},
        activate_python_env=True,
        description="flexycon dotfile configs",
    ),
    ### Firefox
    Shortcut(
        type="d",
        path=FLEXYCON_CONFIG / "firefox",
        alias_map={"default": ["f", "c", "f"]},
        activate_python_env=True,
        description="flexycon firefox",
    ),
    ### Git
    Shortcut(
        type="d",
        path=FLEXYCON_CONFIG / "git",
        alias_map={"default": ["f", "c", "g"]},
        activate_python_env=True,
        description="flexycon git",
    ),
    ### NeoVim
    Shortcut(
        type="d",
        path=FLEXYCON_CONFIG / "nvim",
        alias_map={"default": ["f", "c", "n"]},
        activate_python_env=True,
        description="flexycon nvim",
    ),
    Shortcut(
        type="f",
        path=FLEXYCON_CONFIG / "nvim" / "init.lua",
        alias_map={"default": ["f", "c", "n", "i"]},
        activate_python_env=True,
        description="flexycon nvim init.lua",
    ),
    ### Newsraft
    Shortcut(
        type="d",
        path=FLEXYCON_CONFIG / "newsraft",
        alias_map={"default": ["f", "c", "N"]},
        activate_python_env=True,
        description="flexycon newsraft",
    ),
    ### Shell
    Shortcut(
        type="d",
        path=FLEXYCON_CONFIG / "shell",
        alias_map={"default": ["f", "c", "s"]},
        activate_python_env=True,
        description="flexycon shell config",
    ),
    ### Yazi
    Shortcut(
        type="d",
        path=FLEXYCON_CONFIG / "yazi",
        alias_map={"default": ["f", "c", "y"]},
        activate_python_env=True,
        description="flexycon yazi",
    ),
    Shortcut(
        type="d",
        path=FLEXYCON_CONFIG / "yazi" / "plugins",
        alias_map={"default": ["f", "c", "y", "p"]},
        activate_python_env=True,
        description="flexycon yazi plugins",
    ),
    Shortcut(
        type="f",
        path=FLEXYCON_CONFIG / "yazi" / "keymap.toml",
        alias_map={"default": ["f", "c", "y", "k"]},
        activate_python_env=True,
        description="flexycon yazi keymap.toml",
    ),
    ## Scripts
    Shortcut(
        type="d",
        path=FLEXYCON_SCRIPTS,
        alias_map={"default": ["f", "l", "x", "s"], YAZI.name: ["f", "s"]},
        activate_python_env=True,
        description="flexycon dotfile scripts",
    ),
    Shortcut(
        type="f",
        path=FLEXYCON_SCRIPTS / "user_shortcuts" / "data" / "shortcuts.py",
        alias_map={"default": ["s", "h", "r", "t"], YAZI.name: ["s", "c"]},
        activate_python_env=True,
        description="user shortcuts data",
    ),
    Shortcut(
        type="d",
        path=FLEXYCON_DEPS,
        alias_map={"default": ["f", "l", "x", "D"], YAZI.name: ["f", "D", "f"]},
        description="flexycon deps",
    ),
    Shortcut(
        type="d",
        path=FLEXYCON_DEPS / "dwm-flexipatch",
        alias_map={"default": ["s", "r", "c", "d"], YAZI.name: ["f", "D", "d"]},
        description="dwm-flexypatch source",
    ),
    Shortcut(
        type="d",
        path=FLEXYCON_DEPS / "dwmblocks-async",
        alias_map={"default": ["s", "r", "c", "D"], YAZI.name: ["f", "D", "D"]},
        description="dwmblocks-async source",
    ),
    # Misc
    Shortcut(
        type="d",
        path=JOURNAL_HOME,
        alias_map={"default": ["j", "r", "d"], YAZI.name: ["J"]},
        description="journal",
    ),
    Shortcut(
        type="d",
        path=ROOT / "mnt",
        alias_map={"default": ["m", "n"], YAZI.name: ["M"]},
        description="mount",
        condition=system == "linux",
    ),
    Shortcut(
        type="d",
        path=ROOT / "Volumes",
        alias_map={"default": ["v", "o", "l"], YAZI.name: ["V"]},
        description="volumes",
        condition=system == "darwin",
    ),
    Shortcut(
        type="d",
        path=Path(os.getenv("APPDATA", "")),
        alias_map={"default": ["a", "p", "p", "d"], YAZI.name: ["A"]},
        description="app data",
        condition=system == "win32",
    ),
]

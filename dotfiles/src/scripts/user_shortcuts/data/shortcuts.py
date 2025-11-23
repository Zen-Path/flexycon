import platform
from typing import List

from common.variables import flex_home_parts
from scripts.user_shortcuts.src.models import Bookmark
from scripts.user_shortcuts.src.renderers import YAZI

system = platform.system()

flex_dotfiles = flex_home_parts + ["dotfiles"]
flex_config = flex_dotfiles + ["config"]
flex_scripts = flex_dotfiles + ["src", "scripts"]

shortcuts: List[Bookmark] = [
    # Home
    Bookmark(
        type="d",
        path_parts=["$HOME"],
        aliases={"default": ["h"]},
        description="home",
    ),
    Bookmark(
        type="d",
        path_parts=["$XDG_CACHE_HOME"],
        aliases={"default": ["c", "a", "c"]},
        description="user cache",
    ),
    Bookmark(
        type="f",
        path_parts=["$HOME", ".zprofile"],
        aliases={"default": ["c", "s", "p"]},
        description="shell profile",
    ),
    Bookmark(
        type="d",
        path_parts=["$XDG_DOCUMENTS_DIR"],
        aliases={"default": ["d", "o", "c"], YAZI.name: ["d"]},
        description="documents",
    ),
    Bookmark(
        type="d",
        path_parts=["$XDG_DOWNLOAD_DIR"],
        aliases={"default": ["d", "w", "n"], YAZI.name: ["D"]},
        description="downloads",
    ),
    Bookmark(
        type="d",
        path_parts=["$XDG_MUSIC_DIR"],
        aliases={"default": ["m", "u", "s"], YAZI.name: ["m"]},
        description="music",
    ),
    Bookmark(
        type="d",
        path_parts=["$XDG_PICTURES_DIR"],
        aliases={"default": ["i", "m", "g"], YAZI.name: ["i"]},
        description="images",
    ),
    Bookmark(
        type="d",
        path_parts=["$XDG_VIDEOS_DIR"],
        aliases={"default": ["v", "i", "d"], YAZI.name: ["v"]},
        description="videos",
    ),
    # University
    Bookmark(
        type="d",
        path_parts=["$HOME", "University"],
        aliases={"default": ["u", "n", "i"], YAZI.name: ["U"]},
        description="university",
    ),
    Bookmark(
        type="f",
        path_parts=["$HOME", "University", "Timetable"],
        aliases={"default": ["u", "n", "i", "t"], YAZI.name: ["u", "t"]},
        description="university timetable",
    ),
    Bookmark(
        type="d",
        path_parts=["$HOME", "University", "Y1_S1"],
        aliases={"default": ["u", "n", "i", "s"], YAZI.name: ["u", "s"]},
        description="university current semester",
    ),
    # Library
    Bookmark(
        type="d",
        path_parts=["$HOME", "Library"],
        aliases={"default": ["l", "i", "b"], YAZI.name: ["L"]},
        description="library",
        condition=system == "Darwin",
    ),
    Bookmark(
        type="d",
        path_parts=["$HOME", "Library", "Application Support"],
        aliases={"default": ["l", "i", "b", "s"], YAZI.name: ["l", "s"]},
        description="library application support",
        condition=system == "Darwin",
    ),
    Bookmark(
        type="d",
        path_parts=["$HOME", "Library", "Application Support", "Code"],
        aliases={"default": ["l", "i", "b", "v"], YAZI.name: ["l", "v"]},
        description="library vscode",
        condition=system == "Darwin",
    ),
    Bookmark(
        type="d",
        path_parts=["$HOME", "Library", "Application Support", "Firefox"],
        aliases={"default": ["l", "i", "b", "f"], YAZI.name: ["l", "f"]},
        description="library firefox",
        condition=system == "Darwin",
    ),
    # User Config
    Bookmark(
        type="d",
        path_parts=["$XDG_CONFIG_HOME"],
        aliases={"default": ["u", "c"], YAZI.name: ["C"]},
        description="user configs",
    ),
    ## Flexycon
    Bookmark(
        type="d",
        path_parts=["$XDG_CONFIG_HOME", "flexycon"],
        aliases={"default": ["u", "c", "f"]},
        description="user config flexycon",
    ),
    Bookmark(
        type="d",
        path_parts=["$XDG_CONFIG_HOME", "flexycon", "userscripts"],
        aliases={"default": ["u", "c", "f", "u"]},
        description="user config flexycon processed userscripts",
    ),
    ## Firefox
    Bookmark(
        type="d",
        path_parts=["$XDG_CONFIG_HOME", "firefox"],
        aliases={"default": ["u", "c", "F"]},
        description="user config firefox",
    ),
    ## Git
    Bookmark(
        type="d",
        path_parts=["$XDG_CONFIG_HOME", "git"],
        aliases={"default": ["u", "c", "g"]},
        description="user config git",
    ),
    ## NeoVim
    Bookmark(
        type="d",
        path_parts=["$XDG_CONFIG_HOME", "nvim"],
        aliases={"default": ["u", "c", "n"]},
        description="user config nvim",
    ),
    ## Newsraft
    Bookmark(
        type="d",
        path_parts=["$XDG_CONFIG_HOME", "newsraft"],
        aliases={"default": ["u", "c", "N"]},
        description="user config newsraft",
    ),
    Bookmark(
        type="f",
        path_parts=["$XDG_CONFIG_HOME", "newsraft", "feeds"],
        aliases={"default": ["u", "c", "N", "f"]},
        description="user config newsraft feeds",
    ),
    ## Shell
    Bookmark(
        type="d",
        path_parts=["$XDG_CONFIG_HOME", "shell"],
        aliases={"default": ["u", "c", "s"]},
        description="user config shell",
    ),
    ## Yazi
    Bookmark(
        type="d",
        path_parts=["$XDG_CONFIG_HOME", "yazi"],
        aliases={"default": ["u", "c", "y"]},
        description="user config yazi",
    ),
    # Local
    Bookmark(
        type="d",
        path_parts=["$XDG_BIN_HOME"],
        aliases={"default": ["b", "i", "n"], YAZI.name: ["b"]},
        description="local bins",
    ),
    Bookmark(
        type="d",
        path_parts=["$XDG_DATA_HOME"],
        aliases={"default": ["d", "a", "t"], YAZI.name: ["l", "d"]},
        description="local data",
    ),
    # Sources
    Bookmark(
        type="d",
        path_parts=["$XDG_SRC_HOME"],
        aliases={"default": ["s", "r", "c"], YAZI.name: ["S"]},
        description="user sources",
    ),
    Bookmark(
        type="d",
        path_parts=["$XDG_SRC_HOME", "docs"],
        aliases={"default": ["s", "r", "c", "d"]},
        activate_python_env=True,
        description="documents source",
    ),
    Bookmark(
        type="d",
        path_parts=["$XDG_SRC_HOME", "flexycon-private"],
        aliases={"default": ["p", "r", "v"], YAZI.name: ["P"]},
        description="private config source",
    ),
    # Flexycon
    Bookmark(
        type="d",
        path_parts=[*flex_home_parts],
        aliases={"default": ["f", "l", "x"], YAZI.name: ["F"]},
        activate_python_env=True,
        description="flexycon home",
    ),
    ## Config
    Bookmark(
        type="d",
        path_parts=[*flex_config],
        aliases={"default": ["f", "l", "x", "c"], YAZI.name: ["f", "c"]},
        activate_python_env=True,
        description="flexycon dotfile configs",
    ),
    ### Firefox
    Bookmark(
        type="d",
        path_parts=[*flex_config, "firefox"],
        aliases={"default": ["f", "c", "f"]},
        description="flexycon firefox",
    ),
    ### Git
    Bookmark(
        type="d",
        path_parts=[*flex_config, "git"],
        aliases={"default": ["f", "c", "g"]},
        description="flexycon git",
    ),
    ### NeoVim
    Bookmark(
        type="d",
        path_parts=[*flex_config, "nvim"],
        aliases={"default": ["f", "c", "n"]},
        description="flexycon nvim",
    ),
    Bookmark(
        type="f",
        path_parts=[*flex_config, "nvim", "init.lua"],
        aliases={"default": ["f", "c", "n", "i"]},
        description="flexycon nvim init.lua",
    ),
    ### Newsraft
    Bookmark(
        type="d",
        path_parts=[*flex_config, "newsraft"],
        aliases={"default": ["f", "c", "N"]},
        description="flexycon newsraft",
    ),
    ### Shell
    Bookmark(
        type="d",
        path_parts=[*flex_config, "shell"],
        aliases={"default": ["f", "c", "s"]},
        description="flexycon shell config",
    ),
    ### Yazi
    Bookmark(
        type="d",
        path_parts=[*flex_config, "yazi"],
        aliases={"default": ["f", "c", "y"]},
        description="flexycon yazi",
    ),
    Bookmark(
        type="d",
        path_parts=[*flex_config, "yazi", "plugins"],
        aliases={"default": ["f", "c", "y", "p"]},
        description="flexycon yazi plugins",
    ),
    Bookmark(
        type="f",
        path_parts=[*flex_config, "yazi", "keymap.toml"],
        aliases={"default": ["f", "c", "y", "k"]},
        description="flexycon yazi keymap.toml",
    ),
    ## Scripts
    Bookmark(
        type="d",
        path_parts=[*flex_scripts],
        aliases={"default": ["f", "l", "x", "s"], YAZI.name: ["f", "s"]},
        activate_python_env=True,
        description="flexycon dotfile scripts",
    ),
    Bookmark(
        type="d",
        path_parts=[*flex_scripts, "media_server"],
        aliases={"default": ["f", "s", "m"]},
        description="flexycon dotfile scripts",
    ),
    Bookmark(
        type="f",
        path_parts=[*flex_scripts, "user_shortcuts", "data", "shortcuts.py"],
        aliases={"default": ["s", "h", "r", "t"], YAZI.name: ["s", "c"]},
        description="user shortcuts data",
    ),
    # Misc
    Bookmark(
        type="d",
        path_parts=["$JOURNAL_HOME"],
        aliases={"default": ["j", "r", "d"], YAZI.name: ["J"]},
        description="journal",
    ),
    Bookmark(
        type="d",
        path_parts=["/", "mnt"],
        aliases={"default": ["m", "n"], YAZI.name: ["M"]},
        description="mount",
        condition=system == "Linux",
    ),
    Bookmark(
        type="d",
        path_parts=["/", "Volumes"],
        aliases={"default": ["v", "o", "l"], YAZI.name: ["V"]},
        description="volumes",
        condition=system == "Darwin",
    ),
]

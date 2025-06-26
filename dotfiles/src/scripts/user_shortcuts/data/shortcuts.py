from typing import List

from scripts.user_shortcuts.src.models import Bookmark
from scripts.user_shortcuts.src.renderers import YAZI

flex_home = ["$FLEXYCON_HOME"]
flex_dotfiles = flex_home + ["dotfiles"]
flex_config = flex_dotfiles + ["config"]
flex_scripts = flex_dotfiles + ["src", "scripts"]

shortcuts: List[Bookmark] = [
    # Home
    ## Standard
    Bookmark(
        type="d",
        path_parts=["$HOME"],
        aliases={"default": ["h"]},
        description="home",
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
    ## Custom
    Bookmark(
        type="d",
        path_parts=["$HOME", "Archive"],
        aliases={"default": ["a", "r", "c"], YAZI.name: ["a"]},
        description="archive",
    ),
    Bookmark(
        type="d",
        path_parts=["$HOME", "Entertainment"],
        aliases={"default": ["e", "n", "t"], YAZI.name: ["e"]},
        description="entertainment",
    ),
    Bookmark(
        type="d",
        path_parts=["$HOME", "Nerdy"],
        aliases={"default": ["n", "r", "d"], YAZI.name: ["n"]},
        description="nerdy",
    ),
    ## Extra
    Bookmark(
        type="d",
        path_parts=["$XDG_CACHE_HOME"],
        aliases={"default": ["c", "a", "c"]},
        description="caches",
    ),
    # Library
    Bookmark(
        type="d",
        path_parts=["$HOME", "Library"],
        aliases={"default": ["l", "i", "b"], YAZI.name: ["L"]},
        description="library",
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
        path_parts=["$HOME", "University", "Timetable.pdf"],
        aliases={"default": ["u", "n", "i", "t"], YAZI.name: ["u", "t"]},
        description="university timetable",
    ),
    Bookmark(
        type="d",
        path_parts=["$HOME", "University", "Semester"],
        aliases={"default": ["u", "n", "i", "s"], YAZI.name: ["u", "s"]},
        description="university semester",
    ),
    # Configs
    Bookmark(
        type="d",
        path_parts=["$XDG_CONFIG_HOME"],
        aliases={"default": ["c", "f"], YAZI.name: ["C"]},
        description="configs",
    ),
    ## Shell
    Bookmark(
        type="d",
        path_parts=["$XDG_CONFIG_HOME", "shell"],
        aliases={"default": ["c", "s", "d"]},
        description="shell config",
    ),
    Bookmark(
        type="f",
        path_parts=[*flex_config, "shell", "aliases.sh"],
        aliases={"default": ["f", "s", "a"]},
        description="shell aliases.sh",
    ),
    Bookmark(
        type="f",
        path_parts=["$HOME", ".zprofile"],
        aliases={"default": ["c", "s", "p"]},
        description="shell profile",
    ),
    ## Git
    Bookmark(
        type="d",
        path_parts=["$XDG_CONFIG_HOME", "git"],
        aliases={"default": ["c", "g", "d"]},
        description="git config",
    ),
    Bookmark(
        type="f",
        path_parts=[*flex_config, "git", "config.ini"],
        aliases={"default": ["f", "g", "c"]},
        description="git config.init",
    ),
    ## Yazi
    Bookmark(
        type="d",
        path_parts=["$XDG_CONFIG_HOME", "yazi"],
        aliases={"default": ["c", "y", "d"]},
        description="yazi config",
    ),
    Bookmark(
        type="d",
        path_parts=["$XDG_CONFIG_HOME", "yazi", "plugins"],
        aliases={"default": ["c", "y", "p", "d"]},
        description="yazi plugins",
    ),
    Bookmark(
        type="f",
        path_parts=["$XDG_CONFIG_HOME", "yazi", "keymap.toml"],
        aliases={"default": ["c", "y", "k"]},
        description="yazi keymap.toml",
    ),
    Bookmark(
        type="f",
        path_parts=["$XDG_CONFIG_HOME", "yazi", "theme.toml"],
        aliases={"default": ["c", "y", "t"]},
        description="yazi theme.toml",
    ),
    Bookmark(
        type="f",
        path_parts=["$XDG_CONFIG_HOME", "yazi", "yazi.toml"],
        aliases={"default": ["c", "y", "y"]},
        description="yazi yazi.toml",
    ),
    ## NeoVim
    Bookmark(
        type="d",
        path_parts=["$XDG_CONFIG_HOME", "nvim"],
        aliases={"default": ["c", "n", "d"]},
        description="nvim config",
    ),
    Bookmark(
        type="f",
        path_parts=["$XDG_CONFIG_HOME", "nvim", "init.lua"],
        aliases={"default": ["c", "n", "i"]},
        description="nvim init.lua",
    ),
    ## Newsraft
    Bookmark(
        type="f",
        path_parts=["$XDG_CONFIG_HOME", "newsraft", "config"],
        aliases={"default": ["c", "N", "c"]},
        description="newsraft config",
    ),
    Bookmark(
        type="f",
        path_parts=["$XDG_CONFIG_HOME", "newsraft", "feeds"],
        aliases={"default": ["c", "N", "f"]},
        description="newsraft feeds",
    ),
    ## Firefox
    Bookmark(
        type="d",
        path_parts=["$HOME", "Library", "Application Support", "Firefox"],
        aliases={"default": ["l", "i", "b", "f"], YAZI.name: ["l", "f"]},
        description="firefox library",
    ),
    Bookmark(
        type="f",
        path_parts=[*flex_config, "firefox", "user.js"],
        aliases={"default": ["f", "F", "u"]},
        description="firefox user.js",
    ),
    Bookmark(
        type="d",
        path_parts=[*flex_config, "firefox", "chrome"],
        aliases={"default": ["f", "F", "c"]},
        description="firefox chrome",
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
        description="sources",
    ),
    Bookmark(
        type="d",
        path_parts=["$XDG_SRC_HOME", "wis"],
        aliases={"default": ["w", "i", "s"], YAZI.name: ["s", "w"]},
        description="wis source",
    ),
    Bookmark(
        type="d",
        path_parts=["$XDG_SRC_HOME", "md-scripts"],
        aliases={"default": ["m", "d", "d"], YAZI.name: ["s", "m", "d"]},
        description="mobile department scripts",
    ),
    Bookmark(
        type="d",
        path_parts=["$XDG_SRC_HOME", "private"],
        aliases={"default": ["p", "r", "v"], YAZI.name: ["P"]},
        description="private source",
    ),
    # Flexycon
    Bookmark(
        type="d",
        path_parts=[*flex_home],
        aliases={"default": ["f", "l", "x"], YAZI.name: ["F"]},
        description="flexycon home",
    ),
    Bookmark(
        type="d",
        path_parts=[*flex_config],
        aliases={"default": ["f", "l", "x", "c"], YAZI.name: ["f", "c"]},
        description="flexycon config",
    ),
    Bookmark(
        type="d",
        path_parts=[*flex_scripts],
        aliases={"default": ["f", "l", "x", "s"], YAZI.name: ["f", "s"]},
        description="flexycon scripts",
    ),
    Bookmark(
        type="f",
        path_parts=[*flex_scripts, "user_shortcuts", "src", "data.py"],
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
        path_parts=["/mnt"],
        aliases={"default": ["m", "n"], YAZI.name: ["M"]},
        description="mount",
    ),
    Bookmark(
        type="d",
        path_parts=["/Volumes"],
        aliases={"default": ["v", "o", "l"], YAZI.name: ["V"]},
        description="volumes",
    ),
]

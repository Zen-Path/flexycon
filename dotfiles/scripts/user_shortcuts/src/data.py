import os
from pathlib import Path
from typing import List

from src.core import Bookmark
from src.renderers import YAZI

flex_home = Path(
    os.getenv("FLEXYCON_HOME") or str(Path.home() / ".local" / "src" / "flexycon")
)
flex_dotfiles = flex_home / "dotfiles"
flex_config = flex_dotfiles / "config"
flex_scripts = flex_dotfiles / "scripts"

shortcuts: List[Bookmark] = [
    # Home
    ## Standard
    Bookmark(
        "d",
        ["$HOME"],
        {"default": ["h"]},
        "home",
    ),
    Bookmark(
        "d",
        ["$XDG_DOCUMENTS_DIR"],
        {"default": ["d", "o", "c"], YAZI.name: ["d"]},
        "documents",
    ),
    Bookmark(
        "d",
        ["$XDG_DOWNLOAD_DIR"],
        {"default": ["d", "w", "n"], YAZI.name: ["D"]},
        "downloads",
    ),
    Bookmark(
        "d",
        ["$XDG_MUSIC_DIR"],
        {"default": ["m", "u", "s"], YAZI.name: ["m"]},
        "music",
    ),
    Bookmark(
        "d",
        ["$XDG_PICTURES_DIR"],
        {"default": ["i", "m", "g"], YAZI.name: ["i"]},
        "images",
    ),
    Bookmark(
        "d",
        ["$XDG_VIDEOS_DIR"],
        {"default": ["v", "i", "d"], YAZI.name: ["v"]},
        "videos",
    ),
    ## Custom
    Bookmark(
        "d",
        ["$HOME", "Archive"],
        {"default": ["a", "r", "c"], YAZI.name: ["a"]},
        "archive",
    ),
    Bookmark(
        "d",
        ["$HOME", "Entertainment"],
        {"default": ["e", "n", "t"], YAZI.name: ["e"]},
        "entertainment",
    ),
    Bookmark(
        "d",
        ["$HOME", "Nerdy"],
        {"default": ["n", "r", "d"], YAZI.name: ["n"]},
        "nerdy",
    ),
    ## Extra
    Bookmark(
        "d",
        ["$XDG_CACHE_HOME"],
        {"default": ["c", "a", "c"]},
        "caches",
    ),
    # Library
    Bookmark(
        "d",
        ["$HOME", "Library"],
        {"default": ["l", "i", "b"], YAZI.name: ["L"]},
        "library",
    ),
    Bookmark(
        "d",
        ["$HOME", "Library", "Application Support", "Firefox"],
        {"default": ["l", "i", "b", "f"], YAZI.name: ["l", "f"]},
        "library firefox",
    ),
    # University
    Bookmark(
        "d",
        ["$HOME", "University"],
        {"default": ["u", "n", "i"], YAZI.name: ["U"]},
        "university",
    ),
    Bookmark(
        "f",
        ["$HOME", "University", "Timetable.pdf"],
        {"default": ["u", "n", "i", "t"], YAZI.name: ["u", "t"]},
        "university timetable",
    ),
    Bookmark(
        "d",
        ["$HOME", "University", "Semester"],
        {"default": ["u", "n", "i", "s"], YAZI.name: ["u", "s"]},
        "university semester",
    ),
    # Configs
    Bookmark(
        "d",
        ["$XDG_CONFIG_HOME"],
        {"default": ["c", "f"], YAZI.name: ["C"]},
        "configs",
    ),
    ## Shell
    Bookmark(
        "d",
        ["$XDG_CONFIG_HOME", "shell"],
        {"default": ["c", "s", "d"]},
        "configs",
    ),
    Bookmark(
        "f",
        ["$XDG_CONFIG_HOME", "shell", "aliases.sh"],
        {"default": ["c", "s", "a"]},
        "shell aliases.sh",
    ),
    Bookmark(
        "f",
        ["$HOME", ".zprofile"],
        {"default": ["c", "s", "p"]},
        "shell profile",
    ),
    ## Git
    Bookmark(
        "d",
        ["$XDG_CONFIG_HOME", "git"],
        {"default": ["c", "g", "d"]},
        "git config",
    ),
    Bookmark(
        "f",
        ["$XDG_CONFIG_HOME", "git", "config.ini"],
        {"default": ["c", "g", "c"]},
        "git config.init",
    ),
    ## Yazi
    Bookmark(
        "d",
        ["$XDG_CONFIG_HOME", "YAZI"],
        {"default": ["c", "y", "d"]},
        "YAZI config",
    ),
    Bookmark(
        "f",
        ["$XDG_CONFIG_HOME", "YAZI", "YAZI.toml"],
        {"default": ["c", "y", "y"]},
        "YAZI YAZI.toml",
    ),
    Bookmark(
        "f",
        ["$XDG_CONFIG_HOME", "YAZI", "keymap.toml"],
        {"default": ["c", "y", "k"]},
        "YAZI keymap.toml",
    ),
    ## NeoVim
    Bookmark(
        "d",
        ["$XDG_CONFIG_HOME", "nvim"],
        {"default": ["c", "n", "d"]},
        "nvim config",
    ),
    Bookmark(
        "f",
        ["$XDG_CONFIG_HOME", "nvim", "init.lua"],
        {"default": ["c", "n", "i"]},
        "nvim init.lua",
    ),
    ## Newsraft
    Bookmark(
        "f",
        ["$XDG_CONFIG_HOME", "newsraft", "config"],
        {"default": ["c", "N", "c"]},
        "newsraft config",
    ),
    Bookmark(
        "f",
        ["$XDG_CONFIG_HOME", "newsraft", "feeds"],
        {"default": ["c", "N", "f"]},
        "newsraft feeds",
    ),
    # Local
    Bookmark(
        "d",
        ["$XDG_BIN_HOME"],
        {"default": ["b", "i", "n"], YAZI.name: ["b"]},
        "local bins",
    ),
    Bookmark(
        "d",
        ["$XDG_DATA_HOME"],
        {"default": ["d", "a", "t"], YAZI.name: ["l", "d"]},
        "local data",
    ),
    # Sources
    Bookmark(
        "d",
        ["$XDG_SRC_HOME"],
        {"default": ["s", "r", "c"], YAZI.name: ["s"]},
        "sources",
    ),
    Bookmark(
        "d",
        ["$XDG_SRC_HOME", "private"],
        {"default": ["p", "r", "v"], YAZI.name: ["s", "p"]},
        "private source",
    ),
    Bookmark(
        "d",
        ["$XDG_SRC_HOME", "wis"],
        {"default": ["w", "i", "s"], YAZI.name: ["s", "w"]},
        "wis source",
    ),
    # Flexycon
    Bookmark(
        "d",
        [flex_home],
        {"default": ["f", "l", "x"], YAZI.name: ["F"]},
        "sources",
    ),
    Bookmark(
        "f",
        [flex_scripts, "user_shortcuts", "src", "data.py"],
        {"default": ["s", "h", "r", "t"]},
        "shell aliases.sh",
    ),
    # Misc
    Bookmark(
        "d",
        ["$JOURNAL_HOME"],
        {"default": ["j", "r", "d"], YAZI.name: ["J"]},
        "journal",
    ),
    Bookmark(
        "d",
        ["/mnt"],
        {"default": ["m", "n"], YAZI.name: ["M"]},
        "mount",
    ),
    # TODO: figure out if revealing today's journal entry is possible in YAZI
]

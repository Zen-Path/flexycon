#!/usr/bin/env python3

from __future__ import annotations

import argparse
import logging
import os
import shlex
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple, Union

# HELPERS

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )


def resolve_path(path_parts: List[str]) -> str:
    """Resolve a list of path parts into a single expanded string path."""
    return os.path.expandvars(os.path.join(*path_parts))


# CORE


@dataclass
class Bookmark:
    type: Literal["d", "f"]
    path_parts: List[str]
    aliases: Dict[str, Union[bool, List[str]]]
    description: Optional[str] = None

    @property
    def resolved_path(self) -> str:
        return resolve_path(self.path_parts)


class BookmarkRenderer(ABC):
    def __init__(
        self,
        name: str,
        path_parts: List[str],
        resolve_path: bool = False,
        escape_path: bool = False,
        indentation_level: int = 4,
    ):
        self.name = name
        self.path_parts = path_parts
        self.resolve_path = resolve_path
        self.escape_path = escape_path
        self.processed_bookmarks: Dict[str, Tuple[List[str], Bookmark]] = {}
        self.indentation = " " * indentation_level

    def process(self, bookmarks: List[Bookmark]) -> None:
        logger.info(f"[{self.name}] Processing bookmarks...")
        count = 0

        for i, bookmark in enumerate(bookmarks):
            alias_value = bookmark.aliases.get(
                self.name, bookmark.aliases.get("default", False)
            )
            if isinstance(alias_value, list):
                alias_str = "".join(alias_value)
                self.processed_bookmarks[alias_str] = [alias_value, bookmark]

                logger.debug(f"- Added alias '{alias_str}' for bookmark {i}")
                count += 1
            else:
                logger.debug(f"- Skipped bookmark {i} (no alias)")

        logger.info(f"[{self.name}] Processed {count} bookmark(s)")

        content = self.compose_file()
        self._write_output(content)

    def _get_path(self, bookmark: Bookmark) -> str:
        result = Path(*bookmark.path_parts)

        if self.resolve_path:
            result = resolve_path(result)

        result_str = str(result)

        if self.escape_path:
            result_str = shlex.quote(result_str)

        return result_str

    def _write_output(self, content: str) -> None:
        path = Path(resolve_path(self.path_parts))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

        logger.info(f"[{self.name}] Wrote file to {path}")

    def compose_bookmarks(self) -> str:
        lines = []
        for alias_str, [alias, bookmark] in self.processed_bookmarks.items():
            lines += [self.compose_bookmark(alias, bookmark)]
        return "\n".join(lines)

    def compose_file(self) -> str:
        return self.compose_bookmarks()

    @abstractmethod
    def compose_bookmark(self, alias: str, bookmark: Bookmark) -> str:
        pass


# RENDERERS


class ZshBookmarkRenderer(BookmarkRenderer):
    def compose_bookmark(
        self, alias: Union[List[str], bool], bookmark: Bookmark
    ) -> str:
        description_fmt = f"# {bookmark.description}\n" if bookmark.description else ""

        alias_cmd = "cd" if bookmark.type == "d" else "$EDITOR"
        alias_fmt = f'alias {"".join(alias):>5}="{alias_cmd} {self._get_path(bookmark)} && ls -A"'

        named_dirs_fmt = (
            f'\nhash -d {"".join(alias):>3}="{bookmark.resolved_path}"'
            if bookmark.type == "d"
            else ""
        )

        # Example:
        # # home
        # alias     h="cd /Users/home && ls -A"
        # hash -d   h=/Users/home

        return f"{description_fmt}{alias_fmt}{named_dirs_fmt}\n"


class VimBookmarkRenderer(BookmarkRenderer):
    def compose_bookmark(
        self, alias: Union[List[str], bool], bookmark: Bookmark
    ) -> str:
        description_fmt = f'" {bookmark.description}\n' if bookmark.description else ""
        return f'{description_fmt}cmap ;{alias} "{self._get_path(bookmark)}"'


class YaziBookmarkRenderer(BookmarkRenderer):
    def compose_bookmark(
        self, alias: Union[List[str], bool], bookmark: Bookmark
    ) -> str:
        description_fmt = (
            f"{'Open' if bookmark.type == 'd' else 'Reveal'} {bookmark.description} {'dir' if bookmark.type == 'd' else 'file'}"
            if bookmark.description
            else ""
        )

        # All yazi bookmarks should start with 'g'.
        alias = ["g"] + alias

        return f'    {{ on = {alias}, run = "cd {self._get_path(bookmark)}", desc = "{description_fmt}" }},'


# ENTRY POINT


def main():
    parser = argparse.ArgumentParser(
        description="Generate bookmarks for various tools."
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug output.")
    args = parser.parse_args()

    setup_logging(verbose=args.verbose)

    # Renderers
    zsh = ZshBookmarkRenderer(
        "ZSH", ["$XDG_CONFIG_HOME", "shell", "shortcuts.sh"], escape_path=True
    )
    nvim = VimBookmarkRenderer("NeoVim", ["$XDG_CONFIG_HOME", "nvim", "shortcuts.vim"])
    yazi = YaziBookmarkRenderer(
        "Yazi", ["$FLEXYCON_HOME", "dotfiles", "config", "yazi", "shortcuts.toml"]
    )

    # Bookmarks
    bookmarks: List[Bookmark] = [
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
            {"default": ["d", "o", "c"], yazi.name: ["d"]},
            "documents",
        ),
        Bookmark(
            "d",
            ["$XDG_DOWNLOAD_DIR"],
            {"default": ["d", "w", "n"], yazi.name: ["D"]},
            "downloads",
        ),
        Bookmark(
            "d",
            ["$XDG_MUSIC_DIR"],
            {"default": ["m", "u", "s"], yazi.name: ["m"]},
            "music",
        ),
        Bookmark(
            "d",
            ["$XDG_PICTURES_DIR"],
            {"default": ["i", "m", "g"], yazi.name: ["i"]},
            "images",
        ),
        Bookmark(
            "d",
            ["$XDG_VIDEOS_DIR"],
            {"default": ["v", "i", "d"], yazi.name: ["v"]},
            "videos",
        ),
        ## Custom
        Bookmark(
            "d",
            ["$HOME", "Archive"],
            {"default": ["a", "r", "c"], yazi.name: ["a"]},
            "archive",
        ),
        Bookmark(
            "d",
            ["$HOME", "Entertainment"],
            {"default": ["e", "n", "t"], yazi.name: ["e"]},
            "entertainment",
        ),
        Bookmark(
            "d",
            ["$HOME", "Nerdy"],
            {"default": ["n", "r", "d"], yazi.name: ["n"]},
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
            {"default": ["l", "i", "b"], yazi.name: ["L"]},
            "library",
        ),
        Bookmark(
            "d",
            ["$HOME", "Library", "Application Support", "Firefox"],
            {"default": ["l", "i", "b", "f"], yazi.name: ["l", "f"]},
            "library firefox",
        ),
        # University
        Bookmark(
            "d",
            ["$HOME", "University"],
            {"default": ["u", "n", "i"], yazi.name: ["U"]},
            "university",
        ),
        Bookmark(
            "f",
            ["$HOME", "University", "Timetable.pdf"],
            {"default": ["u", "n", "i", "t"], yazi.name: ["u", "t"]},
            "university timetable",
        ),
        Bookmark(
            "d",
            ["$HOME", "University", "Semester"],
            {"default": ["u", "n", "i", "s"], yazi.name: ["u", "s"]},
            "university semester",
        ),
        # Configs
        Bookmark(
            "d",
            ["$XDG_CONFIG_HOME"],
            {"default": ["c", "f"], yazi.name: ["C"]},
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
            ["$XDG_CONFIG_HOME", "yazi"],
            {"default": ["c", "y", "d"]},
            "yazi config",
        ),
        Bookmark(
            "f",
            ["$XDG_CONFIG_HOME", "yazi", "yazi.toml"],
            {"default": ["c", "y", "y"]},
            "yazi yazi.toml",
        ),
        Bookmark(
            "f",
            ["$XDG_CONFIG_HOME", "yazi", "keymap.toml"],
            {"default": ["c", "y", "k"]},
            "yazi keymap.toml",
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
            {"default": ["b", "i", "n"], yazi.name: ["b"]},
            "local bins",
        ),
        Bookmark(
            "d",
            ["$XDG_DATA_HOME"],
            {"default": ["d", "a", "t"], yazi.name: ["l", "d"]},
            "local data",
        ),
        # Sources
        Bookmark(
            "d",
            ["$XDG_SRC_HOME"],
            {"default": ["s", "r", "c"], yazi.name: ["s"]},
            "sources",
        ),
        Bookmark(
            "d",
            ["$XDG_SRC_HOME", "private"],
            {"default": ["p", "r", "v"], yazi.name: ["s", "p"]},
            "private source",
        ),
        Bookmark(
            "d",
            ["$XDG_SRC_HOME", "wis"],
            {"default": ["w", "i", "s"], yazi.name: ["s", "w"]},
            "wis source",
        ),
        # Misc
        Bookmark(
            "d",
            ["$FLEXYCON_HOME"],
            {"default": ["f", "l", "x"], yazi.name: ["F"]},
            "sources",
        ),
        Bookmark(
            "d",
            ["$JOURNAL_HOME"],
            {"default": ["j", "r", "d"], yazi.name: ["J"]},
            "journal",
        ),
        Bookmark(
            "d",
            ["mnt"],
            {"default": ["m", "n"], yazi.name: ["M"]},
            "mount",
        ),
        # TODO: figure out if revealing today's journal entry is possible in yazi
    ]

    for renderer in (zsh, nvim, yazi):
        renderer.process(bookmarks)


if __name__ == "__main__":
    main()

import platform
from typing import List

from common.logger import logger
from common.variables import flex_home_parts
from scripts.user_shortcuts.src.models import Bookmark, BookmarkRenderer

OPEN_COMMANDS = {
    "Darwin": "open",
    "Linux": "xdg-open",
}


class ZshBookmarkRenderer(BookmarkRenderer):
    def compose_bookmark(self, alias_segments: List[str], bookmark: Bookmark) -> str:
        """
        Target:
        # downloads
        alias dwn="cd /Users/user/Downloads && ls"
        hash -d dwn=/Users/user/Downloads
        """
        result = []
        if bookmark.description:
            result.append(f"# {bookmark.description}")

        path = self._get_path(bookmark)
        command = OPEN_COMMANDS.get(platform.system(), "$EDITOR")

        alias_name = "".join(alias_segments)
        alias_value = (
            f"cd {path} && ls" if bookmark.type == "d" else f"{command} {path}"
        )

        if bookmark.activate_python_env:
            if bookmark.type != "d":
                logger.warning(
                    f"Python env can only be activated for directory bookmarks: {bookmark}"
                )
            else:
                alias_value += " && penva"

        result.append(f'alias {alias_name}="{alias_value}"')

        if bookmark.type == "d":
            result.append(f"hash -d {alias_name}={path}")

        return "\n".join(result) + "\n"


ZSH = ZshBookmarkRenderer(
    "Zsh", [*flex_home_parts, "dotfiles", "config", "zsh", "shortcuts.sh"]
)


class NVimBookmarkRenderer(BookmarkRenderer):
    def compose_bookmark(self, alias_segments: List[str], bookmark: Bookmark) -> str:
        result = []
        if bookmark.description:
            result.append(f"-- {bookmark.description}")

        result.append(
            f"""vim.api.nvim_set_keymap(
    "c",
    ";{"".join(alias_segments)}",
    "{self._get_path(bookmark)}",
    {{ noremap = true }}
)"""
        )

        return "\n".join(result) + "\n"


NVIM = NVimBookmarkRenderer(
    "NeoVim",
    [*flex_home_parts, "dotfiles", "config", "nvim", "shortcuts.lua"],
    escape_path=False,
)


class YaziBookmarkRenderer(BookmarkRenderer):
    def compose_bookmark(self, alias_segments: List[str], bookmark: Bookmark) -> str:
        verb = "Open" if bookmark.type == "d" else "Reveal"
        type_readable = "dir" if bookmark.type == "d" else "file"
        description_fmt = (
            f"{verb} {bookmark.description} {type_readable}"
            if bookmark.description
            else ""
        )

        # All yazi bookmarks should start with 'b'.
        alias_segments = ["b"] + alias_segments
        path = self._get_path(bookmark)
        command = (
            f'"cd {path}"' if bookmark.type == "d" else f'["reveal {path}", "open"]'
        )

        return f'    {{ on = {alias_segments}, run = {command}, desc = "{description_fmt}" }},'


YAZI = YaziBookmarkRenderer(
    "Yazi", [*flex_home_parts, "dotfiles", "config", "yazi", "shortcuts.toml"]
)

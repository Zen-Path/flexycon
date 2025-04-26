from typing import List, Union

from src.core import Bookmark, BookmarkRenderer


class ZshBookmarkRenderer(BookmarkRenderer):
    def compose_bookmark(self, alias: List[str], bookmark: Bookmark) -> str:
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


ZSH = ZshBookmarkRenderer(
    "ZSH", ["$XDG_CONFIG_HOME", "shell", "shortcuts.sh"], escape_path=True
)


class NVimBookmarkRenderer(BookmarkRenderer):
    def compose_bookmark(self, alias_segments: List[str], bookmark: Bookmark) -> str:
        description_fmt = f'" {bookmark.description}\n' if bookmark.description else ""
        return f'{description_fmt}cmap ;{alias_segments} "{self._get_path(bookmark)}"'


NVIM = NVimBookmarkRenderer("NeoVim", ["$XDG_CONFIG_HOME", "nvim", "shortcuts.vim"])


class YaziBookmarkRenderer(BookmarkRenderer):
    def compose_bookmark(self, alias_segments: List[str], bookmark: Bookmark) -> str:
        verb = "Open" if bookmark.type == "d" else "Reveal"
        type_readable = "dir" if bookmark.type == "d" else "file"
        description_fmt = (
            f"{verb} {bookmark.description} {type_readable}"
            if bookmark.description
            else ""
        )

        # All yazi bookmarks should start with 'g'.
        alias_segments = ["g"] + alias_segments
        command = (
            f'"cd {self._get_path(bookmark)}"'
            if bookmark.type == "d"
            else f'["reveal {self._get_path(bookmark)}", "open"]'
        )

        return f'{self.indentation}{{ on = {alias_segments}, run = {command}, desc = "{description_fmt}" }},'

    def compose_file(self) -> str:
        # Add newline so we can comment out the import statement in keymap.toml
        return f"\n{self.indentation}# SHORTCUTS\n{self.compose_bookmarks()}\n"


YAZI = YaziBookmarkRenderer(
    "Yazi", ["$FLEXYCON_HOME", "dotfiles", "config", "yazi", "shortcuts.toml"]
)

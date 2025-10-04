import platform
from typing import List

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
        alias dwn="cd /Users/user/Downloads && ls -A"
        hash -d dwn=/Users/user/Downloads

        """
        result = []
        if bookmark.description:
            result.append(f"# {bookmark.description}")

        alias_name = "".join(alias_segments)
        path = self._get_path(bookmark)
        command = OPEN_COMMANDS.get(platform.system(), "$EDITOR")

        if bookmark.type == "d":
            result.append(f'alias {alias_name}="cd {path} && ls -A"')
            result.append(f"hash -d {alias_name}={path}")
        else:
            result.append(f'alias {alias_name}="{command} {path}"')

        return "\n".join(result) + "\n"


ZSH = ZshBookmarkRenderer(
    "Zsh", ["$FLEXYCON_HOME", "dotfiles", "config", "zsh", "shortcuts.sh"]
)


class NVimBookmarkRenderer(BookmarkRenderer):
    def compose_bookmark(self, alias_segments: List[str], bookmark: Bookmark) -> str:
        description_fmt = f'" {bookmark.description}\n' if bookmark.description else ""
        return f'{description_fmt}cmap ;{''.join(alias_segments)} "{self._get_path(bookmark)}"'


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

        # All yazi bookmarks should start with 'b'.
        alias_segments = ["b"] + alias_segments
        path = self._get_path(bookmark)
        command = (
            f'"cd {path}"' if bookmark.type == "d" else f'["reveal {path}", "open"]'
        )

        return f'{self.indentation}{{ on = {alias_segments}, run = {command}, desc = "{description_fmt}" }},'


YAZI = YaziBookmarkRenderer(
    "Yazi", ["$FLEXYCON_HOME", "dotfiles", "config", "yazi", "shortcuts.toml"]
)

import platform
from typing import List

from scripts.user_shortcuts.src.models import Bookmark, BookmarkRenderer


def get_target_command(bookmark):
    if bookmark.type == "d":
        return "cd"

    system = platform.system()
    commands = {
        "Darwin": "open",
        "Linux": "xdg-open",
    }

    # Default to $EDITOR if defined, otherwise "vi"
    return commands.get(system, "$EDITOR")


class ZshBookmarkRenderer(BookmarkRenderer):
    def compose_bookmark(self, alias_segments: List[str], bookmark: Bookmark) -> str:
        description_fmt = f"# {bookmark.description}\n" if bookmark.description else ""

        alias_name = "".join(alias_segments)

        # Shell keywords
        alias_keyword = "alias"
        hash_keyword = "hash -d"

        # Determine max width so the '=' line up
        max_keyword_len = max(len(alias_keyword), len(hash_keyword))

        alias_header = f"{alias_keyword:<{max_keyword_len}} {alias_name}"
        hash_header = f"{hash_keyword:<{max_keyword_len}} {alias_name}"

        target_command = get_target_command(bookmark)
        alias_definition = (
            f'{alias_header}="{target_command} {self._get_path(bookmark)} && ls -A"'
        )

        hash_definition = (
            f'\n{hash_header}="{bookmark.resolved_path}"'
            if bookmark.type == "d"
            else ""
        )

        # Example:
        # # home
        # alias   dwn="cd '$XDG_DOWNLOAD_DIR' && ls -A"
        # hash -d dwn="/Users/home/Downloads"

        return f"{description_fmt}{alias_definition}{hash_definition}\n"


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

        # All yazi bookmarks should start with 'b'.
        alias_segments = ["b"] + alias_segments
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

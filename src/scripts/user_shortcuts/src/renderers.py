import sys

from common.logger import log
from common.variables import flex_home_parts
from scripts.user_shortcuts.src.models import Shortcut, ShortcutRenderer

OPEN_COMMANDS = {
    "darwin": "open",
    "linux": "xdg-open",
}


class ZshShortcutRenderer(ShortcutRenderer):
    def compose_shortcut(self, alias_segments: list[str], shortcut: Shortcut) -> str:
        """
        Target:
        # downloads
        alias dwn="cd /Users/user/Downloads && ls"
        hash -d dwn=/Users/user/Downloads
        """
        result: list[str] = []
        if shortcut.description:
            result.append(f"# {shortcut.description}")

        path = self.get_path(shortcut)
        command = OPEN_COMMANDS.get(sys.platform, "$EDITOR")

        alias_name = "".join(alias_segments)
        alias_value = (
            f"cd {path} && ls" if shortcut.type == "d" else f"{command} {path}"
        )

        if shortcut.activate_python_env:
            if shortcut.type != "d":
                log.warning(
                    f"Python env can only be activated for directory shortcuts: {shortcut}"
                )
            else:
                alias_value += " && penva"

        result.append(f'alias {alias_name}="{alias_value}"')

        if shortcut.type == "d":
            result.append(f"hash -d {alias_name}={path}")

        return "\n".join(result) + "\n"


ZSH = ZshShortcutRenderer(
    "Zsh", [*flex_home_parts, "dotfiles", "config", "zsh", "shortcuts.sh"]
)


class NVimShortcutRenderer(ShortcutRenderer):
    def compose_shortcut(self, alias_segments: list[str], shortcut: Shortcut) -> str:
        result: list[str] = []
        if shortcut.description:
            result.append(f"-- {shortcut.description}")

        result.append(
            f"""vim.api.nvim_set_keymap(
    "c",
    ";{"".join(alias_segments)}",
    "{self.get_path(shortcut)}",
    {{ noremap = true }}
)"""
        )

        return "\n".join(result) + "\n"


NVIM = NVimShortcutRenderer(
    "NeoVim",
    [*flex_home_parts, "dotfiles", "config", "nvim", "shortcuts.lua"],
    escape_path=False,
)


class YaziShortcutRenderer(ShortcutRenderer):
    def compose_shortcut(self, alias_segments: list[str], shortcut: Shortcut) -> str:
        verb = "Open" if shortcut.type == "d" else "Reveal"
        type_readable = "dir" if shortcut.type == "d" else "file"
        description_fmt = (
            f"{verb} {shortcut.description} {type_readable}"
            if shortcut.description
            else ""
        )

        # All yazi shortcuts should start with 'b'.
        alias_segments = ["b"] + alias_segments
        path = self.get_path(shortcut)
        command = (
            f'"cd {path}"' if shortcut.type == "d" else f'["reveal {path}", "open"]'
        )

        return f'    {{ on = {alias_segments}, run = {command}, desc = "{description_fmt}" }},'


YAZI = YaziShortcutRenderer(
    "Yazi", [*flex_home_parts, "dotfiles", "config", "yazi", "shortcuts.toml"]
)

import json
import shlex
import sys

from common.variables import FLEXYCON_CONFIG
from scripts.user_shortcuts.src.models import Shortcut, ShortcutRenderer


class ZshShortcutRenderer(ShortcutRenderer):
    OPEN_COMMANDS = {
        "darwin": "open",
        "linux": "xdg-open",
    }

    def compose_shortcut(self, alias_segments: list[str], shortcut: Shortcut) -> str:
        result = ""
        if shortcut.description:
            result += f"# {shortcut.description}\n"

        path_str = str(shortcut.path)

        if shortcut.type == "d":
            func_body = f"cd {shlex.quote(path_str)} && ls"
            if shortcut.activate_python_env:
                func_body += " && penva"
        else:
            func_body = f"cd {shlex.quote(str(shortcut.path.parent))} && ls"
            if shortcut.activate_python_env:
                func_body += " && penva"

            command = self.OPEN_COMMANDS.get(sys.platform, "$EDITOR")
            func_body += f" && {command} {shlex.quote(path_str)}"

        func_name = "".join(alias_segments)

        # Render as a native shell function instead of an alias
        result += f"function {func_name}() {{\n"
        result += f"    {func_body}\n"
        result += "}\n"

        if shortcut.type == "d":
            result += f"hash -d {func_name}={shlex.quote(path_str)}\n"

        return result


ZSH = ZshShortcutRenderer("Zsh", FLEXYCON_CONFIG / "zsh" / "shortcuts.sh")


class NVimShortcutRenderer(ShortcutRenderer):
    def compose_shortcut(self, alias_segments: list[str], shortcut: Shortcut) -> str:
        result: list[str] = []
        if shortcut.description:
            result.append(f"-- {shortcut.description}")

        # For quotes from the nvim command line to be interpreted as-is, we have to
        # escape them. This results in \\\", which means we'll have a literal backslash,
        # followed by double quotes.
        path_fmt = str(shortcut.path).replace('"', '\\\\\\"')
        result.append(
            f"""vim.api.nvim_set_keymap(
    "c",
    ";{"".join(alias_segments)}",
    "{path_fmt}",
    {{ noremap = true }}
)"""
        )

        return "\n".join(result) + "\n"


NVIM = NVimShortcutRenderer("NeoVim", FLEXYCON_CONFIG / "nvim" / "shortcuts.lua")


class YaziShortcutRenderer(ShortcutRenderer):
    def compose_shortcut(self, alias_segments: list[str], shortcut: Shortcut) -> str:
        description_fmt = ""
        if shortcut.description:
            verb = "Open" if shortcut.type == "d" else "Reveal"
            type_readable = "dir" if shortcut.type == "d" else "file"
            description_fmt = f"{verb} {shortcut.description} {type_readable}"

        # All yazi shortcuts should start with 'b'.
        alias_segments = ["b"] + alias_segments

        path = str(shortcut.path).replace('"', '\\"')

        if shortcut.type == "d":
            # raw_run_command =
            run_value = json.dumps(f'cd "{path}"')
        else:
            run_value = json.dumps([f'reveal "{path}"', "open"])

        return f'    {{ on = {alias_segments}, run = {run_value}, desc = "{description_fmt}" }},'


YAZI = YaziShortcutRenderer("Yazi", FLEXYCON_CONFIG / "yazi" / "shortcuts.toml")

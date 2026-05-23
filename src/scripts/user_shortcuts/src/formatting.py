from colorama import Fore, Style, init

from common.string_utilities import truncate
from scripts.user_shortcuts.src.models import Shortcut

init(autoreset=True)

# Column widths
ALIASES_WIDTH = 20
TARGET_WIDTH = 60
DESCRIPTION_WIDTH = 25


def format_aliases(aliases: dict[str, list[str]]) -> str:
    """Format aliases like 'doc, d (Yazi)' if groups differ."""
    parts: list[str] = []
    for group, keys in aliases.items():
        joined = "".join(keys)
        if group != "default":
            parts.append(f"{joined} ({group})")
        else:
            parts.append(joined)
    return "; ".join(parts)


def get_default_alias(shortcut: Shortcut) -> str:
    """Return the first default alias (for sorting)."""
    return shortcut.alias_map.get("default", [""])[0]


def format_shortcuts(shortcuts: list[Shortcut]) -> str:
    groups = {"d": "Directories", "f": "Files"}
    by_type: dict[str, list[Shortcut]] = {t: [] for t in groups}
    for shortcut in shortcuts:
        by_type.get(shortcut.type, []).append(shortcut)

    lines: list[str] = []
    for t, heading in groups.items():
        if not by_type[t]:
            continue

        sorted_shortcuts = sorted(by_type[t], key=get_default_alias)

        lines.append(f"{Fore.BLUE}{heading}{Style.RESET_ALL}")
        lines.append(
            f"{'Aliases':{ALIASES_WIDTH}} {'Target':{TARGET_WIDTH}} Description"
        )
        lines.append("-" * (ALIASES_WIDTH + TARGET_WIDTH + DESCRIPTION_WIDTH))

        for shortcut in sorted_shortcuts:
            aliases = format_aliases(shortcut.alias_map)
            target = str(shortcut.path)
            target_display = truncate(target, TARGET_WIDTH)
            lines.append(
                f"{aliases:{ALIASES_WIDTH}} {target_display:{TARGET_WIDTH}} {shortcut.description}"
            )

        lines.append("")

    return "\n".join(lines)

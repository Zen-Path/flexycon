from tabulate import tabulate

from common.string_utilities import truncate
from common.variables import HOME
from scripts.user_shortcuts.src.models import Shortcut


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


def format_shortcuts(
    shortcuts: list[Shortcut],
    target_col_width: int = 60,
    description_col_width: int = 25,
) -> str:
    """
    Display shortcuts in a table, containing the type, alias, target, and description
    of each shortcut. Rows are sorted by the targets.
    """

    sorted_shortcuts = sorted(shortcuts, key=lambda s: str(s.path))

    table: list[list[str]] = []
    for shortcut in sorted_shortcuts:
        aliases = format_aliases(shortcut.alias_map)
        target_fmt = str(shortcut.path).replace(str(HOME), "~")
        table.append(
            [
                shortcut.type,
                aliases,
                truncate(target_fmt, target_col_width),
                (shortcut.description or "")[:description_col_width],
            ]
        )

    return tabulate(
        tabular_data=table,
        headers=["Type", "Aliases", "Target", "Description"],
        tablefmt="simple_outline",
    )

import os

from scripts.user_shortcuts.src.models import Bookmark

# Column widths
ALIASES_WIDTH = 20
TARGET_WIDTH = 60
DESCRIPTION_WIDTH = 25


def format_aliases(aliases: dict[str, list[str]]) -> str:
    """Format aliases like 'doc, d (Yazi)' if groups differ."""
    parts = []
    for group, keys in aliases.items():
        joined = "".join(keys)
        if group != "default":
            parts.append(f"{joined} ({group})")
        else:
            parts.append(joined)
    return "; ".join(parts)


def get_default_alias(bm) -> str:
    """Return the first default alias (for sorting)."""
    return bm.aliases.get("default", [""])[0]


def truncate(text: str, width: int) -> str:
    """Truncate text to fit into `width`, appending '…' if needed."""
    return text if len(text) <= width else text[: width - 1] + "…"


def format_bookmarks(bookmarks) -> str:
    groups = {"d": "Directories", "f": "Files"}
    by_type: dict[str, list[Bookmark]] = {t: [] for t in groups}
    for bm in bookmarks:
        by_type.get(bm.type, []).append(bm)

    lines = []
    for t, heading in groups.items():
        if not by_type[t]:
            continue

        sorted_bms = sorted(by_type[t], key=get_default_alias)

        lines.append(f"{heading}:")
        lines.append(
            f"{'Aliases':{ALIASES_WIDTH}} {'Target':{TARGET_WIDTH}} Description"
        )
        lines.append("-" * (ALIASES_WIDTH + TARGET_WIDTH + DESCRIPTION_WIDTH))

        for bm in sorted_bms:
            aliases = format_aliases(bm.aliases)
            target = os.path.expandvars(os.path.join(*bm.path_parts))
            target_display = truncate(target, TARGET_WIDTH)
            lines.append(
                f"{aliases:{ALIASES_WIDTH}} {target_display:{TARGET_WIDTH}} {bm.description}"
            )

        lines.append("")

    return "\n".join(lines)

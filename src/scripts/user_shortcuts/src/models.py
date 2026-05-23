from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from common.io_utilities import write_to_file
from common.logger import log


@dataclass
class Shortcut:
    type: Literal["d", "f"]
    path: Path
    alias_map: dict[str, list[str]]
    resolved_alias: list[str] | None = None
    description: str | None = None
    activate_python_env: bool = False
    condition: bool = True
    name: str = field(init=False)

    def __post_init__(self):
        """Compute the shortcuts's display name after initialization."""
        self.name = self.description if self.description else f"{str(self.path)!r}"


class ShortcutRenderer(ABC):
    def __init__(
        self,
        name: str,
        output_path: Path,
    ):
        self.name = name
        self.output_path = output_path

    def process(self, shortcuts: list[Shortcut]) -> None:
        log.info(f"[{self.name}] Processing shortcuts...")

        processed_shortcuts: list[Shortcut] = []
        for shortcut in shortcuts:
            alias = self.resolve_alias(shortcut)

            # The alias check stays because it depends on self.name
            if not alias:
                log.warning(
                    f"- Skipped shortcut {shortcut.name!r} due to missing alias"
                )
                continue

            shortcut.resolved_alias = alias
            processed_shortcuts.append(shortcut)

            log.debug(
                f"- Added alias {''.join(alias)!r:<6} for shortcut {shortcut.name!r}"
            )

        content = self.compose_output_file(processed_shortcuts)
        write_to_file(content, self.output_path)

        log.info(f"[{self.name}] Processed {len(processed_shortcuts)} shortcuts")

    def resolve_alias(self, shortcut: Shortcut) -> list[str] | None:
        return shortcut.alias_map.get(self.name, shortcut.alias_map.get("default"))

    @abstractmethod
    def compose_shortcut(self, alias_segments: list[str], shortcut: Shortcut) -> str:
        pass

    # NOTE: we pass in resolved_alias with the shortcut itself, but we split it when we
    # compose. Maybe there's a better way to do it, but since each Renderer may resolve
    # to a different alias, we use this for now.
    def compose_shortcuts(self, shortcuts: list[Shortcut]) -> str:
        return "\n".join(
            [
                self.compose_shortcut(
                    alias_segments=shortcut.resolved_alias or [], shortcut=shortcut
                )
                for shortcut in shortcuts
            ]
        )

    def compose_output_file(self, shortcuts: list[Shortcut]) -> str:
        return self.compose_shortcuts(shortcuts)

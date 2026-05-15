import os
import shlex
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal

from common.helpers import resolve_path
from common.io_utilities import write_to_file
from common.logger import log


@dataclass
class Shortcut:
    type: Literal["d", "f"]
    path_parts: list[str]
    aliases: dict[str, list[str]]
    resolved_alias: list[str] | None = None
    description: str | None = None
    activate_python_env: bool = False
    condition: bool = True
    name: str = field(init=False)

    def __post_init__(self):
        """Compute the shortcuts's display name after initialization."""
        self.name = (
            self.description if self.description else f"[{''.join(self.path_parts)}]"
        )


class ShortcutRenderer(ABC):
    def __init__(
        self,
        name: str,
        output_path_parts: list[str],
        expand_vars: bool = True,
        escape_path: bool = True,
    ):
        self.name = name
        self.output_path = resolve_path(output_path_parts)
        self.expand_vars = expand_vars
        self.escape_path = escape_path

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
        return shortcut.aliases.get(self.name, shortcut.aliases.get("default"))

    def get_path(self, shortcut: Shortcut) -> str:
        path_str = os.path.join(*shortcut.path_parts)

        if self.expand_vars:
            # TODO: expanded vars may not be valid on Windows
            path_str = os.path.expandvars(path_str)

        if self.escape_path:
            path_str = shlex.quote(path_str)

        return path_str

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

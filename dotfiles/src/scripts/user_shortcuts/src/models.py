import os
import shlex
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal

from common.helpers import resolve_path, write_to_file
from common.logger import logger


@dataclass
class Bookmark:
    type: Literal["d", "f"]
    path_parts: list[str]
    aliases: dict[str, list[str]]
    resolved_alias: list[str] | None = None
    description: str | None = None
    activate_python_env: bool = False
    condition: bool = True
    name: str = field(init=False)

    def __post_init__(self):
        """Compute the bookmark's display name after initialization."""
        if self.description:
            self.name = self.description
        else:
            self.name = f"[{''.join(self.path_parts)}]"


class BookmarkRenderer(ABC):
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

    def process(self, bookmarks: list[Bookmark]) -> None:
        logger.info(f"[{self.name}] Processing bookmarks...")

        processed_bookmarks: list[Bookmark] = []
        for bookmark in bookmarks:
            alias = self.resolve_alias(bookmark)

            # The alias check stays because it depends on self.name
            if not alias:
                logger.warning(
                    f"- Skipped bookmark {bookmark.name!r} due to missing alias"
                )
                continue

            bookmark.resolved_alias = alias
            processed_bookmarks.append(bookmark)

            logger.debug(
                f"- Added alias {''.join(alias)!r:<6} for bookmark {bookmark.name!r}"
            )

        content = self.compose_output_file(processed_bookmarks)
        write_to_file(content, self.output_path)

        logger.info(f"[{self.name}] Processed {len(processed_bookmarks)} bookmarks")

    def resolve_alias(self, bookmark: Bookmark) -> list[str] | None:
        return bookmark.aliases.get(self.name, bookmark.aliases.get("default"))

    def get_path(self, bookmark: Bookmark) -> str:
        path_str = os.path.join(*bookmark.path_parts)

        if self.expand_vars:
            # TODO: expanded vars may not be valid on Windows
            path_str = os.path.expandvars(path_str)

        if self.escape_path:
            path_str = shlex.quote(path_str)

        return path_str

    @abstractmethod
    def compose_bookmark(self, alias_segments: list[str], bookmark: Bookmark) -> str:
        pass

    # NOTE: we pass in resolved_alias with the bookmark itself, but we split it when we
    # compose. Maybe there's a better way to do it, but since each Renderer may resolve
    # to a different alias, we use this for now.
    def compose_bookmarks(self, bookmarks: list[Bookmark]) -> str:
        return "\n".join(
            [
                self.compose_bookmark(
                    alias_segments=bookmark.resolved_alias or [], bookmark=bookmark
                )
                for bookmark in bookmarks
            ]
        )

    def compose_output_file(self, bookmarks: list[Bookmark]) -> str:
        return self.compose_bookmarks(bookmarks)

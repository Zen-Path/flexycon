import os
import shlex
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Tuple

from common.helpers import resolve_path, write_to_file
from common.logger import logger


@dataclass
class Bookmark:
    type: Literal["d", "f"]
    path_parts: List[str]
    aliases: Dict[str, List[str]]
    description: Optional[str] = None
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
        output_path_parts: List[str],
        expand_vars: bool = True,
        escape_path: bool = True,
    ):
        self.name = name
        self.output_path = resolve_path(output_path_parts)
        self.expand_vars = expand_vars
        self.escape_path = escape_path

    def process(self, bookmarks: List[Bookmark]) -> None:
        logger.info(f"[{self.name}] Processing bookmarks...")

        processed_bookmarks = []
        for bookmark in bookmarks:
            if not bookmark.condition:
                logger.warning(
                    f"- Skipped bookmark {bookmark.name!r} due to condition not being met"
                )
                continue

            alias = self.resolve_alias(bookmark)
            if not alias:
                logger.warning(
                    f"- Skipped bookmark {bookmark.name!r} due to missing alias"
                )
                continue

            if not resolve_path(bookmark.path_parts).exists():
                logger.warning(
                    f"- Bookmark {bookmark.name!r} doesn't point to a real file"
                )

            processed_bookmarks.append((alias, bookmark))

            logger.debug(
                f"- Added alias {"".join(alias)!r} for bookmark {bookmark.name!r}"
            )

        logger.info(f"[{self.name}] Processed {len(processed_bookmarks)} bookmarks")

        content = self.compose_output_file(processed_bookmarks)
        write_to_file(content, self.output_path)

    def resolve_alias(self, bookmark: Bookmark) -> Optional[List[str]]:
        return bookmark.aliases.get(self.name, bookmark.aliases.get("default"))

    def _get_path(self, bookmark: Bookmark) -> str:
        path_str = os.path.join(*bookmark.path_parts)

        if self.expand_vars:
            # TODO: expanded vars may not be valid on Windows
            path_str = os.path.expandvars(path_str)

        if self.escape_path:
            path_str = shlex.quote(path_str)

        return path_str

    @abstractmethod
    def compose_bookmark(self, alias_segments: List[str], bookmark: Bookmark) -> str:
        pass

    def compose_bookmarks(self, bookmarks: List[Tuple[List[str], Bookmark]]) -> str:
        return "\n".join(
            [
                self.compose_bookmark(alias_segments, bookmark)
                for [alias_segments, bookmark] in bookmarks
            ]
        )

    def compose_output_file(self, bookmarks) -> str:
        return self.compose_bookmarks(bookmarks)

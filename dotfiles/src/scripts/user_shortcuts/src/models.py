import logging
import os
import shlex
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple, Union

from common.helpers import resolve_path

logger = logging.getLogger(__name__)


@dataclass
class Bookmark:
    type: Literal["d", "f"]
    path_parts: List[str]
    aliases: Dict[str, Union[bool, List[str]]]
    description: Optional[str] = None

    @property
    def resolved_path(self) -> str:
        return resolve_path(self.path_parts)


class BookmarkRenderer(ABC):
    def __init__(
        self,
        name: str,
        path_parts: List[str],
        expand_vars: bool = False,
        escape_path: bool = False,
        indentation_level: int = 4,
    ):
        self.name = name
        self.path_parts = path_parts
        self.expand_vars = expand_vars
        self.escape_path = escape_path
        self.processed_bookmarks: List[Tuple[List[str], Bookmark]] = []
        self.indentation = " " * indentation_level

    def process(self, bookmarks: List[Bookmark]) -> None:
        logger.info(f"[{self.name}] Processing bookmarks...")
        count = 0

        for i, bookmark in enumerate(bookmarks):
            alias_value = bookmark.aliases.get(
                self.name, bookmark.aliases.get("default", False)
            )
            if isinstance(alias_value, list):
                alias_str = "".join(alias_value)
                self.processed_bookmarks.append((alias_value, bookmark))

                logger.debug(f"- Added alias '{alias_str}' for bookmark {i}")
                count += 1
            else:
                logger.debug(f"- Skipped bookmark {i} (no alias)")

        logger.info(f"[{self.name}] Processed {count} bookmark(s)")

        content = self.compose_file()
        self._write_output(content)

    def _get_path(self, bookmark: Bookmark) -> str:
        path_str = os.path.join(*bookmark.path_parts)

        if self.expand_vars:
            path_str = os.path.expandvars(path_str)

        if self.escape_path:
            path_str = shlex.quote(path_str)

        return path_str

    def _write_output(self, content: str) -> None:
        path = Path(resolve_path(self.path_parts))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

        logger.info(f"[{self.name}] Wrote file to {path}")

    def compose_bookmarks(self) -> str:
        lines = []
        for [alias_segments, bookmark] in self.processed_bookmarks:
            lines += [self.compose_bookmark(alias_segments, bookmark)]
        return "\n".join(lines)

    def compose_file(self) -> str:
        return self.compose_bookmarks()

    @abstractmethod
    def compose_bookmark(self, alias_segments: List[str], bookmark: Bookmark) -> str:
        pass

#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging

from common.helpers import get_version, resolve_path
from common.logger import logger, setup_logging
from scripts.user_shortcuts.data.shortcuts import shortcuts
from scripts.user_shortcuts.src.formatting import format_bookmarks
from scripts.user_shortcuts.src.models import Bookmark, BookmarkRenderer
from scripts.user_shortcuts.src.renderers import NVIM, YAZI, ZSH

AVAILABLE_RENDERERS: list[BookmarkRenderer] = [ZSH, NVIM, YAZI]


# TODO: find a better way to render the shortcuts from another script, this is flimsy
def get_active_shortcuts(shortcuts: list[Bookmark] = shortcuts) -> list[Bookmark]:
    result: list[Bookmark] = []
    for shortcut in shortcuts:
        if not shortcut.condition:
            logger.warning(
                f"- Skipped bookmark {shortcut.name!r} due to condition not being met"
            )
            continue

        if not resolve_path(shortcut.path_parts).exists():
            logger.debug(f"- Bookmark {shortcut.name!r} doesn't point to a real file")

        result.append(shortcut)
    return result


def build_parser(renderers: list[BookmarkRenderer]) -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="user_shortcuts",
        description="Generate bookmarks for various tools.",
    )

    parser.add_argument(
        "-r",
        "--renderer",
        choices=sorted(
            [renderer.name.lower() for renderer in renderers], key=str.lower
        ),
        help="generate bookmarks only for a renderer",
    )
    parser.add_argument(
        "-l",
        "--list-shortcuts",
        action="store_true",
        help="list shortcuts in a human-friendly way and exit",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    return parser


def main() -> None:
    args = build_parser(AVAILABLE_RENDERERS).parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.ERROR)
    logger.debug(args)

    if args.list_shortcuts:
        print(format_bookmarks(shortcuts))
        return

    active_renderers = AVAILABLE_RENDERERS
    if args.renderer:
        active_renderers = [
            r for r in AVAILABLE_RENDERERS if r.name.lower() == args.renderer
        ]

    active_shortcuts = get_active_shortcuts(shortcuts)
    for renderer in active_renderers:
        renderer.process(active_shortcuts)


if __name__ == "__main__":
    main()

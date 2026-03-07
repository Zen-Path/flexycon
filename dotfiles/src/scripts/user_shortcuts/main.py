#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging

from common.helpers import resolve_path
from common.logger import logger, setup_logging
from scripts.user_shortcuts.data.shortcuts import shortcuts
from scripts.user_shortcuts.src.formatting import format_bookmarks
from scripts.user_shortcuts.src.renderers import NVIM, YAZI, ZSH

AVAILABLE_RENDERERS = [ZSH, NVIM, YAZI]


def build_parser():
    parser = argparse.ArgumentParser(
        description="Generate bookmarks for various tools."
    )

    parser.add_argument(
        "-r",
        "--renderer",
        choices=sorted(
            [renderer.name.lower() for renderer in AVAILABLE_RENDERERS], key=str.lower
        ),
        help="generate bookmarks only for a renderer",
    )
    parser.add_argument(
        "-l",
        "--list-shortcuts",
        action="store_true",
        help="list shortcuts in a human-friendly way",
    )
    parser.add_argument("--verbose", action="store_true", help="enable debug output")

    return parser


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.ERROR)

    if args.list_shortcuts:
        print(format_bookmarks(shortcuts))
        return

    active_shortcuts = []
    for shortcut in shortcuts:
        if not shortcut.condition:
            logger.warning(
                f"- Skipped bookmark {shortcut.name!r} due to condition not being met"
            )
            continue

        if not resolve_path(shortcut.path_parts).exists():
            logger.debug(f"- Bookmark {shortcut.name!r} doesn't point to a real file")

        active_shortcuts.append(shortcut)

    active_renderers = AVAILABLE_RENDERERS
    if args.renderer:
        active_renderers = [
            r for r in AVAILABLE_RENDERERS if r.name.lower() == args.renderer
        ]

    for renderer in active_renderers:
        renderer.process(active_shortcuts)


if __name__ == "__main__":
    main()

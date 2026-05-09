#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging

from common.helpers import get_version, resolve_path
from common.logger import logger, setup_logging
from scripts.user_shortcuts.data.shortcuts import shortcuts
from scripts.user_shortcuts.src.formatting import format_bookmarks
from scripts.user_shortcuts.src.renderers import NVIM, YAZI, ZSH

AVAILABLE_RENDERERS = [ZSH, NVIM, YAZI]


# TODO: find a better way to render the shortcuts from another script, this is flimsy
def get_active_shortcuts(shortcuts=shortcuts):
    result = []
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="user_shortcuts", description="Generate bookmarks for various tools."
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

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    return parser


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.ERROR)

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

#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging

from common.helpers import get_version
from common.logger import log, setup_logging
from scripts.user_shortcuts.data.shortcuts import shortcuts
from scripts.user_shortcuts.src.formatting import format_shortcuts
from scripts.user_shortcuts.src.models import Shortcut, ShortcutRenderer
from scripts.user_shortcuts.src.renderers import NVIM, YAZI, ZSH

AVAILABLE_RENDERERS: list[ShortcutRenderer] = [ZSH, NVIM, YAZI]


# TODO: find a better way to render the shortcuts from another script, this is flimsy
def get_active_shortcuts(shortcuts: list[Shortcut] = shortcuts) -> list[Shortcut]:
    result: list[Shortcut] = []
    for shortcut in shortcuts:
        if not shortcut.condition:
            log.warning(
                f"- Skipped shortcut {shortcut.name!r} due to condition not being met"
            )
            continue

        if not shortcut.path.exists():
            log.debug(f"- Shortcut {shortcut.name!r} doesn't point to a real file")

        result.append(shortcut)
    return result


def build_parser(renderers: list[ShortcutRenderer]) -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="user_shortcuts",
        description="Generate shortcuts for various tools.",
    )

    parser.add_argument(
        "-r",
        "--renderer",
        choices=sorted(
            [renderer.name.lower() for renderer in renderers], key=str.lower
        ),
        help="generate shortcuts only for a renderer",
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

    setup_logging(log, logging.DEBUG if args.verbose else logging.ERROR)
    log.debug(args)

    if args.list_shortcuts:
        print(format_shortcuts(shortcuts))
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

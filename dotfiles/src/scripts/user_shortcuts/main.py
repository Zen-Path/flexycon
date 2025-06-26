import argparse
import logging

from common.logger import setup_logging
from scripts.user_shortcuts.data.shortcuts import shortcuts
from scripts.user_shortcuts.src.renderers import NVIM, YAZI, ZSH

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Generate bookmarks for various tools."
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug output.")
    args = parser.parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.ERROR)

    for renderer in (ZSH, NVIM, YAZI):
        renderer.process(shortcuts)


if __name__ == "__main__":
    main()

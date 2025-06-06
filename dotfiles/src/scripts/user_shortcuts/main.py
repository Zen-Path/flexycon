import argparse
import logging

from common.logger import setup_logging
from src.data import shortcuts
from src.renderers import NVIM, YAZI, ZSH

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Generate bookmarks for various tools."
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug output.")
    args = parser.parse_args()

    setup_logging(verbose=args.verbose)

    for renderer in (ZSH, NVIM, YAZI):
        renderer.process(shortcuts)


if __name__ == "__main__":
    main()

import argparse
import logging
import warnings
from pathlib import Path

from common.helpers import get_version
from common.logger import log, setup_logging
from common.variables import FLEXYCON_CONFIG
from scripts.dunst_config_compiler.src.core import compose_config_file

warnings.filterwarnings("error", category=UserWarning)


OUTPUT_FILE = FLEXYCON_CONFIG / "dunst" / "dunst.conf"


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="dunst_config_compiler",
        description="Compile configuration for other programs from a Python dictionary.",
    )

    parser.add_argument(
        "-o",
        "--output-file",
        type=Path,
        default=OUTPUT_FILE,
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

    setup_logging(log, logging.DEBUG if args.verbose else logging.INFO)
    log.debug(args)

    final_str = compose_config_file()

    output_file = args.output_file

    # Ensure directory exists and write
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        f.write(final_str)

    log.debug("Compilation successful.")


if __name__ == "__main__":
    main()

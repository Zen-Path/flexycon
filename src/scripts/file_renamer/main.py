#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
from pathlib import Path

from common.helpers import get_version
from common.logger import logger, setup_logging
from common.string_utilities import (
    to_camel_case,
    to_camel_snake_case,
    to_flat_case,
    to_flat_upper_case,
    to_kebab_case,
    to_kebab_upper_case,
    to_lower_case,
    to_pascal_case,
    to_snake_case,
    to_snake_upper_case,
    to_train_case,
    to_upper_case,
)
from scripts.file_renamer.src.core import ConverterRow, rename_path

CONVERTERS: list[ConverterRow] = [
    ("-l", "--lower-case", "lower case", to_lower_case),
    ("-u", "--upper-case", "UPPER CASE", to_upper_case),
    ("-s", "--snake-case", "snake_case", to_snake_case),
    ("-S", "--snake-upper-case", "SNAKE_UPPER", to_snake_upper_case),
    ("-c", "--camel-case", "camelCase", to_camel_case),
    ("-C", "--camel-snake-case", "Camel_Snake_Case", to_camel_snake_case),
    ("-p", "--pascal-case", "PascalCase", to_pascal_case),
    ("-t", "--train-case", "Train-Case", to_train_case),
    ("-k", "--kebab-case", "kebab-case", to_kebab_case),
    ("-K", "--kebab-upper-case", "KEBAB-CASE", to_kebab_upper_case),
    ("-f", "--flat-case", "flatcase (destructive)", to_flat_case),
    ("-F", "--flat-upper-case", "FLATCASE (destructive)", to_flat_upper_case),
]


def map_converters(converters: list[ConverterRow]) -> dict[str, ConverterRow]:
    result: dict[str, ConverterRow] = {}

    for converter in converters:
        short, long, _desc, _func = converter
        dest_name = long.lstrip("-").replace("-", "_") if long else short.lstrip("-")
        result[dest_name] = converter

    return result


def build_parser(converters_map: dict[str, ConverterRow]):
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="rename_file",
        description="Rename files with different case styles.\n"
        "\nNOTE: The order in which the converters are called may not be the same order\n"
        "in which they are executed.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    group = parser.add_argument_group(title="converters")
    for dest, (short, long, desc, _func) in converters_map.items():
        group.add_argument(
            short,
            long,
            dest=dest,
            nargs="+",
            type=Path,
            action="extend",
            metavar="PATH",
            help=f"convert to {desc}",
        )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    return parser


def main() -> None:
    converters_map = map_converters(CONVERTERS)

    args = build_parser(converters_map).parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.INFO)
    logger.debug(args)

    for dest, (_short, _long, _desc, transform) in converters_map.items():
        # Get list of paths for a specific converter (e.g. args.kebab_case)
        converter = getattr(args, dest)

        if not converter:
            continue

        logger.debug(f"Using converter {dest!r}.")

        for target in converter:
            if not target.exists():
                logger.warning(f"Skipping non-existent path {str(target)!r}.")
                continue

            rename_path(target, transform)


if __name__ == "__main__":
    main()

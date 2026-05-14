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
from scripts.file_renamer.src.core import ConverterRow, map_converters, rename_path

CONVERTERS: list[ConverterRow] = [
    ConverterRow(
        short="-l",
        long="--lower-case",
        description="lower case",
        transform_func=to_lower_case,
    ),
    ConverterRow(
        short="-u",
        long="--upper-case",
        description="UPPER CASE",
        transform_func=to_upper_case,
    ),
    ConverterRow(
        short="-s",
        long="--snake-case",
        description="snake_case",
        transform_func=to_snake_case,
    ),
    ConverterRow(
        short="-S",
        long="--snake-upper-case",
        description="SNAKE_UPPER",
        transform_func=to_snake_upper_case,
    ),
    ConverterRow(
        short="-c",
        long="--camel-case",
        description="camelCase",
        transform_func=to_camel_case,
    ),
    ConverterRow(
        short="-C",
        long="--camel-snake-case",
        description="Camel_Snake_Case",
        transform_func=to_camel_snake_case,
    ),
    ConverterRow(
        short="-p",
        long="--pascal-case",
        description="PascalCase",
        transform_func=to_pascal_case,
    ),
    ConverterRow(
        short="-t",
        long="--train-case",
        description="Train-Case",
        transform_func=to_train_case,
    ),
    ConverterRow(
        short="-k",
        long="--kebab-case",
        description="kebab-case",
        transform_func=to_kebab_case,
    ),
    ConverterRow(
        short="-K",
        long="--kebab-upper-case",
        description="KEBAB-CASE",
        transform_func=to_kebab_upper_case,
    ),
    ConverterRow(
        short="-f",
        long="--flat-case",
        description="flatcase",
        is_destructive=True,
        transform_func=to_flat_case,
    ),
    ConverterRow(
        short="-F",
        long="--flat-upper-case",
        description="FLATCASE",
        is_destructive=True,
        transform_func=to_flat_upper_case,
    ),
]


def build_parser(converters_map: dict[str, ConverterRow]) -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="rename_file",
        description="Rename files with different case styles.\n"
        "\nNOTE: The order in which the converters are called may not be the same order\n"
        "in which they are executed.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    group = parser.add_argument_group(title="converters")
    for dest, converter in converters_map.items():
        group.add_argument(
            converter.short,
            converter.long,
            dest=dest,
            nargs="+",
            type=Path,
            action="extend",
            metavar="PATH",
            help=f"convert to {converter.description}{' (destructive)' if converter.is_destructive else ''}",
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

    for dest, converter in converters_map.items():
        # Get list of paths for a specific converter (e.g. args.kebab_case)
        paths = getattr(args, dest)

        if not paths:
            continue

        logger.debug(f"Using converter {dest!r}.")

        for target in paths:
            if not target.exists():
                logger.warning(f"Skipping non-existent path {str(target)!r}.")
                continue

            rename_path(target, converter.transform_func)


if __name__ == "__main__":
    main()

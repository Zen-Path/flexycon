#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import os
from pathlib import Path
from typing import Callable

from common.helpers import get_version
from common.logger import logger, setup_logging
from common.string_utilities import split_into_words
from scripts.file_renamer.src.converters import (
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

type ConverterFunc = Callable[[list[str], str], str]
type ConverterRow = tuple[str, str, str, ConverterFunc]

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


def rename_path(path: Path, transform_func: ConverterFunc):
    """Attempt to rename a file or directory, catching and logging errors."""
    try:
        root, ext = os.path.splitext(path.name)
        words = split_into_words(root)

        new_name = transform_func(words, ext)
        logger.debug(f"Words={words}, ext={ext}, new_name={new_name}")

        # Skip if name didn't change
        if path.name == new_name:
            return

        new_path = path.with_name(new_name)
        path.rename(new_path)
        logger.debug(f"Renamed: {path.name} -> {new_path.name}")

    except Exception as e:
        logger.error(f"Error renaming {str(path)!r}: {e}")


def build_parser(converters_map: dict[str, ConverterRow]):
    parser = argparse.ArgumentParser(
        prog="rename_file", description="Rename files with different case styles."
    )

    group = parser.add_mutually_exclusive_group(required=True)
    for dest, (short, long, desc, _func) in converters_map.items():
        args = [arg for arg in (short, long) if arg]  # ignore None flags
        group.add_argument(
            *args, action="store_true", help=f"convert to {desc}", dest=dest
        )

    parser.add_argument(
        "targets", nargs="+", type=Path, help="files or directories to rename"
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    return parser


def main():
    converters_map = map_converters(CONVERTERS)

    args = build_parser(converters_map).parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.INFO)
    logger.debug(f"CLI Arguments: {args}")

    # Pick the first converter that is set
    transform = next(
        (
            func
            for dest, (_short, _long, _desc, func) in converters_map.items()
            if getattr(args, dest)
        ),
        None,
    )

    if transform is None:
        return

    for target in args.targets:
        if not target.exists():
            logger.warning(f"Skipping non-existent path {str(target)!r}.")
            continue

        rename_path(target, transform)


if __name__ == "__main__":
    main()

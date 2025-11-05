#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import os
from pathlib import Path

from common.helpers import split_into_words
from common.logger import logger, setup_logging
from scripts.rename_file.src.converters import (
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

CONVERTERS = [
    ["-l", "--lower-case", "lower case", to_lower_case],
    ["-u", "--upper-case", "UPPER CASE", to_upper_case],
    ["-s", "--snake-case", "snake_case", to_snake_case],
    ["-S", "--snake-upper-case", "SNAKE_UPPER", to_snake_upper_case],
    ["-c", "--camel-case", "camelCase", to_camel_case],
    ["-C", "--camel-snake-case", "Camel_Snake_Case", to_camel_snake_case],
    ["-p", "--pascal-case", "PascalCase", to_pascal_case],
    ["-t", "--train-case", "Train-Case", to_train_case],
    ["-k", "--kebab-case", "kebab-case", to_kebab_case],
    ["-K", "--kebab-upper-case", "KEBAB-CASE", to_kebab_upper_case],
    ["-f", "--flat-case", "flatcase (destructive)", to_flat_case],
    ["-F", "--flat-upper-case", "FLATCASE (destructive)", to_flat_upper_case],
]


def map_converters(converters):
    result = {}

    for converter in converters:
        if len(converter) < 4:
            continue

        short, long, desc, func = converter[:4]

        # Skip converters with no flags at all
        if not short and not long:
            continue

        # Determine a safe dest name (like argparse would) so we can refer to it
        dest_name = long.lstrip("-").replace("-", "_") if long else short.lstrip("-")

        result[dest_name] = [short, long, desc, func]

    return result


def rename_path(path: Path, transform_func):
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
        logger.error(f"Error renaming '{path}': {e}")


def build_parser(converters_map):
    parser = argparse.ArgumentParser(
        description="Rename files with different case styles."
    )

    group = parser.add_mutually_exclusive_group(required=True)
    for dest, (short, long, desc, func) in converters_map.items():
        args = [arg for arg in (short, long) if arg]  # ignore None flags
        group.add_argument(
            *args, action="store_true", help=f"Convert to {desc}", dest=dest
        )

    parser.add_argument("targets", nargs="+", help="files or directories to rename")

    parser.add_argument("--verbose", action="store_true", help="enable debug output")

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
            for dest, (_, _, _, func) in converters_map.items()
            if getattr(args, dest)
        ),
        None,
    )

    if transform is None:
        return

    for target in args.targets:
        path = Path(target)
        if not path.exists():
            logger.warning(f"Skipping non-existent path: {path}")
            continue

        rename_path(path, transform)


if __name__ == "__main__":
    main()

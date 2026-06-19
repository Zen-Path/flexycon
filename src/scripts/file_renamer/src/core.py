import argparse
import os
from pathlib import Path
from typing import Callable, NamedTuple

from common.logger import log
from common.string_utilities import split_into_words

type TransformFunc = Callable[[list[str], str], str]


class ConverterRow(NamedTuple):
    short: str
    long: str
    description: str
    transform_func: TransformFunc
    is_destructive: bool = False


def rename_path(path: Path, transform_func: TransformFunc) -> None:
    """Attempt to rename a file or directory, catching and logging errors."""
    try:
        root, ext = os.path.splitext(path.name)
        words = split_into_words(root)

        new_name = transform_func(words, ext)
        log.debug(f"Words={words}, ext={ext!r}")

        # Skip if name didn't change
        if path.name == new_name:
            return

        new_path = path.with_name(new_name)
        path.rename(new_path)
        log.info(f"Renamed {str(path.absolute())!r} -> {str(new_path)!r}")

    except Exception as e:
        log.error(f"Error renaming {str(path)!r}: {e}")


def map_converters(converters: list[ConverterRow]) -> dict[str, ConverterRow]:
    result: dict[str, ConverterRow] = {}

    for converter in converters:
        dest_name = (converter.long or converter.short).lstrip("-").replace("-", "_")
        result[dest_name] = converter

    return result


def process_renames(
    args: argparse.Namespace, converters_map: dict[str, ConverterRow]
) -> None:
    """Applies renaming transformations based on parsed arguments."""
    for dest, converter in converters_map.items():
        # Get list of paths for a specific converter (e.g. args.kebab_case)
        paths = getattr(args, dest)

        if not paths:
            continue

        log.debug(f"Using converter {dest!r}.")

        # Sort paths by depth in descending order (deepest paths first)
        sorted_paths = sorted(paths, key=lambda p: len(p.parts), reverse=True)

        for target in sorted_paths:
            if not target.exists():
                log.warning(f"Skipping non-existent path {str(target)!r}.")
                continue

            rename_path(target, converter.transform_func)

import argparse
import os
from pathlib import Path
from typing import Callable, NamedTuple

from common.logger import log

type TransformFunc = Callable[[str], str]


class ConverterRow(NamedTuple):
    short: str
    long: str
    description: str
    transform_func: TransformFunc
    is_destructive: bool = False


def compose_new_path(path: Path, transform_func: TransformFunc) -> Path:
    """
    Transform the file root using transform_func and format the extension.

    Returns the new path.
    """

    root, ext = os.path.splitext(path.name)
    new_root = transform_func(root)
    new_ext = "." + ext.replace(" ", "").strip(".").lower() if ext else ""

    return path.with_name(f"{new_root}{new_ext}")


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
            log.debug(f"Processing {str(target)!r}")

            if not target.exists():
                log.warning(f"Skipping non-existent path {str(target)!r}")
                continue

            new_path = compose_new_path(target, converter.transform_func)
            if target == new_path:
                continue

            try:
                target.rename(new_path)
                log.info(f"Renamed {str(target.absolute())!r} -> {str(new_path)!r}")
            except Exception as e:
                log.error(f"Error renaming {str(target)!r}: {e}")

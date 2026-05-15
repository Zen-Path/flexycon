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

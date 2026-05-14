import os
from pathlib import Path
from typing import Callable

from common.logger import logger
from common.string_utilities import split_into_words

type ConverterFunc = Callable[[list[str], str], str]
type ConverterRow = tuple[str, str, str, ConverterFunc]


def rename_path(path: Path, transform_func: ConverterFunc):
    """Attempt to rename a file or directory, catching and logging errors."""
    try:
        root, ext = os.path.splitext(path.name)
        words = split_into_words(root)

        new_name = transform_func(words, ext)
        logger.debug(f"Words={words}, ext={ext!r}")

        # Skip if name didn't change
        if path.name == new_name:
            return

        new_path = path.with_name(new_name)
        path.rename(new_path)
        logger.info(f"Renamed {str(path.absolute())!r} -> {str(new_path)!r}")

    except Exception as e:
        logger.error(f"Error renaming {str(path)!r}: {e}")

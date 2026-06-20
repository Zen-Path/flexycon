import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from common.string_utilities import split_into_words
from scripts.file_renamer.src.core import (
    ConverterRow,
    compose_new_path,
    process_renames,
)


@pytest.mark.parametrize(
    "path,expected",
    [
        ("one", "one"),
        ("one two three", "one_two_three"),
        ("hello world.ext", "hello_world.ext"),
        ("hello world.ExT", "hello_world.ext"),
        ("hello world.ext1", "hello_world.ext1"),
        (
            # Technical limitation of os.path.splitext
            "hello world.ext1.ext2",
            "hello_world_ext_1.ext2",
        ),
        ("hello world.  ext ", "hello_world.ext"),
        ("hello world.  multi word ext  ", "hello_world.multiwordext"),
    ],
)
def test_compose_new_path(path: str, expected: str):
    def mock_transform(text: str) -> str:
        return "_".join(split_into_words(text)).lower()

    assert str(compose_new_path(Path(path), mock_transform)) == expected


def test_process_renames_skips_missing_files(tmp_path: Path):
    """Test that missing files are safely ignored."""

    fake_path = tmp_path / "does_not_exist.txt"
    mock_converter = MagicMock()
    converters_map: dict[str, ConverterRow] = {"kebab_case": mock_converter}
    mock_args = argparse.Namespace(kebab_case=[fake_path])

    with patch(
        "scripts.file_renamer.src.core.compose_new_path"
    ) as mock_compose_new_path:
        process_renames(mock_args, converters_map)

        # Should never be called because the file doesn't exist
        mock_compose_new_path.assert_not_called()

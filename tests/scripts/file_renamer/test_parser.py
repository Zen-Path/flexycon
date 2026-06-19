import argparse
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from scripts.file_renamer.main import build_parser
from scripts.file_renamer.src.core import ConverterRow


@pytest.fixture
def mock_converters_map() -> dict[str, ConverterRow]:
    """Provides a small subset of converters to test parser generation."""
    # We use MagicMock for transform_func since the parser doesn't execute it
    return {
        "lower_case": ConverterRow(
            short="-l",
            long="--lower-case",
            description="lower case",
            transform_func=MagicMock(),
            is_destructive=False,
        ),
        "flat_case": ConverterRow(
            short="-f",
            long="--flat-case",
            description="flatcase",
            transform_func=MagicMock(),
            is_destructive=True,  # Test the destructive flag
        ),
    }


def test_build_parser_maps_arguments_to_paths(
    mock_converters_map: dict[str, ConverterRow],
) -> None:
    """Test that the parser maps CLI arguments to the correct destinations as Paths."""
    parser = build_parser(mock_converters_map)

    cli_args = [
        "-l",
        "some/file.txt",
        "--flat-case",
        "dir/file1",
        "dir/file2",
    ]

    args = parser.parse_args(cli_args)

    assert args.lower_case == [Path("some/file.txt")]
    assert args.flat_case == [Path("dir/file1"), Path("dir/file2")]


def test_build_parser_appends_destinations_with_extend(
    mock_converters_map: dict[str, ConverterRow],
) -> None:
    """Test that using the same flag multiple times extends the list."""
    parser = build_parser(mock_converters_map)

    files = [Path("file1.txt"), Path("file2.txt")]

    cli_args = ["-l", str(files[0]), "-l", str(files[1])]
    args = parser.parse_args(cli_args)

    # The action="extend" should merge these into a single list
    assert args.lower_case == files


def test_build_parser_descriptions_and_destructive_flags(
    mock_converters_map: dict[str, ConverterRow],
) -> None:
    """Test that the help strings format descriptions and destructive flags correctly."""
    parser = build_parser(mock_converters_map)

    # _actions is an internal argparse list, but standard for checking parser configs in tests
    actions: dict[str, argparse.Action] = {
        action.dest: action for action in parser._actions
    }

    # Standard description
    assert "lower_case" in actions
    assert actions["lower_case"].help == "convert to lower case"

    # Destructive description
    assert "flat_case" in actions
    assert actions["flat_case"].help == "convert to flatcase (destructive)"

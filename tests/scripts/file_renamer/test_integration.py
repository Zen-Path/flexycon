import argparse
from pathlib import Path

from common.string_utilities import (
    to_lower_case,
    to_pascal_case,
    to_upper_case,
)
from scripts.file_renamer.src.core import ConverterRow, process_renames


def test_rename_single_file_to_snake_case(tmp_path: Path) -> None:
    """Test that a single file is correctly renamed on the filesystem."""
    # Setup
    target_file = tmp_path / "MyAwesomeFile"
    target_file.touch()

    converters_map = {
        "lower_case": ConverterRow(
            short="-l",
            long="--lower-case",
            description="",
            transform_func=to_lower_case,
        )
    }
    args = argparse.Namespace(lower_case=[target_file])

    # Execute
    process_renames(args, converters_map)

    # Verify
    expected_file = tmp_path / "my awesome file"

    assert not target_file.exists(), "The original file should no longer exist."
    assert expected_file.exists(), "The renamed file should exist."
    assert expected_file.is_file()


def test_rename_nested_paths_bottom_up(tmp_path: Path) -> None:
    """Proves the bottom-up sorting works."""
    # Setup
    parent_dir = tmp_path / "pascal-Case-Dir"
    parent_dir.mkdir()

    child_file = parent_dir / "pascalCase file"
    child_file.touch()

    converters_map = {
        "pascal_case": ConverterRow(
            short="-p",
            long="--pascal-case",
            description="",
            transform_func=to_pascal_case,
        )
    }

    args = argparse.Namespace(pascal_case=[parent_dir, child_file])

    # Execute
    process_renames(args, converters_map)

    # Verify
    expected_parent = tmp_path / "PascalCaseDir"
    expected_child = expected_parent / "PascalCaseFile"

    # Old paths should be completely gone
    # Note: on case-insensitive systems, like macOS, a case-only change wouldn't register
    # as the old file not existing
    assert not child_file.exists()
    assert not parent_dir.exists()

    # New paths should exist in the correct structure
    assert expected_parent.exists()
    assert expected_parent.is_dir()
    assert expected_child.exists()
    assert expected_child.is_file()


def test_rename_multiple_converters_simultaneously(tmp_path: Path) -> None:
    """Test that the script handles multiple flags passed in the same command."""
    # Setup
    file_one = tmp_path / "pascal-case"
    file_one.touch()

    file_two = tmp_path / "snake_case"
    file_two.touch()

    converters_map = {
        "pascal_case": ConverterRow(
            short="-p",
            long="--pascal-case",
            description="",
            transform_func=to_pascal_case,
        ),
        "upper_case": ConverterRow(
            short="-u",
            long="--upper-case",
            description="",
            transform_func=to_upper_case,
        ),
    }

    args = argparse.Namespace(pascal_case=[file_one], upper_case=[file_two])

    # Execute
    process_renames(args, converters_map)

    # Verify
    assert (tmp_path / "PascalCase").exists()
    assert (tmp_path / "SNAKE CASE").exists()

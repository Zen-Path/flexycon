import argparse
from pathlib import Path

from common.string_utilities import (
    to_flat_case,
    to_kebab_case,
    to_snake_case,
)
from scripts.file_renamer.src.core import ConverterRow, process_renames


def test_rename_single_file_to_snake_case(tmp_path: Path) -> None:
    """Test that a single file is correctly renamed on the filesystem."""
    # Setup
    target_file = tmp_path / "MyAwesomeFile"
    target_file.touch()

    converters_map = {
        "snake_case": ConverterRow(
            short="-s",
            long="--snake-case",
            description="snake_case",
            transform_func=to_snake_case,
        )
    }
    args = argparse.Namespace(snake_case=[target_file])

    # Execute
    process_renames(args, converters_map)

    # Verify
    expected_file = tmp_path / "my_awesome_file"

    assert not target_file.exists(), "The original file should no longer exist."
    assert expected_file.exists(), "The renamed file should exist."
    assert expected_file.is_file()


def test_rename_nested_paths_bottom_up(tmp_path: Path) -> None:
    """Proves the bottom-up sorting works."""
    # Setup
    parent_dir = tmp_path / "camelCaseDir"
    parent_dir.mkdir()

    child_file = parent_dir / "camelCaseFile"
    child_file.touch()

    converters_map = {
        "kebab_case": ConverterRow(
            short="-k",
            long="--kebab-case",
            description="kebab-case",
            transform_func=to_kebab_case,
        )
    }

    args = argparse.Namespace(kebab_case=[parent_dir, child_file])

    # Execute
    process_renames(args, converters_map)

    # Verify
    expected_parent = tmp_path / "camel-case-dir"
    expected_child = expected_parent / "camel-case-file"

    # Old paths should be completely gone
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
    file_one = tmp_path / "PascalCase"
    file_one.touch()

    file_two = tmp_path / "snake_case"
    file_two.touch()

    converters_map = {
        "kebab_case": ConverterRow(
            short="-k",
            long="--kebab-case",
            description="kebab-case",
            transform_func=to_kebab_case,
        ),
        "flat_case": ConverterRow(
            short="-f",
            long="--flat-case",
            description="flatcase",
            transform_func=to_flat_case,
        ),
    }

    args = argparse.Namespace(kebab_case=[file_one], flat_case=[file_two])

    # Execute
    process_renames(args, converters_map)

    # Verify
    assert (tmp_path / "pascal-case").exists()
    assert (tmp_path / "snakecase").exists()

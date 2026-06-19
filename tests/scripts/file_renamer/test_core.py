import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.file_renamer.src.core import ConverterRow, process_renames


def test_process_renames_bottom_up_order(tmp_path: Path):
    """Test that deeper paths are renamed before shallower paths."""

    # Setup real files in a temporary directory
    parent_dir = tmp_path / "hello"
    parent_dir.mkdir()
    child_file = parent_dir / "file.txt"
    child_file.touch()

    # Mock a converter object
    mock_converter = MagicMock()
    mock_converter.transform_func = lambda x: x

    converters_map: dict[str, ConverterRow] = {"kebab_case": mock_converter}

    # Note: we pass the parent first, simulating user input order
    mock_args = argparse.Namespace(kebab_case=[parent_dir, child_file])

    # Patch so we don't actually move the files
    with patch("scripts.file_renamer.src.core.rename_path") as mock_rename_path:
        process_renames(mock_args, converters_map)

        assert mock_rename_path.call_count == 2

        calls = mock_rename_path.call_args_list

        # Call 1 should be the child (depth 3)
        assert calls[0][0][0] == child_file
        assert calls[0][0][1] == mock_converter.transform_func

        # Call 2 should be the parent (depth 2)
        assert calls[1][0][0] == parent_dir
        assert calls[1][0][1] == mock_converter.transform_func


def test_process_renames_skips_missing_files(tmp_path: Path):
    """Test that missing files are safely ignored."""

    fake_path = tmp_path / "does_not_exist.txt"
    mock_converter = MagicMock()
    converters_map: dict[str, ConverterRow] = {"kebab_case": mock_converter}
    mock_args = argparse.Namespace(kebab_case=[fake_path])

    with patch("scripts.file_renamer.src.core.rename_path") as mock_rename_path:
        process_renames(mock_args, converters_map)

        # Should never be called because the file doesn't exist
        mock_rename_path.assert_not_called()

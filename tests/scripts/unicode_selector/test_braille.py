import pytest

from scripts.unicode_selector.src.core import braille_bin_to_symbol

MOCK_SYMBOLS = {
    "⠀": "00000000",
    "⠂": "01000000",
    "⠈": "00001000",
    "⢕": "10100101",
    "⠛": "11001100",
    "⣿": "11111111",
}


@pytest.mark.parametrize(
    "patterns, by_row, expected",
    [
        # Column
        pytest.param(
            [""],
            False,
            {"⠀": "00000000"},
            id="col_empty_string_pads_to_zeros",
        ),
        pytest.param(
            ["01"],
            False,
            {"⠂": "01000000"},
            id="col_short_string_pads_right",
        ),
        pytest.param(
            ["10100101"],
            False,
            {"⢕": "10100101"},
            id="col_zig_zag",
        ),
        pytest.param(
            ["11001100"],
            False,
            {"⠛": "11001100"},
            id="col_top_square_mapping",
        ),
        pytest.param(
            ["11111111"],
            False,
            {"⣿": "11111111"},
            id="col_all_ones",
        ),
        # Row
        pytest.param(
            [""],
            True,
            {"⠀": "00000000"},
            id="row_empty_string_pads_to_zeros",
        ),
        pytest.param(
            ["01"],
            True,
            {"⠈": "01000000"},
            id="row_short_string_pads_right",
        ),
        pytest.param(
            ["10011001"],
            True,
            {"⢕": "10011001"},
            id="row_zig_zag",
        ),
        pytest.param(
            ["11110000"],
            True,
            {"⠛": "11110000"},
            id="row_top_square_mapping",
        ),
        pytest.param(
            ["11111111"],
            True,
            {"⣿": "11111111"},
            id="row_all_ones",
        ),
        # Invalid inputs
        pytest.param(
            ["101010101"],
            False,
            {},
            id="invalid_length_too_long",
        ),
        pytest.param(
            ["12345678"],
            False,
            {},
            id="invalid_characters_numeric",
        ),
        pytest.param(
            ["10 01"],
            False,
            {},
            id="invalid_characters_space",
        ),
        pytest.param(
            ["abcdefgh"],
            False,
            {},
            id="invalid_characters_alpha",
        ),
        pytest.param(
            ["11111110"],
            False,
            {},
            id="valid_binary_but_missing_from_dict",
        ),
        # Multiple patterns at once
        pytest.param(
            ["01", "10100101", "11111111"],
            False,
            {"⠂": "01000000", "⢕": "10100101", "⣿": "11111111"},
            id="col_multiple_valid_patterns",
        ),
        pytest.param(
            ["01", "10011001", "11111111"],
            True,
            {"⠈": "01000000", "⢕": "10011001", "⣿": "11111111"},
            id="row_multiple_valid_patterns",
        ),
        pytest.param(
            ["", "123", "01", "111111111", "10100101"],
            False,
            {"⠀": "00000000", "⠂": "01000000", "⢕": "10100101"},
            id="mixed_valid_and_invalid_filters_correctly",
        ),
        # Deduplication
        pytest.param(
            ["", "0000", "00000000", "010", "01000"],
            False,
            {"⠀": "00000000", "⠂": "01000000"},
            id="duplicate_symbols_overwrite_cleanly",
        ),
    ],
)
def test_braille_bin_to_symbol(
    patterns: list[str], by_row: bool, expected: dict[str, str]
):
    """Test standard mappings, invalid data filtering, and row/column transformations."""
    result = braille_bin_to_symbol(patterns, MOCK_SYMBOLS, by_row=by_row)
    assert result == expected

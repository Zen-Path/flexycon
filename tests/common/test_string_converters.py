import pytest

from common.string_utilities import (
    to_alternate_case,
    to_camel_case,
    to_lower_case,
    to_pascal_case,
    to_upper_case,
)


@pytest.mark.parametrize(
    "text, delimiter, upper_first, expected",
    [
        ("one", " ", True, "OnE"),
        ("one", "", False, "oNe"),
        ("Upper CASE", " ", True, "UpPeR cAsE"),
        ("one two three", " ", True, "OnE tWo ThReE"),
        ("one two three1", "-", True, "OnE-tWo-ThReE-1"),
        ("a1#合$23b", "", True, "A1#合$23b"),
        ("  one  two ", " ", True, "OnE tWo"),
        (" ", " ", True, ""),
    ],
)
def test_alternate_case(text: str, delimiter: str, upper_first: bool, expected: str):
    assert to_alternate_case(text, delimiter, upper_first) == expected


@pytest.mark.parametrize(
    "text, delimiter, expected",
    [
        ("one", "", "one"),
        ("Upper CASE", "", "upperCase"),
        ("one two three", "", "oneTwoThree"),
        ("one two three1", "-", "one-Two-Three-1"),
        ("  one  two ", "", "oneTwo"),
        (" ", "", ""),
    ],
)
def test_camel_case(text: str, delimiter: str, expected: str):
    assert to_camel_case(text, delimiter) == expected


@pytest.mark.parametrize(
    "text, delimiter, expected",
    [
        ("one", " ", "one"),
        ("Upper CASE", " ", "upper case"),
        ("one two three", " ", "one two three"),
        ("one two three1", "-", "one-two-three-1"),
        ("  one  two ", " ", "one two"),
        (" ", " ", ""),
    ],
)
def test_lower_case(text: str, delimiter: str, expected: str):
    assert to_lower_case(text, delimiter) == expected


@pytest.mark.parametrize(
    "text, delimiter, expected",
    [
        ("one", " ", "ONE"),
        ("Upper CASE", " ", "UPPER CASE"),
        ("one two three", " ", "ONE TWO THREE"),
        ("one two three1", "-", "ONE-TWO-THREE-1"),
        ("  one  two ", " ", "ONE TWO"),
        (" ", " ", ""),
    ],
)
def test_upper_case(text: str, delimiter: str, expected: str):
    assert to_upper_case(text, delimiter) == expected


@pytest.mark.parametrize(
    "text, delimiter, expected",
    [
        ("one", "", "One"),
        ("Upper CASE", "", "UpperCase"),
        ("one two three", "", "OneTwoThree"),
        ("one two three1", "-", "One-Two-Three-1"),
        ("  one  two ", "", "OneTwo"),
        (" ", "", ""),
    ],
)
def test_pascal_case(text: str, delimiter: str, expected: str):
    assert to_pascal_case(text, delimiter) == expected

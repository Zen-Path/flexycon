from argparse import ArgumentTypeError
from datetime import datetime

import pytest
from common.args import parse_abs_date


@pytest.mark.parametrize(
    "date_str, expected",
    [
        ("2025.01.01", datetime(2025, 1, 1)),
        ("2025.1.1", datetime(2025, 1, 1)),
        ("2025/01/15", datetime(2025, 1, 15)),
        ("2025-01-15", datetime(2025, 1, 15)),
        ("2025 01 15", datetime(2025, 1, 15)),
        ("2020-02-29", datetime(2020, 2, 29)),  # leap year
        ("0190-01-01", datetime(190, 1, 1)),
    ],
)
def test_date_simple(date_str, expected):
    assert parse_abs_date(date_str) == expected


@pytest.mark.parametrize(
    "date_str, expected",
    [
        ("Today is 2025-01-15!", datetime(2025, 1, 15)),
        ("The year is 2025, the month is 1 and the day is 15", datetime(2025, 1, 15)),
    ],
)
def test_ignore_alpha(date_str, expected):
    assert parse_abs_date(date_str) == expected


@pytest.mark.parametrize(
    "date_str",
    [
        "2025",
        "2025-01",
        "2025-01-15-10",
        "no numbers",
    ],
)
def test_date_invalid_group_count(date_str):
    with pytest.raises(ArgumentTypeError, match="Invalid date format"):
        parse_abs_date(date_str)


@pytest.mark.parametrize(
    "date_str",
    [
        "2-01-15",
        "20-01-15",
        "202-01-15",
        "15/01/2025",  # wrong format
    ],
)
def test_date_invalid_year_length(date_str):
    with pytest.raises(ArgumentTypeError, match="Invalid year component"):
        parse_abs_date(date_str)


@pytest.mark.parametrize(
    "date_str",
    [
        "2025-13-01",  # invalid month
        "2025-00-10",  # invalid month
        "2025-01-32",  # invalid day
        "2025-02-30",  # invalid day on a leap year
    ],
)
def test_date_invalid_components(date_str):
    with pytest.raises(ArgumentTypeError, match="Invalid date components"):
        parse_abs_date(date_str)

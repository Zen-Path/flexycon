from argparse import ArgumentTypeError, Namespace
from datetime import datetime, timedelta

import pytest
from common.args import resolve_date


@pytest.fixture
def fixed_now(monkeypatch):
    """Monkeypatch datetime.now() in the target module to return a fixed point in time."""
    fixed_now = datetime(2024, 1, 1, 12, 0, 0)

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed_now

    monkeypatch.setattr("common.args.datetime", FixedDateTime)
    return fixed_now


def test_no_date_value(fixed_now):
    args = Namespace(date_value=None, is_date_absolute=False)
    result = resolve_date(args)
    assert isinstance(result, datetime)
    assert result == fixed_now


def test_absolute(monkeypatch):
    called = {}

    def fake_parse_abs_date(value: str) -> datetime:
        called["value"] = value
        return datetime(2020, 2, 2)

    # Patch parse_abs_date to track the call
    monkeypatch.setattr("common.args.parse_abs_date", fake_parse_abs_date)

    args = Namespace(date_value="2020-02-02", is_date_absolute=True)
    result = resolve_date(args)

    assert result == datetime(2020, 2, 2)
    assert called["value"] == "2020-02-02"


def test_relative_valid(fixed_now):
    args = Namespace(
        date_value="5",
        is_date_absolute=False,
    )
    result = resolve_date(args)
    assert result == fixed_now + timedelta(days=5)


def test_relative_invalid():
    args = Namespace(
        date_value="abc",
        is_date_absolute=False,
    )
    with pytest.raises(ArgumentTypeError, match="Invalid relative offset"):
        resolve_date(args)


def test_missing_attribute():
    args = Namespace(
        # Missing `date_value`
        is_date_absolute=False,
    )
    with pytest.raises(ArgumentTypeError, match="Missing required argument"):
        resolve_date(args)

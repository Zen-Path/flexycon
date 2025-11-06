import os
from datetime import datetime
from pathlib import Path

import pytest
from scripts.journal_entry.main import get_journal_entry_path, open_journal_entry


@pytest.fixture
def sample_date():
    """A fixed datetime object for predictable paths."""
    return datetime(2024, 2, 15)


@pytest.fixture
def mock_env(monkeypatch, tmp_path) -> Path:
    """Provide fake JOURNAL_HOME and EDITOR environment variables."""
    home = tmp_path / "journal_home"
    home.mkdir()
    monkeypatch.setenv("JOURNAL_HOME", str(home))
    monkeypatch.setenv("EDITOR", "nano")
    return home


def test_get_journal_entry_path_with_env(sample_date, mock_env):
    path = get_journal_entry_path(sample_date)
    expected = Path(os.getenv("JOURNAL_HOME", "")) / "2024" / "02" / "02.15.md"
    assert path == expected


def test_get_journal_entry_path_missing_env(monkeypatch, sample_date):
    monkeypatch.delenv("JOURNAL_HOME", raising=False)

    with pytest.raises(
        EnvironmentError, match="JOURNAL_HOME environment variable is not set"
    ):
        _ = get_journal_entry_path(sample_date)


def test_open_journal_entry_success(monkeypatch, mock_env, sample_date):
    """Should create directories and open editor with correct file path."""
    called = {}

    # Mock ensure_directory_interactive
    def fake_ensure_directory_interactive(path):
        called.setdefault("dirs", []).append(path)

    monkeypatch.setattr(
        "scripts.journal_entry.main.ensure_directory_interactive",
        fake_ensure_directory_interactive,
    )

    # Mock subprocess.run so it doesn't actually open anything
    def fake_run(cmd, *a, **kw):
        called["cmd"] = cmd

    monkeypatch.setattr("scripts.journal_entry.main.subprocess.run", fake_run)

    # Mock logger to suppress output
    monkeypatch.setattr(
        "scripts.journal_entry.main.logger",
        type(
            "L", (), {"info": lambda *a, **kw: None, "debug": lambda *a, **kw: None}
        )(),
    )

    open_journal_entry(sample_date)

    # Validate directory creation
    year_dir = mock_env / "2024"
    month_dir = year_dir / "02"
    assert called["dirs"] == [str(year_dir), str(month_dir)]

    # Validate subprocess call
    expected_file = month_dir / "02.15.md"
    assert called["cmd"] == ["nano", str(expected_file)]


def test_open_journal_entry_without_env(monkeypatch, sample_date):
    monkeypatch.delenv("JOURNAL_HOME", raising=False)

    with pytest.raises(
        EnvironmentError, match="JOURNAL_HOME environment variable is not set"
    ):
        open_journal_entry(sample_date)

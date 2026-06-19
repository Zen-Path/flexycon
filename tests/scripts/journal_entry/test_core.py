import os
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from scripts.journal_entry.src.core import get_journal_entry_path, open_journal_entry


@pytest.fixture
def sample_date() -> datetime:
    """A fixed datetime object for predictable paths."""
    return datetime(2024, 2, 15)


@pytest.fixture
def mock_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """Provide fake JOURNAL_HOME and EDITOR environment variables."""
    home = tmp_path / "journal_home"
    home.mkdir()
    monkeypatch.setenv("JOURNAL_HOME", str(home))
    monkeypatch.setenv("EDITOR", "nano")
    return home


def test_get_journal_entry_path_with_env(sample_date: datetime):
    path = get_journal_entry_path(sample_date)
    expected = Path(os.getenv("JOURNAL_HOME", "")) / "2024" / "02" / "02.15.md"
    assert path == expected


def test_get_journal_entry_path_missing_env(
    monkeypatch: pytest.MonkeyPatch, sample_date: datetime
):
    monkeypatch.delenv("JOURNAL_HOME", raising=False)

    with pytest.raises(
        EnvironmentError, match="Environment variable 'JOURNAL_HOME' is not set"
    ):
        _ = get_journal_entry_path(sample_date)


def test_open_journal_entry_success(
    monkeypatch: pytest.MonkeyPatch, mock_env: Path, sample_date: datetime
):
    """Should ensure the month directory exists (handling parents) and open editor."""
    ensured_path: Path | None = None

    # Mock ensure_directory_interactive
    def fake_ensure_directory_interactive(path: Path):
        nonlocal ensured_path
        ensured_path = path
        return True

    monkeypatch.setattr(
        "scripts.journal_entry.src.core.ensure_directory_interactive",
        fake_ensure_directory_interactive,
    )

    # Mock subprocess.run
    called_cmd: list[str] = []

    def fake_run(cmd: list[str], *a: Any, **kw: Any):
        nonlocal called_cmd
        called_cmd = cmd

    monkeypatch.setattr("scripts.journal_entry.src.core.subprocess.run", fake_run)

    open_journal_entry(sample_date)

    # Validate
    expected_month_dir = mock_env / "2024" / "02"
    expected_file = expected_month_dir / "02.15.md"

    assert ensured_path == expected_month_dir

    # Ensure subprocess received the correct editor and path
    assert "nano" in called_cmd
    assert any(str(expected_file) in str(arg) for arg in called_cmd)


def test_open_journal_entry_without_env(
    monkeypatch: pytest.MonkeyPatch, sample_date: datetime
):
    monkeypatch.delenv("JOURNAL_HOME", raising=False)

    with pytest.raises(
        EnvironmentError, match="Environment variable 'JOURNAL_HOME' is not set"
    ):
        open_journal_entry(sample_date)

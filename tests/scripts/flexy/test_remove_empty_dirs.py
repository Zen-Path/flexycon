import logging
from pathlib import Path

import pytest
from scripts.flexy.src.targets import remove_empty_dirs

# --- STANDARD TESTS ---


def test_remove_standard_empty_dir(tmp_path: Path):
    """An empty directory with no restrictions should be removed."""
    d = tmp_path / "empty_dir"
    d.mkdir()

    remove_empty_dirs(base_dir=tmp_path)
    assert not d.exists()


def test_keep_non_empty_dir(tmp_path: Path):
    """A directory containing a file should be kept."""
    d = tmp_path / "data_dir"
    d.mkdir()
    (d / "file.txt").write_text("hello")

    remove_empty_dirs(base_dir=tmp_path)
    assert d.exists()


def test_recursive_empty_pruning(tmp_path: Path):
    """Nested empty directories should all be removed bottom-up."""
    d = tmp_path / "one" / "two" / "three"
    d.mkdir(parents=True)

    remove_empty_dirs(base_dir=tmp_path)
    assert not (tmp_path / "one").exists()


def test_hidden_file_prevents_removal(tmp_path: Path):
    """Hidden files make a directory non-empty."""
    d = tmp_path / "hidden_dir"
    d.mkdir()
    (d / ".hidden").write_text("")

    remove_empty_dirs(base_dir=tmp_path)
    assert d.exists()


def test_remove_hidden_directory(tmp_path: Path):
    """Scenario: With no arguments, even dir like .git are wiped if empty."""
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    dotfiles_dir = tmp_path / "dotfiles"
    dotfiles_dir.mkdir()

    remove_empty_dirs(base_dir=tmp_path)

    assert not git_dir.exists()
    assert not dotfiles_dir.exists()


# --- EXPLICIT EXCLUSION TESTS ---


def test_global_exclude_name(tmp_path: Path):
    """Explicitly passing .git should protect it."""
    d = tmp_path / ".git"
    d.mkdir()

    remove_empty_dirs(base_dir=tmp_path, global_excludes={".git"})
    assert d.exists()


def test_global_exclude_protects_nested_empty(tmp_path: Path):
    """If .git is explicitly excluded, .git/empty_sub folder should survive."""
    git_dir = tmp_path / "project" / ".git"
    empty_sub = git_dir / "objects"
    empty_sub.mkdir(parents=True)

    remove_empty_dirs(base_dir=tmp_path, global_excludes={".git"})
    assert empty_sub.exists()
    assert git_dir.exists()


# --- PROTECTED ROOTS TESTS ---


def test_protected_root_exact_match(tmp_path: Path):
    """A specifically protected root directory is kept."""
    dotfiles = tmp_path / "dotfiles"
    dotfiles.mkdir()

    remove_empty_dirs(base_dir=tmp_path, protected_roots={dotfiles})
    assert dotfiles.exists()


def test_protected_root_nested_match_is_deleted(tmp_path: Path):
    """A directory named 'dotfiles' deep in the tree is NOT protected
    if only the root-level 'dotfiles' is in the protected list."""

    # Protect the root one
    root_dotfiles = tmp_path / "dotfiles"

    # Create a nested one
    nested_dotfiles = tmp_path / "projects" / "dotfiles"
    nested_dotfiles.mkdir(parents=True)

    remove_empty_dirs(base_dir=tmp_path, protected_roots={root_dotfiles})

    assert not nested_dotfiles.exists()
    assert not (tmp_path / "projects").exists()


# --- SAFETY & EDGE CASE TESTS ---


def test_permission_error_handling(tmp_path: Path, caplog: pytest.LogCaptureFixture):
    """A locked directory logs an error but does not crash the script."""
    d = tmp_path / "locked_dir"
    d.mkdir()

    # Remove all permissions (read, write, execute)
    d.chmod(0o000)

    try:
        with caplog.at_level(logging.WARNING):
            remove_empty_dirs(base_dir=tmp_path)

        assert d.exists()
        assert "Could not remove" in caplog.text
    finally:
        # Restore permissions so pytest can clean up the temp directory!
        d.chmod(0o755)


def test_symlink_treated_as_file(tmp_path: Path):
    """A directory containing a broken symlink is NOT empty."""
    d = tmp_path / "symlink_dir"
    d.mkdir()
    link = d / "broken_link"
    link.symlink_to(tmp_path / "does_not_exist")

    remove_empty_dirs(base_dir=tmp_path)
    assert d.exists()

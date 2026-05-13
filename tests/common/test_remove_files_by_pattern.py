from pathlib import Path

from common.io_utilities import remove_files_by_pattern


def test_remove_single_file(tmp_path: Path):
    """Should delete a specific file by name."""
    f = tmp_path / "target.txt"
    f.write_text("content")

    remove_files_by_pattern({"target.txt"}, base_dir=tmp_path)
    assert not f.exists()


def test_remove_glob_files(tmp_path: Path):
    """Should delete multiple files matching a glob."""
    f1 = tmp_path / "test1.tmp"
    f2 = tmp_path / "test2.tmp"
    f3 = tmp_path / "keep.txt"
    for f in [f1, f2, f3]:
        f.write_text("")

    remove_files_by_pattern({"*.tmp"}, base_dir=tmp_path)
    assert not f1.exists()
    assert not f2.exists()
    assert f3.exists()


def test_remove_directory_recursively(tmp_path: Path):
    """Should delete a directory and all its nested contents."""
    d = tmp_path / "trash_dir"
    sub = d / "nested"
    sub.mkdir(parents=True)
    (sub / "file.txt").write_text("content")

    remove_files_by_pattern({"trash_dir"}, base_dir=tmp_path)
    assert not d.exists()


def test_remove_symlink_only(tmp_path: Path):
    """Deleting a symlink should NOT delete the original target."""
    target_dir = tmp_path / "real_dir"
    target_dir.mkdir()
    target_file = target_dir / "data.txt"
    target_file.write_text("save me")

    link = tmp_path / "link_to_dir"
    link.symlink_to(target_dir, target_is_directory=True)

    # Delete the link
    remove_files_by_pattern({"link_to_dir"}, base_dir=tmp_path)

    assert not link.exists()  # Link is gone
    assert target_dir.exists()  # Original dir stays
    assert target_file.exists()  # Content stays


def test_overlapping_patterns(tmp_path: Path):
    """
    Scenario: Pattern matches a dir AND a file inside it.
    The parent rmtree happens first; child should be handled gracefully.
    """
    d = tmp_path / "build"
    d.mkdir()
    f = d / "main.o"
    f.write_text("")

    # If 'build' is removed first, 'main.o' will be missing when the loop hits it.
    remove_files_by_pattern({"build", "*.o"}, base_dir=tmp_path)
    assert not d.exists()


def test_nested_glob_matching(tmp_path: Path):
    """Should find and delete files deep in subdirectories."""
    d = tmp_path / "a" / "b" / "c"
    d.mkdir(parents=True)
    f = d / "garbage.log"
    f.write_text("")

    remove_files_by_pattern({"*.log"}, base_dir=tmp_path)
    assert not f.exists()
    assert d.exists()  # The directories should stay if they didn't match


def test_non_existent_pattern(tmp_path: Path):
    """Should not crash or log warnings if nothing matches."""
    remove_files_by_pattern({"*.missing"}, base_dir=tmp_path)
    # Success is simply not raising an exception


def test_pattern_match_inside_global_exclude_is_ignored(tmp_path: Path):
    """Files inside a globally excluded name (like .git) should be ignored."""
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    trash = git_dir / "debug.log"
    trash.write_text("")

    remove_files_by_pattern(
        patterns={"*.log"}, base_dir=tmp_path, global_excludes={".git"}
    )
    assert trash.exists()

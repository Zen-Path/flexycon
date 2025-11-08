import platform

import pytest
from scripts.user_shortcuts.src.renderers import ZshBookmarkRenderer


class DummyBookmark:
    def __init__(
        self, path_parts, type="d", description=None, activate_python_env=False
    ):
        self.path_parts = path_parts
        self.type = type
        self.description = description
        self.activate_python_env = activate_python_env


@pytest.mark.parametrize(
    "bookmark, alias_segments, platform_name, expected",
    [
        # Directory with description
        (
            DummyBookmark(
                ["/", "Users", "user", "Downloads"], type="d", description="downloads"
            ),
            ["dwn"],
            "Darwin",
            "# downloads\n"
            'alias dwn="cd /Users/user/Downloads && ls"\n'
            "hash -d dwn=/Users/user/Downloads\n",
        ),
        # Directory without description
        (
            DummyBookmark(["/", "Users", "user", "Documents"], type="d"),
            ["docs"],
            "Linux",
            'alias docs="cd /Users/user/Documents && ls"\n'
            "hash -d docs=/Users/user/Documents\n",
        ),
        # File with description
        (
            DummyBookmark(["/", "tmp", "file.txt"], type="f", description="a file"),
            ["f1"],
            "Linux",
            "# a file\n" 'alias f1="xdg-open /tmp/file.txt"\n',
        ),
        # File without description
        (
            DummyBookmark(["/", "etc", "hosts"], type="f"),
            ["hosts"],
            "Linux",
            'alias hosts="xdg-open /etc/hosts"\n',
        ),
        # Windows platform
        (
            DummyBookmark(["/", "etc", "hosts"], type="f"),
            ["hosts"],
            "Windows",
            'alias hosts="$EDITOR /etc/hosts"\n',
        ),
        # Path that requires quoting (contains spaces)
        (
            DummyBookmark(
                ["/", "Users", "user", "My Folder"], type="d", description="spaced dir"
            ),
            ["mf"],
            "Linux",
            "# spaced dir\n"
            "alias mf=\"cd '/Users/user/My Folder' && ls\"\n"
            "hash -d mf='/Users/user/My Folder'\n",
        ),
    ],
)
def test_compose_bookmark(
    monkeypatch, bookmark, alias_segments, platform_name, expected
):
    renderer = ZshBookmarkRenderer(
        "Zsh", ["$XDG_CONFIG_HOME", "shell", "shortcuts.sh"], escape_path=True
    )
    # Make platform.system predictable
    monkeypatch.setattr(platform, "system", lambda: platform_name)
    result = renderer.compose_bookmark(alias_segments, bookmark)
    assert platform.system() == platform_name
    assert result == expected

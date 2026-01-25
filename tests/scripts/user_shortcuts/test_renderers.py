# ruff: noqa: E501

import platform

import pytest
from scripts.user_shortcuts.src.models import Bookmark
from scripts.user_shortcuts.src.renderers import NVIM, YAZI, ZSH, ZshBookmarkRenderer


@pytest.fixture
def mock_env(monkeypatch):
    """Provide fake environment variables."""
    monkeypatch.setenv("HOME", "/Users/mock")
    monkeypatch.setenv("COUNTRY", "United States of America")


@pytest.mark.parametrize(
    "renderer, aliases, expected",
    [
        (ZSH, {"default": ["h"]}, ["h"]),
        (ZSH, {"default": ["d", "o", "c"]}, ["d", "o", "c"]),
        # uppercase
        (ZSH, {"default": ["D", "o", "c"]}, ["D", "o", "c"]),
        # multi-char alias parts
        (ZSH, {"default": ["Ctrl-D", "o", "c"]}, ["Ctrl-D", "o", "c"]),
        # one specific renderer
        (ZSH, {"default": ["d", "o", "c"], ZSH.name: ["a", "b", "c"]}, ["a", "b", "c"]),
        (
            YAZI,
            {"default": ["d", "o", "c"], ZSH.name: ["a", "b", "c"]},
            ["d", "o", "c"],
        ),
        #  multiple specific renderers
        (
            ZSH,
            {
                "default": ["d", "o", "c"],
                ZSH.name: ["a", "b", "c"],
                YAZI.name: ["y", "a", "z", "i"],
            },
            ["a", "b", "c"],
        ),
        # no default + one specific renderer
        (ZSH, {ZSH.name: ["a", "b", "c"]}, ["a", "b", "c"]),
        (YAZI, {ZSH.name: ["a", "b", "c"]}, None),
    ],
)
def test_resolve_alias(renderer, aliases, expected):
    bm = Bookmark(
        type="d",
        path_parts=[""],
        aliases=aliases,
    )
    assert renderer.resolve_alias(bm) == expected


@pytest.mark.parametrize(
    "path_parts, expand_vars, escape_path, expected",
    [
        (["$HOME", "Documents"], True, True, "/Users/mock/Documents"),
        (["$HOME", "Documents"], True, False, "/Users/mock/Documents"),
        (["$HOME", "Documents"], False, True, "'$HOME/Documents'"),
        (["$HOME", "Documents"], False, False, "$HOME/Documents"),
        # spaces need escaping
        (["$HOME", "Student marks"], True, True, "'/Users/mock/Student marks'"),
        # funky escaping, but actually 3 separate shell strings that get concatenated
        (["$HOME", "Student's"], True, True, "'/Users/mock/Student'\"'\"'s'"),
        # variable that when expanded contains a space
        (
            ["$HOME", "$COUNTRY", "Students"],
            True,
            True,
            "'/Users/mock/United States of America/Students'",
        ),
        # a path part is just a space
        (["$HOME", " "], True, True, "'/Users/mock/ '"),
        # a path part is empty
        (["$HOME", "", "Students"], True, True, "/Users/mock/Students"),
    ],
)
def test_get_path(path_parts, expand_vars, escape_path, expected, mock_env):
    bm = Bookmark(
        type="d",
        path_parts=path_parts,
        aliases={"default": [""]},
    )

    renderer = ZshBookmarkRenderer(
        "", [""], expand_vars=expand_vars, escape_path=escape_path
    )

    assert renderer._get_path(bm) == expected


@pytest.mark.parametrize(
    "type, path_parts, alias, description, zsh_expected, nvim_expected, yazi_expected",
    [
        # single-char alias
        (
            "d",
            ["$HOME"],
            ["h"],
            "user home",
            # zsh
            '# user home\nalias h="cd /Users/mock && ls"\nhash -d h=/Users/mock\n',
            # nvim
            "-- user home\n"
            "vim.api.nvim_set_keymap(\n"
            '    "c",\n'
            '    ";h",\n'
            '    "/Users/mock",\n'
            "    { noremap = true }\n"
            ")\n",
            # yazi
            "    { on = ['b', 'h'], run = \"cd /Users/mock\", desc = \"Open user home dir\" },",
        ),
        # multi-char alias
        (
            "d",
            ["$HOME", "Documents"],
            ["d", "o", "c"],
            "Documents",
            # zsh
            "# Documents\n"
            'alias doc="cd /Users/mock/Documents && ls"\n'
            "hash -d doc=/Users/mock/Documents\n",
            # nvim
            "-- Documents\n"
            "vim.api.nvim_set_keymap(\n"
            '    "c",\n'
            '    ";doc",\n'
            '    "/Users/mock/Documents",\n'
            "    { noremap = true }\n"
            ")\n",
            # yazi
            "    { on = ['b', 'd', 'o', 'c'], run = \"cd /Users/mock/Documents\", desc = \"Open Documents dir\" },",
        ),
        # no description
        (
            "d",
            ["$HOME", "Documents"],
            ["d", "o", "c"],
            None,
            # zsh
            'alias doc="cd /Users/mock/Documents && ls"\n'
            "hash -d doc=/Users/mock/Documents\n",
            # nvim
            "vim.api.nvim_set_keymap(\n"
            '    "c",\n'
            '    ";doc",\n'
            '    "/Users/mock/Documents",\n'
            "    { noremap = true }\n"
            ")\n",
            # yazi
            "    { on = ['b', 'd', 'o', 'c'], run = \"cd /Users/mock/Documents\", desc = \"\" },",
        ),
        # requires shell quoting
        (
            "d",
            ["$HOME", "Student marks"],
            ["s", "t", "u", "m"],
            None,
            # zsh
            "alias stum=\"cd '/Users/mock/Student marks' && ls\"\n"
            "hash -d stum='/Users/mock/Student marks'\n",
            # nvim
            "vim.api.nvim_set_keymap(\n"
            '    "c",\n'
            '    ";stum",\n'
            '    "/Users/mock/Student marks",\n'
            "    { noremap = true }\n"
            ")\n",
            # yazi
            "    { on = ['b', 's', 't', 'u', 'm'], run = \"cd '/Users/mock/Student marks'\", desc = \"\" },",
        ),
        # file
        (
            "f",
            ["$HOME", "University", "Timetable.pdf"],
            ["u", "n", "i", "t"],
            "university timetable",
            # zsh
            "# university timetable\n"
            'alias unit="open /Users/mock/University/Timetable.pdf"\n',
            # nvim
            "-- university timetable\n"
            "vim.api.nvim_set_keymap(\n"
            '    "c",\n'
            '    ";unit",\n'
            '    "/Users/mock/University/Timetable.pdf",\n'
            "    { noremap = true }\n"
            ")\n",
            # yazi
            "    { on = ['b', 'u', 'n', 'i', 't'], run = [\"reveal /Users/mock/University/Timetable.pdf\", \"open\"], desc = \"Reveal university timetable file\" },",
        ),
    ],
)
def test_compose_bookmark(
    type,
    path_parts,
    alias,
    description,
    zsh_expected,
    nvim_expected,
    yazi_expected,
    monkeypatch,
    mock_env,
):
    monkeypatch.setattr(platform, "system", lambda: "Darwin")

    bm = Bookmark(
        type=type,
        path_parts=path_parts,
        aliases={"default": [""]},
        description=description,
    )

    assert ZSH.compose_bookmark(alias, bm) == zsh_expected
    assert NVIM.compose_bookmark(alias, bm) == nvim_expected
    assert YAZI.compose_bookmark(alias, bm) == yazi_expected


@pytest.mark.parametrize(
    "platform_name, expected",
    [
        ("Darwin", 'alias unit="open /Users/mock/University/Timetable.pdf"\n'),
        ("Linux", 'alias unit="xdg-open /Users/mock/University/Timetable.pdf"\n'),
        ("Windows", 'alias unit="$EDITOR /Users/mock/University/Timetable.pdf"\n'),
        ("Unknown", 'alias unit="$EDITOR /Users/mock/University/Timetable.pdf"\n'),
    ],
)
def test_compose_platforms(platform_name, expected, monkeypatch, mock_env):
    monkeypatch.setattr(platform, "system", lambda: platform_name)
    bm = Bookmark(
        type="f",
        aliases={"default": [""]},
        path_parts=["$HOME", "University", "Timetable.pdf"],
    )
    assert ZSH.compose_bookmark(["u", "n", "i", "t"], bm) == expected


@pytest.mark.parametrize(
    "renderer, expected",
    [
        (
            ZSH,
            "# documents\n"
            'alias doc="cd /Users/mock/Documents && ls && penva"\n'
            "hash -d doc=/Users/mock/Documents\n",
        ),
    ],
)
def test_compose_activate_penv(renderer, expected, mock_env):
    bm = Bookmark(
        type="d",
        path_parts=["$HOME", "Documents"],
        aliases={"default": [""]},
        activate_python_env=True,
        description="documents",
    )
    assert renderer.compose_bookmark(["d", "o", "c"], bm) == expected

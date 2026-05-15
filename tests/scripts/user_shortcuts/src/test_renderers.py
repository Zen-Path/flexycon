# ruff: noqa: E501

import sys
from typing import Literal

import pytest

from scripts.user_shortcuts.src.models import Shortcut
from scripts.user_shortcuts.src.renderers import (
    NVIM,
    YAZI,
    ZSH,
    ShortcutRenderer,
    ZshShortcutRenderer,
)


@pytest.fixture
def mock_env(monkeypatch: pytest.MonkeyPatch):
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
def test_resolve_alias(
    renderer: ShortcutRenderer,
    aliases: dict[str, list[str]],
    expected: list[str] | None,
):
    shortcut = Shortcut(
        type="d",
        path_parts=[""],
        aliases=aliases,
    )
    assert renderer.resolve_alias(shortcut) == expected


@pytest.mark.usefixtures("mock_env")
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
def test_get_path(
    path_parts: list[str], expand_vars: bool, escape_path: bool, expected: str
):
    shortcut = Shortcut(
        type="d",
        path_parts=path_parts,
        aliases={"default": [""]},
    )

    renderer = ZshShortcutRenderer(
        "", [""], expand_vars=expand_vars, escape_path=escape_path
    )

    assert renderer.get_path(shortcut) == expected


@pytest.mark.usefixtures("mock_env")
@pytest.mark.parametrize(
    "type, path_parts, alias, description, zsh_expected, nvim_expected, yazi_expected",
    [
        pytest.param(
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
            id="single_char_alias",
        ),
        pytest.param(
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
            id="multi_char_alias",
        ),
        pytest.param(
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
            id="no_description",
        ),
        pytest.param(
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
            id="requires_shell_quoting",
        ),
        pytest.param(
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
            id="file",
        ),
    ],
)
def test_compose_shortcut(
    type: Literal["d"] | Literal["f"],
    path_parts: list[str],
    alias: list[str],
    description: str | None,
    zsh_expected: str,
    nvim_expected: str,
    yazi_expected: str,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(sys, "platform", "darwin")

    shortcut = Shortcut(
        type=type,
        path_parts=path_parts,
        aliases={"default": [""]},
        description=description,
    )

    assert ZSH.compose_shortcut(alias, shortcut) == zsh_expected
    assert NVIM.compose_shortcut(alias, shortcut) == nvim_expected
    assert YAZI.compose_shortcut(alias, shortcut) == yazi_expected


@pytest.mark.usefixtures("mock_env")
@pytest.mark.parametrize(
    "platform_name, expected",
    [
        ("darwin", 'alias unit="open /Users/mock/University/Timetable.pdf"\n'),
        ("linux", 'alias unit="xdg-open /Users/mock/University/Timetable.pdf"\n'),
        ("win32", 'alias unit="$EDITOR /Users/mock/University/Timetable.pdf"\n'),
        ("unknown", 'alias unit="$EDITOR /Users/mock/University/Timetable.pdf"\n'),
    ],
)
def test_compose_platforms(
    platform_name: Literal["darwin", "linux", "win32", "unknown"],
    expected: str,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(sys, "platform", platform_name)
    shortcut = Shortcut(
        type="f",
        aliases={"default": [""]},
        path_parts=["$HOME", "University", "Timetable.pdf"],
    )
    assert ZSH.compose_shortcut(["u", "n", "i", "t"], shortcut) == expected


@pytest.mark.usefixtures("mock_env")
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
def test_compose_activate_penv(renderer: ShortcutRenderer, expected: str):
    shortcut = Shortcut(
        type="d",
        path_parts=["$HOME", "Documents"],
        aliases={"default": [""]},
        activate_python_env=True,
        description="documents",
    )
    assert renderer.compose_shortcut(["d", "o", "c"], shortcut) == expected

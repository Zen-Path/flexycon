# ruff: noqa: E501

import sys
from pathlib import Path
from typing import Literal

import pytest

from scripts.user_shortcuts.src.models import Shortcut
from scripts.user_shortcuts.src.renderers import (
    NVIM,
    YAZI,
    ZSH,
    ShortcutRenderer,
)

HOME = Path("/") / "Users" / "mock"
COUNTRY = "United States of America"


@pytest.mark.parametrize(
    "renderer, alias_map, expected",
    [
        pytest.param(
            ZSH,
            {"default": ["h"]},
            ["h"],
            id="single_char",
        ),
        pytest.param(
            ZSH,
            {"default": ["d", "o", "c"]},
            ["d", "o", "c"],
            id="multi_char",
        ),
        pytest.param(
            ZSH,
            {"default": ["D", "o", "c"]},
            ["D", "o", "c"],
            id="mixed_case",
        ),
        pytest.param(
            ZSH,
            {"default": ["Ctrl-D", "o", "c"]},
            ["Ctrl-D", "o", "c"],
            id="multi_char_parts",
        ),
        pytest.param(
            ZSH,
            {"default": ["d", "o", "c"], ZSH.name: ["a", "b", "c"]},
            ["a", "b", "c"],
            id="target_renderer",
        ),
        pytest.param(
            YAZI,
            {"default": ["d", "o", "c"], ZSH.name: ["a", "b", "c"]},
            ["d", "o", "c"],
            id="not_target_renderer",
        ),
        pytest.param(
            ZSH,
            {
                "default": ["d", "o", "c"],
                ZSH.name: ["a", "b", "c"],
                YAZI.name: ["y", "a", "z", "i"],
            },
            ["a", "b", "c"],
            id="multiple_target_renderers",
        ),
        pytest.param(
            ZSH,
            {ZSH.name: ["a", "b", "c"]},
            ["a", "b", "c"],
            id="no_default_target_renderer",
        ),
        pytest.param(
            YAZI,
            {ZSH.name: ["a", "b", "c"]},
            None,
            id="no_default_not_target_renderer",
        ),
    ],
)
def test_resolve_alias(
    renderer: ShortcutRenderer,
    alias_map: dict[str, list[str]],
    expected: list[str] | None,
) -> None:
    shortcut = Shortcut(
        type="d",
        path=Path.home(),  # path isn't important
        alias_map=alias_map,
    )
    assert renderer.resolve_alias(shortcut) == expected


@pytest.mark.parametrize(
    "renderer, expected_dir, expected_file",
    [
        pytest.param(
            ZSH,
            """# user documents
function doc() {
    cd /Users/mock/Documents && ls
}
hash -d doc=/Users/mock/Documents
""",
            """# user documents
function doc() {
    cd /Users/mock && ls && open /Users/mock/Documents
}
""",
            id="zsh",
        ),
        pytest.param(
            NVIM,
            """-- user documents
vim.api.nvim_set_keymap(
    "c",
    ";doc",
    "/Users/mock/Documents",
    { noremap = true }
)
""",
            """-- user documents
vim.api.nvim_set_keymap(
    "c",
    ";doc",
    "/Users/mock/Documents",
    { noremap = true }
)
""",
            id="nvim",
        ),
        pytest.param(
            YAZI,
            "    { on = ['b', 'd', 'o', 'c'], "
            'run = "cd \\"/Users/mock/Documents\\"", '
            'desc = "Open user documents dir" },',
            "    { on = ['b', 'd', 'o', 'c'], "
            'run = ["reveal \\"/Users/mock/Documents\\"", "open"], '
            'desc = "Reveal user documents file" },',
            id="yazi",
        ),
    ],
)
def test_renderer_basic(
    renderer: ShortcutRenderer,
    expected_dir: str,
    expected_file: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "platform", "darwin")

    cases: list[tuple[Literal["d", "f"], str]] = [
        ("d", expected_dir),
        ("f", expected_file),
    ]
    for shortcut_type, expected in cases:
        shortcut = Shortcut(
            type=shortcut_type,
            path=HOME / "Documents",
            alias_map={"default": [""]},
            description="user documents",
        )
        assert renderer.compose_shortcut(["d", "o", "c"], shortcut) == expected


@pytest.mark.parametrize(
    "renderer, expected_dir, expected_file",
    [
        pytest.param(
            ZSH,
            """\
function d() {
    cd /Users/mock/Documents && ls
}
hash -d d=""",
            "function d() {",
            id="zsh",
        ),
        pytest.param(NVIM, ";d", ";d", id="nvim"),
        pytest.param(YAZI, "on = ['b', 'd'], ", "on = ['b', 'd'], ", id="yazi"),
    ],
)
def test_renderer_single_char_alias(
    renderer: ShortcutRenderer, expected_dir: str, expected_file: str
) -> None:
    cases: list[tuple[Literal["d", "f"], str]] = [
        ("d", expected_dir),
        ("f", expected_file),
    ]
    for shortcut_type, expected in cases:
        shortcut = Shortcut(
            type=shortcut_type,
            path=HOME / "Documents",
            alias_map={"default": [""]},
        )
        assert expected in renderer.compose_shortcut(["d"], shortcut)


@pytest.mark.parametrize(
    "renderer, expected",
    [
        pytest.param(ZSH, "function doc() {", id="zsh"),
        pytest.param(NVIM, "vim.api.nvim_set_keymap(", id="nvim"),
        pytest.param(
            YAZI,
            "    { on = ['b', 'd', 'o', 'c'], "
            'run = "cd \\"/Users/mock/Documents\\"", '
            'desc = "" },',
            id="yazi",
        ),
    ],
)
def test_renderer_no_description(renderer: ShortcutRenderer, expected: str) -> None:
    shortcut = Shortcut(
        type="d",
        path=HOME / "Documents",
        alias_map={"default": [""]},
    )
    assert renderer.compose_shortcut(["d", "o", "c"], shortcut).startswith(expected)


@pytest.mark.parametrize(
    "renderer, path, expected",
    [
        pytest.param(
            ZSH,
            HOME / "Student marks",
            """\
function stum() {
    cd '/Users/mock/Student marks' && ls
}
hash -d stum='/Users/mock/Student marks'
""",
            id="zsh_space",
        ),
        pytest.param(
            ZSH,
            HOME / 'Student\'s "marks"',
            # TODO: use proper quoting
            """\
function stum() {
    cd '/Users/mock/Student'"'"'s "marks"' && ls
}
hash -d stum='/Users/mock/Student'"'"'s "marks"'
""",
            id="zsh_quote",
        ),
        pytest.param(
            NVIM,
            HOME / "Student marks",
            "vim.api.nvim_set_keymap(\n"
            '    "c",\n'
            '    ";stum",\n'
            '    "/Users/mock/Student marks",\n'
            "    { noremap = true }\n"
            ")\n",
            id="nvim_space",
        ),
        pytest.param(
            NVIM,
            HOME / 'Student\'s "marks"',
            "vim.api.nvim_set_keymap(\n"
            '    "c",\n'
            '    ";stum",\n'
            '    "/Users/mock/Student\'s \\\\\\"marks\\\\\\"",\n'
            "    { noremap = true }\n"
            ")\n",
            id="nvim_quote",
        ),
        pytest.param(
            YAZI,
            HOME / "Student marks",
            """    { on = ['b', 's', 't', 'u', 'm'], run = "cd \\"/Users/mock/Student marks\\"", desc = "" },""",
            id="yazi_space",
        ),
        pytest.param(
            YAZI,
            # TODO: use proper quoting
            HOME / 'Student\'s "marks"',
            """    { on = ['b', 's', 't', 'u', 'm'], run = "cd \\"/Users/mock/Student's \\\\\\"marks\\\\\\"\\"", desc = "" },""",
            id="yazi_quote",
        ),
    ],
)
def test_render_require_quoting(
    renderer: ShortcutRenderer,
    path: Path,
    expected: str,
) -> None:
    shortcut = Shortcut(
        type="d",
        path=path,
        alias_map={"default": [""]},
    )

    assert renderer.compose_shortcut(["s", "t", "u", "m"], shortcut) == expected


@pytest.mark.parametrize(
    "platform_name, command",
    [
        ("darwin", "open"),
        ("linux", "xdg-open"),
        ("win32", "$EDITOR"),
        ("unknown", "$EDITOR"),
    ],
)
def test_compose_platforms(
    platform_name: Literal["darwin", "linux", "win32", "unknown"],
    command: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "platform", platform_name)
    path = HOME / "University" / "Timetable.pdf"
    shortcut = Shortcut(
        type="f",
        alias_map={"default": [""]},
        path=path,
    )

    assert f"&& {command} {str(path)}" in ZSH.compose_shortcut(
        ["u", "n", "i", "t"], shortcut
    )


@pytest.mark.parametrize(
    "type, expected",
    [
        pytest.param(
            "d",
            "cd /Users/mock/Documents && ls && penva",
            id="directory",
        ),
        pytest.param(
            "f",
            "cd /Users/mock && ls && penva && open /Users/mock/Documents",
            id="file",
        ),
    ],
)
def test_compose_activate_penv(
    type: Literal["d"] | Literal["f"], expected: str
) -> None:
    shortcut = Shortcut(
        type=type,
        path=HOME / "Documents",
        alias_map={"default": [""]},
        activate_python_env=True,
    )
    assert expected in ZSH.compose_shortcut(["d", "o", "c"], shortcut)

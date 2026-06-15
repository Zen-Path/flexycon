import json
from pathlib import Path
from typing import Any

from scripts.dunst_config_compiler.src.config import DUNST_SETTINGS

COLON_SEPARATED_KEYS = ["icon_path"]


def format_val(key: str, val: Any) -> str:
    if isinstance(val, bool):
        return "true" if val else "false"

    if isinstance(val, (int, float)):
        return str(val)

    if isinstance(val, tuple):
        if all(isinstance(item, (int, float)) for item in val):
            return str(val)

    if isinstance(val, list):
        if all(isinstance(item, str) for item in val):
            val = ", ".join(str(item) for item in val)

        elif key in COLON_SEPARATED_KEYS:
            val = ";".join(str(item) for item in val)

    if isinstance(val, Path):
        val = str(val)

    return json.dumps(val)


def compose_config_file() -> str:
    dict_data = DUNST_SETTINGS.model_dump(by_alias=True, exclude_none=True)

    sections: list[list[str]] = []

    for section_name, section_content in dict_data.items():
        section: list[str] = []

        section.append(f"[{section_name}]")

        for key, val in section_content.items():
            val_fmt = format_val(key, val)
            section.append(f"    {key} = {val_fmt}")

        sections.append(section)

    preamble = "# Generated automatically via Dunst Python Compiler"
    content = "\n\n".join(["\n".join(section) for section in sections])

    return f"{preamble}\n\n{content}\n"

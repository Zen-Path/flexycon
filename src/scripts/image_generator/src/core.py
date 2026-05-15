import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeIs

from common.logger import log


@dataclass
class ImageConfig:
    block_size: int = 25

    font_size: int = 11
    font_color: str = "#928374"

    outline_thickness: float = 0.5
    outline_color: str = "#dddddd"

    show_labels: bool = True


def is_grid(val: Any) -> TypeIs[list[list[int]]]:
    """Narrow the type from Any to list[list[int]]."""
    if not isinstance(val, list):
        return False

    for row in val:  # type: ignore
        if not isinstance(row, list):
            return False
        for cell in row:  # type: ignore
            # Explicitly exclude bools because in Python True/False are ints
            if not isinstance(cell, int) or isinstance(cell, bool):
                return False

    return True


def load_grid_from_json(path: Path | str) -> list[list[int]] | None:
    """
    Loads and validates a 2D integer grid from a JSON file.
    Returns the grid if valid, otherwise returns None.
    """
    path = Path(path)

    if not path.exists():
        log.error(f"Input file not found: {str(path)!r}")
        return None

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if is_grid(data):
            return data

        log.error(f"Invalid grid structure or data types in {str(path)!r}")
        return None

    except json.JSONDecodeError as e:
        log.error(f"Failed to parse JSON in {str(path)!r}: {e}")
        return None


def generate_svg(
    grid: list[list[int]],
    colors: list[str] | None = None,  # TODO: allow for Color objects
    config: ImageConfig | None = None,
    output_path: Path | None = None,
    coordinate_start: int = 1,
) -> Path:
    """
    Generates an SVG representation of a 2D integer grid.

    Each integer in the grid corresponds to an index in the colors list.
    The function handles coordinate offsets, label rendering, and styling
    based on the provided ImageConfig.

    Args:
        grid: A 2D list of integers representing the pixel/block map
        colors: A list of hex color strings. Defaults to black and white
        config: An ImageConfig instance
        output_path: Destination path for the SVG file. If None, defaults
            to 'image.svg' in the current directory.
        coordinate_start: The starting index for row/column labels

    Returns:
        Path: The path where the SVG was saved.
    """

    colors = colors or ["#000000", "#FFFFFF"]
    config = config or ImageConfig()
    output_path = output_path or Path("image.svg")

    log.debug(config)

    rows = len(grid)
    cols = len(grid[0])

    # Calculate margins based on whether labels are enabled
    offset_x = config.block_size if config.show_labels else 0
    offset_y = config.block_size if config.show_labels else 0

    grid_width = cols * config.block_size
    grid_height = rows * config.block_size

    total_width = grid_width + offset_x
    total_height = grid_height + offset_y

    svg = [
        f'<svg width="{total_width}" height="{total_height}" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges">'
    ]

    # Draw the coordinate labels only if enabled
    if config.show_labels:
        for c in range(cols):
            x = offset_x + (c * config.block_size) + int(config.block_size / 2)
            y = offset_y - 10
            svg.append(
                f'  <text x="{x}" y="{y}" font-family="monospace" font-size="{config.font_size}" fill="{config.font_color}" text-anchor="middle">{c + coordinate_start}</text>'
            )

        for r in range(rows):
            x = offset_x - 10
            y = offset_y + (r * config.block_size) + int(config.block_size / 2)
            svg.append(
                f'  <text x="{x}" y="{y}" font-family="monospace" font-size="{config.font_size}" fill="{config.font_color}" text-anchor="end" dominant-baseline="middle">{r + coordinate_start}</text>'
            )

    # Draw the grid
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val == 0:
                fill_color = "none"  # make the cell transparent
            else:
                # fallback to white
                fill_color = colors[val - 1] if val < len(colors) else "#FFFFFF"

            x = offset_x + (c * config.block_size)
            y = offset_y + (r * config.block_size)

            svg.append(
                f'  <rect x="{x}" y="{y}" width="{config.block_size}" height="{config.block_size}" '
                f'fill="{fill_color}" stroke="{config.outline_color}" stroke-width="{config.outline_thickness}" />'
            )

    svg.append("</svg>")

    with open(output_path, "w") as f:
        f.write("\n".join(svg))

    return output_path

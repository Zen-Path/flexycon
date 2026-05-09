import argparse
import logging
from pathlib import Path
from typing import Any

from common.helpers import get_version
from common.logger import logger, setup_logging

# Only needed for demo
from scripts.image_generator.data import references


def generate_svg(
    grid: list[list[int]],
    colors: list[str],
    config: dict[str, Any] | None = None,
    output_file: Path | str = "blueprint.svg",
    coordinate_start: int = 1,
):
    rows = len(grid)
    cols = len(grid[0])

    # Extract config values
    config = config or {}
    b_size = config.get("block_size", 25)
    f_size = config.get("font_size", 11)
    f_color = config.get("font_color", "#928374")

    out_color = config.get("outline_color", "#dddddd")
    out_thick = config.get("outline_thickness", 0.5)

    show_labels = config.get("show_labels", True)

    # Calculate margins based on whether labels are enabled
    offset_x = b_size if show_labels else 0
    offset_y = b_size if show_labels else 0

    grid_w = cols * b_size
    grid_h = rows * b_size

    total_w = grid_w + offset_x
    total_h = grid_h + offset_y

    svg = [
        f'<svg width="{total_w}" height="{total_h}" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges">'
    ]

    # Draw the coordinate labels only if enabled
    if show_labels:
        for c in range(cols):
            x = offset_x + (c * b_size) + (b_size / 2)
            y = offset_y - 10
            svg.append(
                f'  <text x="{x}" y="{y}" font-family="monospace" font-size="{f_size}" fill="{f_color}" text-anchor="middle">{c + coordinate_start}</text>'
            )

        for r in range(rows):
            x = offset_x - 10
            y = offset_y + (r * b_size) + (b_size / 2)
            svg.append(
                f'  <text x="{x}" y="{y}" font-family="monospace" font-size="{f_size}" fill="{f_color}" text-anchor="end" dominant-baseline="middle">{r + coordinate_start}</text>'
            )

    # Draw the grid
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val == 0:
                fill_color = "none"  # make the cell transparent
            else:
                # fallback to white
                fill_color = colors[val] if val < len(colors) else "#FFFFFF"

            x = offset_x + (c * b_size)
            y = offset_y + (r * b_size)

            svg.append(
                f'  <rect x="{x}" y="{y}" width="{b_size}" height="{b_size}" '
                f'fill="{fill_color}" stroke="{out_color}" stroke-width="{out_thick}" />'
            )

    svg.append("</svg>")

    output_file = Path(output_file)
    with open(output_file, "w") as f:
        f.write("\n".join(svg))

    logger.info(f"Blueprint saved to {output_file!r}")


COLORS = ["transparent", "#458588", "#cc241d", "#458588"]


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="image_generator", description="Generate an svg image from a pixel map."
    )

    parser.add_argument(
        "--no-frame", action="store_true", help="hide labels and margins"
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    return parser


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.ERROR)

    config = {"show_labels": not args.no_frame}

    generate_svg(
        grid=references.EMOJI_SMILE, colors=COLORS, config=config, coordinate_start=0
    )


if __name__ == "__main__":
    main()

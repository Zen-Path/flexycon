import argparse
import logging
from dataclasses import fields
from pathlib import Path

from common.helpers import get_version
from common.logger import logger, setup_logging
from scripts.image_generator.data import references  # Only needed for demo
from scripts.image_generator.src.core import (
    ImageConfig,
    generate_svg,
    load_grid_from_json,
)

GENERATORS = {
    "svg": (ImageConfig, generate_svg),
}


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="image_generator",
        description="Generate an image representation of a 2D integer grid.",
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    # SUBCOMMANDS
    cmd_parent = argparse.ArgumentParser(add_help=False)
    cmd_parent.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="enable debug output",
    )

    subparsers = parser.add_subparsers(dest="image_type", metavar="IMAGE_TYPE")
    # TODO: allow for more image types. use base config and factory pattern to
    # automatically call an image type with its specific configuration options.

    ## SVG
    svg_sp = subparsers.add_parser(name="svg", parents=[cmd_parent])

    svg_cfg_group = svg_sp.add_argument_group(title="config")
    svg_cfg_group.add_argument(
        "--no-labels",
        dest="show_labels",
        action="store_false",
        default=True,
        help="hide labels like block number",
    )

    svg_cfg_group.add_argument(
        "--block-size",
        type=int,
        help="define the width and height of a block",
    )

    svg_cfg_group.add_argument("--font-size", type=int)
    svg_cfg_group.add_argument("--font-color", type=str)

    svg_cfg_group.add_argument(
        "--outline-thickness",
        type=float,
        help="define the thickness of a block's outline",
    )
    svg_cfg_group.add_argument("--outline-color", type=str)

    svg_path_group = svg_sp.add_argument_group(title="path")
    svg_path_group.add_argument("-i", "--input-path", type=Path)
    svg_path_group.add_argument("-o", "--output-path", type=Path)

    return parser


def main() -> None:
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.ERROR)
    logger.debug(args)

    config_cls, generator_fn = GENERATORS[args.image_type]

    # Build config from CLI
    args_dict = vars(args)
    config_fields: set[str] = {f.name for f in fields(ImageConfig)}

    provided_config = {
        k: v for k, v in args_dict.items() if k in config_fields and v is not None
    }

    config = config_cls(**provided_config)

    # Data loading
    grid = None
    if args.input_path:
        grid = load_grid_from_json(args.input_path)
        if grid is None:
            logger.error(f"Unable to load input data from {str(args.input_path)!r}")
            return

    if grid is None:
        logger.warning("No input path provided. Defaulting to demo data.")
        grid = references.EMOJI_SMILE

    # Execution
    COLORS = ["#cc241d", "#458588", "#458588"]
    output_path = generator_fn(
        grid=grid,
        colors=COLORS,
        config=config,
        output_path=args.output_path,
        coordinate_start=0,
    )

    logger.info(f"Saved image to {str(output_path)!r}")


if __name__ == "__main__":
    main()

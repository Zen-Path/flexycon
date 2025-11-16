import argparse
import logging
import sys

from common.logger import logger, setup_logging
from scripts.media_manager.src.core import (
    handle_audio,
    handle_image,
    handle_pdf,
    handle_video,
)


def build_parser():
    parser = argparse.ArgumentParser(description="Media Manager CLI")

    subparsers = parser.add_subparsers(dest="media_type", required=True)

    image = subparsers.add_parser("image", help="Image operations")
    image.set_defaults(func=handle_image)

    video = subparsers.add_parser("video", help="Video operations")
    video.set_defaults(func=handle_video)

    audio = subparsers.add_parser("audio", help="Audio operations")
    audio.set_defaults(func=handle_audio)

    pdf = subparsers.add_parser("pdf", help="PDF operations")
    pdf.set_defaults(func=handle_pdf)

    for sp in [image, video, audio, pdf]:
        sp.add_argument(
            "-i", "--input", nargs="+", required=True, help="one or more input files"
        )
        sp.add_argument(
            "-o",
            "--output",
            nargs="+",
            help="output files (must match number of inputs)",
        )

        sp.add_argument("-c", "--convert", help="format to convert to")
        sp.add_argument("-C", "--compress", type=int, help="compression level/quality")

    for sp in [image, video, pdf]:
        sp.add_argument("-r", "--rotate", type=int, help="rotate image by degrees")

    video.add_argument("--extract-audio", action="store_true", help="extract audio")

    # Keep verbose at the end of the arguments
    for sp in [image, video, audio, pdf]:
        sp.add_argument("--verbose", action="store_true", help="enable debug output")

    return parser


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.WARNING)

    if args.output:
        if len(args.input) != len(args.output):
            logger.error(
                f"Number of output paths ({len(args.output)}) does not match "
                f"number of input paths ({len(args.input)})."
            )
            sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()

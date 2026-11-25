#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import sys

from common.helpers import get_version
from common.logger import log, setup_logging
from scripts.yt_manager.src.core import (
    handle_audio,
    handle_stream,
    handle_thumb,
    handle_video,
)
from scripts.yt_manager.src.helpers import (
    VALID_AUDIO_MODES,
    VALID_IMAGE_FORMATS,
    VALID_VIDEO_FORMATS,
    validate_quality,
    validate_range_value,
)


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="yt_manager",
        description="YouTube media downloader and streamer utility",
    )

    subparsers = parser.add_subparsers(dest="action", required=True)

    thumb = subparsers.add_parser("thumb", help="Download video thumbnail")
    thumb.set_defaults(func=handle_thumb)

    stream = subparsers.add_parser("stream", help="Stream video in mpv")
    stream.set_defaults(func=handle_stream)

    video = subparsers.add_parser("video", help="Download video, playlist, or clip")
    video.set_defaults(func=handle_video)

    audio = subparsers.add_parser("audio", help="Download audio, playlist, or clip")
    audio.set_defaults(func=handle_audio)

    # Common URL argument across all subcommands
    for sp in [thumb, stream, video, audio]:
        sp.add_argument("url", help="YouTube URL")

    # Thumb options
    thumb.add_argument(
        "-f",
        "--format",
        choices=VALID_IMAGE_FORMATS,
        type=str.lower,
        default=None,
        help="target image format (omit for best native format)",
    )

    # Stream options
    stream.add_argument(
        "-q",
        "--quality",
        type=validate_quality,
        default="best",
        help="max vertical resolution (e.g., 720, 1080) or 'best'",
    )

    # Video options
    video.add_argument(
        "-q",
        "--quality",
        type=validate_quality,
        default="best",
        help="max vertical resolution (e.g., 720, 1080) or 'best'",
    )
    video.add_argument(
        "-f",
        "--format",
        choices=VALID_VIDEO_FORMATS,
        default="mp4",
        help="output container format (default: mp4)",
    )
    video.add_argument(
        "--no-thumb",
        dest="thumb",
        action="store_false",
        help="do not embed thumbnail",
    )

    # Audio options
    audio.add_argument(
        "-m",
        "--mode",
        choices=VALID_AUDIO_MODES,
        default="amusic",
        help="audio preset (default: amusic)",
    )

    # Shared playlist & clipping options for video and audio
    for sp in [video, audio]:
        sp.add_argument(
            "-p",
            "--playlist",
            action="store_true",
            help="download playlist into a dedicated folder",
        )
        sp.add_argument(
            "-s",
            "--start",
            type=validate_range_value,
            help="clip start timestamp (MM:SS) or playlist start index (e.g., 1)",
        )
        sp.add_argument(
            "-e",
            "--end",
            type=validate_range_value,
            help="clip end timestamp (MM:SS) or playlist end index (e.g., 5)",
        )

    # Keep dry-run and verbose at the end of the arguments
    for sp in [thumb, stream, video, audio]:
        sp.add_argument(
            "--dry-run",
            action="store_true",
            help="print underlying command without executing",
        )
        sp.add_argument(
            "-v", "--verbose", action="store_true", help="enable debug output"
        )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    return parser


def main() -> None:
    args = build_parser().parse_args()

    setup_logging(log, logging.DEBUG if args.verbose else logging.WARNING)
    log.debug(args)

    try:
        args.func(args)
    except ValueError as exc:
        log.error(str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()

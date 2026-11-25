import argparse

from common.cmd_utilities import run_cmd
from scripts.yt_manager.src.helpers import (
    build_audio_cmd,
    build_stream_cmd,
    build_thumb_cmd,
    build_video_cmd,
)


def handle_thumb(args: argparse.Namespace) -> None:
    cmd = build_thumb_cmd(url=args.url, fmt=args.format)
    run_cmd(cmd, dry_run=args.dry_run)


def handle_stream(args: argparse.Namespace) -> None:
    cmd = build_stream_cmd(url=args.url, quality=args.quality)
    run_cmd(cmd, dry_run=args.dry_run)


def handle_video(args: argparse.Namespace) -> None:
    cmd = build_video_cmd(
        url=args.url,
        quality=args.quality,
        fmt=args.format,
        playlist=args.playlist,
        thumb=args.thumb,
        start=args.start,
        end=args.end,
    )
    run_cmd(cmd, dry_run=args.dry_run)


def handle_audio(args: argparse.Namespace) -> None:
    cmd = build_audio_cmd(
        url=args.url,
        mode=args.mode,
        playlist=args.playlist,
        start=args.start,
        end=args.end,
    )
    run_cmd(cmd, dry_run=args.dry_run)

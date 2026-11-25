# {{@@ header() @@}}

import pytest

from scripts.yt_manager.main import build_parser
from scripts.yt_manager.src.helpers import (
    build_audio_cmd,
    build_stream_cmd,
    build_thumb_cmd,
    build_video_cmd,
)


def test_parser_defaults():
    parser = build_parser()
    args = parser.parse_args(["audio", "https://youtu.be/abc"])
    assert args.action == "audio"
    assert args.mode == "amusic"
    assert args.playlist is False
    assert args.start is None
    assert args.end is None


def test_thumb_native_vs_converted():
    cmd_native = build_thumb_cmd("https://youtu.be/abc")
    assert "--convert-thumbnails" not in cmd_native
    assert "%(title)s [%(id)s].%(ext)s" in cmd_native

    cmd_jpg = build_thumb_cmd("https://youtu.be/abc", "jpeg")
    idx = cmd_jpg.index("--convert-thumbnails")
    assert cmd_jpg[idx + 1] == "jpg"


def test_stream_quality_cap():
    cmd = build_stream_cmd("https://youtu.be/abc", "1080")
    assert "--ytdl-format=bestvideo[height<=1080]+bestaudio/best[height<=1080]" in cmd
    assert "--slang=en,ro" in cmd


def test_audio_open_ended_clip():
    cmd = build_audio_cmd(url="https://youtu.be/abc", mode="m4a", start="14:20")
    assert "*14:20-inf" in cmd
    assert "%(title)s [%(id)s] [14-20_inf].%(ext)s" in cmd


def test_video_clip():
    cmd = build_video_cmd(
        url="https://youtu.be/abc",
        quality="720",
        fmt="mp4",
        playlist=False,
        thumb=False,
        start="01:15",
        end="02:30",
    )
    assert "--no-playlist" in cmd
    assert "--embed-thumbnail" not in cmd
    assert "*01:15-02:30" in cmd
    assert "%(title)s [%(id)s] [01-15_02-30].%(ext)s" in cmd


def test_video_playlist_range():
    cmd = build_video_cmd(
        url="https://www.youtube.com/watch?v=abc&list=PL12345",
        quality="720",
        fmt="mp4",
        playlist=True,
        thumb=False,
        start="1",
        end="5",
    )
    assert "--yes-playlist" in cmd
    assert "--download-sections" not in cmd
    assert cmd[cmd.index("--playlist-items") + 1] == "1:5"
    assert (
        "%(playlist_title|YouTube Playlist)s [%(playlist_id)s]/%(playlist_index)02d - %(title)s [%(id)s].%(ext)s"
        in cmd
    )


def test_playlist_end_only():
    cmd = build_audio_cmd(url="https://youtu.be/abc", playlist=True, end="5")
    idx = cmd.index("--playlist-items")
    assert cmd[idx + 1] == ":5"


def test_playlist_rejects_timestamp():
    with pytest.raises(ValueError, match="positive integer index"):
        build_video_cmd(url="https://youtu.be/abc", playlist=True, start="01:15")


def test_clip_end_without_start_defaults_to_zero():
    cmd = build_audio_cmd("https://youtu.be/abc", playlist=False, end="01:00")
    assert "*0-01:00" in cmd
    assert "%(title)s [%(id)s] [0_01-00].%(ext)s" in cmd

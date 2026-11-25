import argparse
import re

VALID_IMAGE_FORMATS = ("jpg", "jpeg", "png", "webp")
VALID_VIDEO_FORMATS = ("mp4", "mkv", "webm")
VALID_AUDIO_MODES = ("amusic", "m4a", "mp3", "best")
RANGE_VALUE_RE = re.compile(r"^(\d{1,2}:)?\d{1,2}:\d{2}(\.\d+)?$|^\d+(\.\d+)?$")


def validate_range_value(value: str) -> str:
    """Validate a timestamp (SS, MM:SS, HH:MM:SS) or a playlist index (integer)."""
    if not RANGE_VALUE_RE.match(value):
        raise argparse.ArgumentTypeError(
            f"Invalid start/end value '{value}'. Use a timestamp (MM:SS, HH:MM:SS) or playlist index (e.g., 1, 5)."
        )
    return value


def validate_quality(value: str) -> str:
    """Validate 'best' or a positive integer resolution height."""
    if value.lower() == "best":
        return "best"
    if value.isdigit() and int(value) > 0:
        return value
    raise argparse.ArgumentTypeError(
        f"Invalid quality '{value}'. Use 'best' or a numeric height (e.g., 720, 1080)."
    )


def sanitize_filename_time(ts: str) -> str:
    """Replace colons in timestamps with hyphens for safe filenames."""
    return ts.replace(":", "-")


def apply_clip_and_playlist(
    cmd: list[str],
    playlist: bool = False,
    start: str | None = None,
    end: str | None = None,
) -> list[str]:
    """Apply playlist range (--playlist-items) or single-video clipping (--download-sections)."""
    if playlist:
        cmd.append("--yes-playlist")

        if start or end:
            if start and (not start.isdigit() or int(start) < 1):
                raise ValueError(
                    f"Playlist --start must be a positive integer index, got '{start}'."
                )
            if end and (not end.isdigit() or int(end) < 1):
                raise ValueError(
                    f"Playlist --end must be a positive integer index, got '{end}'."
                )
            if start and end and int(start) > int(end):
                raise ValueError(
                    f"Playlist --start ({start}) cannot be greater than --end ({end})."
                )

            item_range = f"{start or ''}:{end or ''}"
            cmd.extend(["--playlist-items", item_range])

        cmd.extend(
            [
                "-o",
                "%(playlist_title|YouTube Playlist)s [%(playlist_id)s]/%(playlist_index)02d - %(title)s [%(id)s].%(ext)s",
            ]
        )
        return cmd

    # Single-video / clip mode
    clip_suffix = ""
    if start or end:
        start_val = start or "0"
        end_val = end or "inf"
        cmd.extend(
            [
                "--download-sections",
                f"*{start_val}-{end_val}",
                "--force-keyframes-at-cuts",
            ]
        )
        clip_suffix = (
            f" [{sanitize_filename_time(start_val)}_{sanitize_filename_time(end_val)}]"
        )

    cmd.extend(["--no-playlist", "-o", f"%(title)s [%(id)s]{clip_suffix}.%(ext)s"])
    return cmd


def build_thumb_cmd(url: str, fmt: str | None = None) -> list[str]:
    """Construct yt-dlp command for thumbnail extraction."""
    cmd = [
        "yt-dlp",
        "--ignore-config",
        "--skip-download",
        "--write-thumbnail",
        "-o",
        "%(title)s [%(id)s].%(ext)s",
    ]
    if fmt:
        normalized = "jpg" if fmt.lower() == "jpeg" else fmt.lower()
        cmd.extend(["--convert-thumbnails", normalized])
    cmd.append(url)
    return cmd


def build_stream_cmd(url: str, quality: str = "best") -> list[str]:
    """Construct mpv command for direct streaming with EN/RO subtitles."""
    if quality == "best":
        ytdl_fmt = "bestvideo+bestaudio/best"
    else:
        ytdl_fmt = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"

    return [
        "mpv",
        "--fs",
        "--slang=en,ro",
        f"--ytdl-format={ytdl_fmt}",
        "--ytdl-raw-options=ignore-config=,sub-langs=en.*,ro.*,write-subs=,write-auto-subs=",
        url,
    ]


def build_video_cmd(
    url: str,
    quality: str = "best",
    fmt: str = "mp4",
    playlist: bool = False,
    thumb: bool = True,
    start: str | None = None,
    end: str | None = None,
) -> list[str]:
    """Construct yt-dlp command for video downloads."""
    if quality == "best":
        f_str = f"bv*[ext={fmt}]+ba[ext=m4a]/bv*+ba/b"
    else:
        f_str = (
            f"bv*[height<={quality}][ext={fmt}]+ba[ext=m4a]/"
            f"bv*[height<={quality}]+ba/b[height<={quality}]"
        )

    cmd = [
        "yt-dlp",
        "--ignore-config",
        "--concurrent-fragments",
        "4",
        "-f",
        f_str,
        "--merge-output-format",
        fmt,
        "--embed-metadata",
        "--embed-chapters",
    ]

    if thumb:
        cmd.extend(["--embed-thumbnail", "--convert-thumbnails", "jpg"])

    apply_clip_and_playlist(cmd, playlist=playlist, start=start, end=end)
    cmd.append(url)
    return cmd


def build_audio_cmd(
    url: str,
    mode: str = "amusic",
    playlist: bool = False,
    start: str | None = None,
    end: str | None = None,
) -> list[str]:
    """Construct yt-dlp command for audio downloads."""
    cmd = [
        "yt-dlp",
        "--ignore-config",
        "--concurrent-fragments",
        "4",
        "--extract-audio",
        "--embed-metadata",
    ]

    if mode == "amusic":
        cmd.extend(
            [
                "-f",
                "ba[ext=m4a]",
                # Parse into artist & meta_title so %(title)s stays intact for the filename
                "--parse-metadata",
                "title:%(artist)s - %(meta_title)s",
                "--parse-metadata",
                "uploader:%(artist)s - Topic",
                "--embed-chapters",
                "--embed-thumbnail",
                "--convert-thumbnails",
                "jpg",
                "--postprocessor-args",
                'Metadata:-metadata album="YouTube Downloads" -metadata album_artist="Various Artists"',
            ]
        )
    elif mode == "m4a":
        cmd.extend(["-f", "ba[ext=m4a]"])
    elif mode == "mp3":
        cmd.extend(
            [
                "--audio-format",
                "mp3",
                "--audio-quality",
                "0",
                "--embed-thumbnail",
                "--convert-thumbnails",
                "jpg",
            ]
        )
    elif mode == "best":
        cmd.extend(["-f", "bestaudio/best"])
    else:
        raise ValueError(f"Unsupported audio mode: {mode}")

    apply_clip_and_playlist(cmd, playlist=playlist, start=start, end=end)
    cmd.append(url)
    return cmd

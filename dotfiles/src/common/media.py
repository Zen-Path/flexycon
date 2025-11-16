import os
from pathlib import Path
from typing import Optional

from common.helpers import run_command
from common.logger import logger

# IMAGES


def compress_image(
    input_path: Path, output_path: Optional[Path] = None
) -> Optional[Path]:
    """
    Compress jpg / jpeg / png image.
    Output path: <filename>-compressed<extension>
    """
    filename, extension = os.path.splitext(input_path)
    if not output_path:
        output_path = Path(f"{filename}-compressed{extension}")

    match extension.lstrip("."):
        case "jpg" | "jpeg":
            # fmt: off
            run_command([
                "ffmpeg",
                "-i", str(input_path),
                "-q:v", "10",
                str(output_path)
            ])
            # fmt: on
        case "png":
            # fmt: off
            run_command([
                "ffmpeg",
                "-i", str(input_path),
                "-compression_level", "9",
                str(output_path),
            ])
            # fmt: on
        case _:
            logger.error(f"Unsupported image format: {extension}")
            return None

    return output_path


def rotate_image(
    input_path: Path, degrees: int, output_path: Optional[Path] = None
) -> Path:
    """
    Rotates image by degrees.
    """
    if not output_path:
        output_path = input_path

    run_command(["magick", str(input_path), "-rotate", str(degrees), str(output_path)])

    return output_path


# VIDEOS


def convert_video_to_mp4(input_path: Path, output_path: Optional[Path] = None) -> Path:
    """
    Converts video to mp4.
    Output path: <filename>.mp4
    """
    if not output_path:
        filename, extension = os.path.splitext(input_path)
        output_path = Path(f"{filename}.mp4")

    # fmt: off
    run_command([
        "ffmpeg",
        "-fflags", "+genpts",
        "-i", str(input_path),
        "-r", "24",
        str(output_path)
    ])
    # fmt: on

    return output_path


def compress_video(input_path: Path, output_path: Optional[Path] = None) -> Path:
    """
    Converts video to codec x264.
    Output path: <filename>-compressed<extension>
    """
    if not output_path:
        filename, extension = os.path.splitext(input_path)
        output_path = Path(f"{filename}-compressed{extension}")

    # fmt: off
    run_command([
        "ffmpeg",
        "-i", str(input_path),
        "-vcodec", "libx264",
        "-crf", "28",
        str(output_path),
    ])
    # fmt: on

    return output_path


def rotate_video(
    input_path: Path, degrees: int, output_path: Optional[Path] = None
) -> Path:
    """
    Rotate a video by any degree value.

    - Uses fast lossless transpose for multiples of 90°
    - Uses rotate filter for arbitrary angles
    """
    if not output_path:
        filename, extension = os.path.splitext(input_path)
        output_path = Path(f"{filename}-audio{extension}")

    deg = degrees % 360

    # Transpose is lossless, so if possible, we prefer it
    if deg == 90:
        vf = "transpose=1"
    elif deg == 180:
        vf = "transpose=1,transpose=1"
    elif deg == 270:
        vf = "transpose=2"
    elif deg == 0:
        # No rotation, just copy input
        # fmt: off
        run_command([
            "ffmpeg",
            "-i", str(input_path),
            "-c", "copy",
            str(output_path)
        ])
        # fmt: on
        return output_path
    else:
        vf = f"rotate={deg}*PI/180"

    # fmt: off
    run_command([
        "ffmpeg",
        "-i", str(input_path),
        "-vf", vf,
        "-preset", "fast",
        "-y",
        str(output_path)
    ])
    # fmt: on

    return output_path


def extract_audio_from_video(
    input_path: Path, output_path: Optional[Path] = None
) -> Path:
    """
    Converts input video to audio using ffmpeg.
    Output path: <filename>-audio<extension>
    """
    if not output_path:
        filename, extension = os.path.splitext(input_path)
        output_path = Path(f"{filename}-audio{extension}")

    # fmt: off
    run_command([
        "ffmpeg",
        "-i", str(input_path),
        "-q:a", "0",
        "-map", "a",
        str(output_path)
    ])
    # fmt: on

    return output_path


# PDF


def compress_pdf(input_path: Path, output_path: Optional[Path] = None) -> Path:
    """
    Compress pdf.
    Output path: <filename>-compressed<extension>
    """
    if not output_path:
        filename, extension = os.path.splitext(input_path)
        output_path = Path(f"{filename}-compressed{extension}")

    run_command(
        [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dDownsampleColorImages=true",
            "-dColorImageResolution=150",
            "-dNOPAUSE",
            "-dBATCH",
            f'-sOutputFile="{output_path}"',
            str(input_path),
        ]
    )

    return output_path


def convert_pdf_to_png(input_path: Path, output_path: Optional[Path] = None) -> Path:
    """
    Convert a pdf file to a png.
    Output path: <filename>-compressed<extension>
    """
    if not output_path:
        filename, extension = os.path.splitext(input_path)
        output_path = Path(f"{filename}.png")

    # fmt: off
    run_command(
        [
            "magick",
            "-density", "300",
            str(input_path),
            "-quality", "100",
            "-alpha", "remove",
            str(output_path)
        ]
    )
    # fmt: on

    return output_path


# MISC


def trim_media(
    input_path: Path,
    start_time: str,
    duration_s: int,
    output_path: Optional[Path] = None,
) -> Path:
    """
    Trims media from a start time to finish time.
    Output path: <filename>-trimmed<extension>
    """
    if not output_path:
        filename, extension = os.path.splitext(input_path)
        output_path = Path(f"{filename}-trimmed{extension}")

    # fmt: off
    run_command([
        "ffmpeg",
        "-i", str(input_path),
        "-ss", start_time,
        "-t", str(duration_s),
        "-c", "copy",
        str(output_path),
    ])
    # fmt: on

    return output_path

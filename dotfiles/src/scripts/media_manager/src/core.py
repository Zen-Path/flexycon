from common.logger import logger
from common.media import (
    compress_image,
    compress_pdf,
    compress_video,
    convert_pdf_to_png,
    convert_video_to_mp4,
    extract_audio_from_video,
    rotate_image,
    rotate_video,
)


def handle_image(args):
    for i, input_path in enumerate(args.input):
        output_path = args.output[i] if args.output else None

        if args.compress:
            compress_image(input_path, output_path)

        if args.rotate:
            logger.debug(f"Rotating image {input_path!r} by {args.rotate!r} degrees.")
            rotate_image(input_path, args.rotate, output_path)


def handle_video(args):
    for i, input_path in enumerate(args.input):
        output_path = args.output[i] if args.output else None

        if args.convert:
            if args.convert == "mp4":
                convert_video_to_mp4(input_path, output_path)

        if args.compress:
            compress_video(input_path, output_path)

        if args.rotate:
            rotate_video(input_path, args.rotate, output_path)

        if args.extract_audio:
            extract_audio_from_video(input_path, output_path)


def handle_audio(args):
    for i, input_path in enumerate(args.input):
        _ = args.output[i] if args.output else None

        if args.convert:
            pass

        if args.compress:
            pass


def handle_pdf(args):
    for i, input_path in enumerate(args.input):
        output_path = args.output[i] if args.output else None

        if args.convert:
            logger.debug(f"Converting PDF {args.input!r} to a {args.convert!r} file.")

            if args.convert == "png":
                convert_pdf_to_png(input_path, output_path)
                return

        if args.compress:
            compress_pdf(input_path, output_path)

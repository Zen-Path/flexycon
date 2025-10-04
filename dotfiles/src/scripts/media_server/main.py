import argparse
import atexit
import logging
import os
from pathlib import Path

from common.logger import logger, setup_logging
from flask import Flask
from flask_cors import CORS
from scripts.media_server.routes.media import media_bp
from scripts.media_server.src.history import HistoryLogger
from scripts.media_server.src.logging_middleware import register_logging

DATA_HOME_DIR = (
    Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local/share")) / "flexycon"
)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Media server to download files from the web."
    )

    parser.add_argument("--verbose", action="store_true", help="enable debug output")

    parser.add_argument(
        "--history-path",
        type=Path,
        default=DATA_HOME_DIR / "history.json",
        help="Path to the config file",
    )

    return parser


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.WARNING)
    logger.debug(args)

    # Flask setup
    app = Flask(__name__)
    app.register_blueprint(media_bp)
    register_logging(app)

    CORS(app)  # Enable CORS for all routes

    app.extensions["history_logger"] = HistoryLogger(args.history_path)
    atexit.register(lambda: app.extensions["history_logger"].flush())

    app.run(port=5000, debug=False)


if __name__ == "__main__":
    main()

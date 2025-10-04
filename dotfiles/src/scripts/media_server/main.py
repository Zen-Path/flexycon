import argparse
import atexit
import json
import logging
from datetime import datetime

from colorama import Fore, Style
from common.logger import logger, setup_logging
from flask import Flask, current_app, g, jsonify, request
from flask_cors import CORS
from scripts.media_server.src.history import HistoryEntry, HistoryLogger
from scripts.media_server.src.models import Gallery
from scripts.media_server.src.logging_middleware import register_logging

# Flask setup
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes




def build_parser():
    parser = argparse.ArgumentParser(
        description="Media server to download files from the web."
    )

    parser.add_argument("--verbose", action="store_true", help="enable debug output")

    return parser


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.WARNING)

    app.extensions["history_logger"] = HistoryLogger()
    atexit.register(lambda: app.extensions["history_logger"].flush())

    app.run(port=5000, debug=True)


if __name__ == "__main__":
    main()

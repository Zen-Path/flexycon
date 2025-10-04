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

# Flask setup
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


def skip_logging(f):
    """Decorator to mark a route to skip logging."""
    f._skip_logging = True
    return f


@app.before_request
def log_request():
    view_func = app.view_functions.get(request.endpoint)
    if getattr(view_func, "_skip_logging", False):
        g.skip_logging = True
        return

    params = request.args.to_dict()
    try:
        data = request.get_json(silent=True)
    except Exception:
        data = None

    if data is None:
        if request.form:
            data = request.form.to_dict()
        else:
            data = request.data.decode("utf-8") if request.data else None

    logger.info(
        f"""{Fore.LIGHTBLUE_EX}REQUEST{Fore.LIGHTBLACK_EX}:
params: {json.dumps(params, indent=4)}
data: {json.dumps(data, indent=4) if isinstance(data, (dict, list)) else data}
{Style.RESET_ALL}"""
    )


@app.after_request
def log_response(response):
    if getattr(g, "skip_logging", False):
        return response

    try:
        json_data = response.get_json()
        json_fmt = json.dumps(json_data, indent=4, ensure_ascii=False)
    except Exception:
        json_fmt = response.get_data(as_text=True)

    logger.info(
        f"{Fore.LIGHTYELLOW_EX}RESPONSE{Fore.LIGHTBLACK_EX}:\n{json_fmt}{Style.RESET_ALL}"
    )
    return response


@app.route("/downloadMedia", methods=["POST"])
def download_media():
    data = request.json
    urls = data.get("urls")
    type_ = data.get("type")

    if not urls or not isinstance(urls, list):
        logger.warning("Invalid or missing 'urls' list in request.")
        return jsonify({"error": "Invalid or missing 'urls' list"}), 400

    try:
        match type_:
            case "gallery":
                cmd_result = Gallery.download(urls)
            case _:
                return jsonify({"error": "'type_' is unknown."}), 400

        current_app.extensions["history_logger"].queue_for_saving(
            [HistoryEntry(urls, type_, datetime.now())]
        )

        return jsonify(
            {
                "return_code": cmd_result.return_code,
                "output": cmd_result.output,
            }
        )

    except Exception as e:
        logger.error(f"Error during execution: {e}")
        return jsonify({"return_code": 1, "error": str(e)}), 500


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

import argparse
import logging

from common.logger import setup_logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from scripts.media_server.src.history import log_history_entry
from scripts.media_server.src.models import Gallery

# Flask setup
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


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
                returncode, output = Gallery.download(urls)
            case _:
                return jsonify({"error": "'type_' is unknown."})

        log_history_entry(urls)

        return jsonify(
            {
                "status": "success" if returncode == 0 else "error",
                "return_code": returncode,
                "output": output,
            }
        )

    except Exception as e:
        logger.error(f"Error during execution: {e}")
        return jsonify({"status": "error", "return_code": -1, "error": str(e)}), 500


def parse_args():
    parser = argparse.ArgumentParser(
        description="Media server to download files from the web."
    )

    parser.add_argument("--verbose", action="store_true", help="enable debug output")

    return parser.parse_args()


def main():
    args = parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.WARNING)

    app.run(port=5000, debug=True)


if __name__ == "__main__":
    main()

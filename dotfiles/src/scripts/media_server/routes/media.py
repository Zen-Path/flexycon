from datetime import datetime

from common.helpers import parse_range
from flask import Blueprint, current_app, jsonify, request
from scripts.media_server.src.history import HistoryEntry
from scripts.media_server.src.models import Gallery

media_bp = Blueprint("media", __name__, url_prefix="/media")


@media_bp.route("/download", methods=["POST"])
def download_media():
    data = request.get_json(silent=True) or {}
    urls = data.get("urls")
    type_ = data.get("type")
    range_raw = data.get("range")

    # Validation
    if (
        not urls
        or not isinstance(urls, list)
        or not all(isinstance(u, str) for u in urls)
    ):
        return jsonify({"error": "'urls' must be a list of strings."}), 400

    if not type_ or not isinstance(type_, str):
        return jsonify({"error": "'type_' must be a non-empty string."}), 400

    range_parts = None
    if range_raw:
        range_parts, error = parse_range(range_raw)
        if error:
            return jsonify({"error": error}), 400

    match type_:
        case "gallery":
            # Pass range_parts only if present
            kwargs = {"range_": range_parts} if range_parts else {}
            cmd_result = Gallery.download(urls, **kwargs)

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

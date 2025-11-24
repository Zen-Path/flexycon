import json
import sqlite3
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from common.helpers import parse_range
from flask import Blueprint, current_app, jsonify, request
from scripts.media_server.src.core import require_api_key
from scripts.media_server.src.models import Gallery

media_bp = Blueprint("media", __name__, url_prefix="/media")


@media_bp.route("/download", methods=["POST"])
@require_api_key
def download_media():
    data = request.get_json(silent=True) or {}
    urls = data.get("urls")
    media_type = data.get("media_type")
    range_raw = data.get("range")

    # Validation

    ## URLs
    if (
        not urls
        or not isinstance(urls, list)
        or not all(isinstance(url, str) for url in urls)
    ):
        return jsonify({"error": "'urls' must be a list of strings."}), 400

    ## Media Type
    if not media_type or not isinstance(media_type, str):
        return jsonify({"error": "'media_type' must be a non-empty string."}), 400

    if media_type not in ["image", "video", "gallery", "unknown"]:
        media_type = "unknown"

    ## Range Parts
    range_parts = None
    if range_raw:
        range_parts, error = parse_range(range_raw)
        if error:
            return jsonify({"error": error}), 400

    # Processing
    for url in urls:
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        title = "No Title Found"

        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                if soup.title and soup.title.string:
                    title = soup.title.string.strip()
            else:
                title = f"Error: {response.status_code}"

        except Exception as e:
            title = "Error: Failed to Connect"

        match media_type:
            case "gallery" | "unknown":
                # Pass range_parts only if present
                kwargs = {"range_parts": range_parts} if range_parts else {}
                cmd_result = Gallery.download([url], **kwargs)

        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save to DB
        with sqlite3.connect(current_app.config["DB_PATH"]) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO downloads (url, title, media_type, start_time, end_time) VALUES (?, ?, ?, ?, ?)",
                (url, title, media_type, start_time, end_time),
            )
            last_id = cursor.lastrowid
            conn.commit()

        # Notify Dashboard
        data = json.dumps(
            {
                "id": last_id,
                "url": url,
                "title": title,
                "media_type": media_type,
                "start_time": start_time,
                "end_time": end_time,
            }
        )
        msg = f"data: {data}\n\n"
        current_app.config["ANNOUNCER"].announce(msg)

    return jsonify({"status": "downloaded", "count": len(urls)})

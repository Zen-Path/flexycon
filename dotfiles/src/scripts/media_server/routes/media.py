import json
import sqlite3
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from common.helpers import run_command
from common.logger import logger
from flask import Blueprint, current_app, jsonify, request
from scripts.media_server.src.downloaders import Gallery

media_bp = Blueprint("media", __name__)


def expand_collection_urls(url):
    """
    Determines if a URL is a collection based on Level Homogeneity. (best effort)
    """
    try:
        cmd = ["gallery-dl", "-s", "-j", url]
        result = run_command(cmd)
        data = json.loads(result.output)

        if not data:
            return [url]

        # Extract levels, ignoring level 1 (which is a generic metadata block)
        levels = [entry[0] for entry in data if entry[0] > 1]

        if not levels:
            return [url]

        unique_levels = set(levels)

        # If there is only ONE unique level (e.g., all are level 6), it is probably
        # a collection of gallery links.
        if len(unique_levels) == 1:
            child_urls = []
            for entry in data:
                # Ensure we only grab strings that look like URLs
                if (
                    len(entry) >= 2
                    and isinstance(entry[1], str)
                    and entry[1].startswith("http")
                ):
                    child_urls.append(entry[1])

            if child_urls:
                return list(dict.fromkeys(child_urls))

        return [url]

    except Exception as e:
        # Fallback to the original URL if anything goes wrong
        logger.error(f"Expansion error for {url}: {e}")
        return [url]


@media_bp.route("/download", methods=["POST"])
def download_media():
    data = request.get_json(silent=True) or {}
    urls = data.get("urls")
    media_type = data.get("mediaType")
    range_start = data.get("rangeStart")
    range_end = data.get("rangeEnd")

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
        return jsonify({"error": "'mediaType' must be a non-empty string."}), 400

    if media_type not in ["image", "video", "gallery", "unknown"]:
        media_type = "unknown"

    ## Range Parts
    if range_start and not isinstance(range_start, int):
        return jsonify({"error": "'rangeStart' must be an int."}), 400

    if range_end and not isinstance(range_end, int):
        return jsonify({"error": "'rangeEnd' must be an int."}), 400

    # Expansion Logic
    final_urls = []
    if media_type in ["gallery", "unknown"]:
        for url in urls:
            expanded = expand_collection_urls(url)
            final_urls.extend(expanded)
    else:
        final_urls = urls

    # Processing
    for url in final_urls:
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

        except Exception:
            title = "Error: Failed to Connect"

        match media_type:
            case "gallery" | "unknown":
                cmd_result = Gallery.download([url], range_start, range_end)

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
                "mediaType": media_type,
                "startTime": start_time,
                "endTime": end_time,
            }
        )
        msg = f"data: {data}\n\n"
        current_app.config["ANNOUNCER"].announce(msg)

    return jsonify({"status": "downloaded", "count": len(final_urls)})

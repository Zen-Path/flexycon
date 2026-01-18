import re
import sqlite3
from datetime import datetime
from typing import Dict, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from common.logger import logger
from flask import Blueprint, current_app, jsonify, request
from scripts.media_server.src.constants import EventType, ScraperConfig
from scripts.media_server.src.downloaders import Gallery
from scripts.media_server.src.utils import DownloadReportItem, expand_collection_urls

media_bp = Blueprint("media", __name__)


def start_download_record(
    url: str, media_type: str
) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Initializes a download entry in the database and notifies the dashboard.

    This function creates a 'shell' record, allowing the system to track that
    a download is active before the heavy processing begins.

    Returns:
        A tuple of (success_status, generated_id, error_message).
    """
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with sqlite3.connect(current_app.config["DB_PATH"]) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO downloads (url, media_type, start_time) VALUES (?, ?, ?)",
                (url, media_type, start_time),
            )
            conn.commit()
            last_id = cursor.lastrowid

        current_app.config["ANNOUNCER"].announce_event(
            EventType.CREATE,
            {
                "id": last_id,
                "url": url,
                "mediaType": media_type,
                "startTime": start_time,
            },
        )

        return True, last_id, None
    except Exception as e:
        err_msg = f"Failed to initialize download record: {e}"
        logger.error(err_msg)
        return False, None, err_msg


def complete_download_record(
    download_id: int, title: Optional[str]
) -> Tuple[bool, Optional[str]]:
    """
    Finalizes an existing download record with its metadata and notifies the dashboard.

    Updates the specific row with the final title and the timestamp of
    completion.

    Returns:
        A tuple of (success_status, error_message).
    """
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with sqlite3.connect(current_app.config["DB_PATH"]) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE downloads
                SET title = ?, end_time = ?
                WHERE id = ?
                """,
                (title, end_time, download_id),
            )
            conn.commit()

        current_app.config["ANNOUNCER"].announce_event(
            EventType.UPDATE,
            {
                "id": download_id,
                "title": title,
                "endTime": end_time,
            },
        )

        return True, None
    except Exception as e:
        err_msg = f"Failed to update download record #{download_id}: {e}"
        logger.error(err_msg)
        return False, err_msg


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

    report: Dict[str, DownloadReportItem] = {}

    # INITIAL RECORDING

    # We store the initial batch to ensure we have a "paper trail"
    initial_queue = []
    for url in list(set(urls)):
        success, download_id, error = start_download_record(url, media_type)
        report[url] = DownloadReportItem(url=url, status=success, error=error)

        if success:
            initial_queue.append((download_id, url))

    # EXPANSION

    final_processing_queue = []
    seen_urls = set()

    if media_type in ["gallery", "unknown"]:
        for parent_id, parent_url in initial_queue:
            seen_urls.add(parent_url)
            expanded_urls = expand_collection_urls(parent_url)

            if not expanded_urls:
                final_processing_queue.append((parent_id, parent_url))
                continue

            report[parent_url].log += f" Expanded into {len(expanded_urls)} items."

            for child_url in expanded_urls:
                if child_url in seen_urls:
                    continue

                child_success, child_id, child_error = start_download_record(
                    child_url, media_type
                )

                # Regardless of success status, we want to keep track of the url,
                # since if it fails and multiple parents expand into lists containing
                # this url, we would keep re-trying to add it to the db. Retries should
                # be a user initiated action.
                seen_urls.add(child_url)

                report[child_url] = DownloadReportItem(
                    url=child_url,
                    status=child_success,
                    error=child_error,
                    log=f"Child of #{parent_id}",
                )

                if child_success:
                    final_processing_queue.append((child_id, child_url))

    else:
        # Non-gallery types will never expand
        final_processing_queue = initial_queue

    # PROCESSING

    # gallery-dl output patterns
    no_results_pattern = r"^\[\w+\]\[info\] No results for"
    larger_than_allowed_pattern = r"^\[\w+\]\[warning\] File size larger"
    catchall_error_pattern = r"^\[\w+\]\[error\]"

    final_processing_count = len(final_processing_queue)
    for i, (download_id, url) in enumerate(final_processing_queue):
        # Scrape title
        title = None

        try:
            headers = {"User-Agent": ScraperConfig.USER_AGENT}
            response = requests.get(url, headers=headers, timeout=ScraperConfig.TIMEOUT)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                if soup.title and soup.title.string:
                    title = soup.title.string.strip()
            else:
                report[url].warnings.append(f"Title scrape HTTP {response.status_code}")

        except Exception as e:
            report[url].warnings.append(f"Title scrape failed: {str(e)}")

        # Download
        try:
            match media_type:
                case "gallery" | "unknown":
                    cmd_result = Gallery.download([url], range_start, range_end)
                    report[url].output = cmd_result.output
                    report[url].status = cmd_result.return_code == 0

                    if not report[url].status:
                        report[url].error = (
                            f"[gallery-dl] Command failed: {cmd_result.return_code}"
                        )
                    else:
                        for line in report[url].output.splitlines():
                            if re.search(no_results_pattern, line):
                                report[url].status = False
                                report[url].error = (
                                    "[gallery-dl] No results found for url."
                                )
                            elif re.search(larger_than_allowed_pattern, line):
                                report[url].status = False
                                report[url].error = (
                                    "[gallery-dl] File size larger than allowed."
                                )
                            elif re.search(catchall_error_pattern, line):
                                report[url].status = False
                                report[url].error = f"[gallery-dl] {line}."

        except Exception as e:
            report[url].status = False
            report[url].error = str(e)

        current_app.config["ANNOUNCER"].announce_event(
            EventType.PROGRESS,
            {"id": download_id, "current": i, "total": final_processing_count},
        )

        # Finalize DB record.
        complete_download_record(download_id, title)  # type: ignore[arg-type]

    final_json_report = {url: item.to_dict() for url, item in report.items()}
    return jsonify(final_json_report), 200

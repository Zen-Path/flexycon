import sqlite3
from datetime import datetime, timezone

from flask import Blueprint, Response, current_app, jsonify, request
from scripts.media_server.src.utils import OperationResult

api_bp = Blueprint("api", __name__)


@api_bp.route("/health", methods=["GET"])
def health_check():
    """
    Standard health check for monitoring tools.
    Returns 200 OK if the server is up.
    """
    return (
        jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": current_app.config.get("APP_VERSION", "unknown"),
            }
        ),
        200,
    )


@api_bp.route("/downloads")
def get_downloads():
    with sqlite3.connect(current_app.config["DB_PATH"]) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM downloads ORDER BY id DESC")

        rows = []
        for row in cursor.fetchall():
            d = dict(row)
            rows.append(
                {
                    "id": d["id"],
                    "url": d["url"],
                    "title": d["title"],
                    "mediaType": d["media_type"],
                    "startTime": d["start_time"],
                    "endTime": d["end_time"],
                }
            )
    return jsonify(rows)


@api_bp.route("/stream")
def stream():
    # Get announcer whilst context is still alive
    announcer = current_app.config["ANNOUNCER"]

    def stream_messages():
        messages = announcer.listen()
        while True:
            msg = messages.get()
            yield msg

    return Response(stream_messages(), mimetype="text/event-stream")


@api_bp.route("/bulkEdit", methods=["PATCH"])
def bulk_edit_entries():
    data = request.get_json(silent=True) or []

    if not isinstance(data, list):
        return (
            jsonify(OperationResult(False, None, "Payload must be a list of objects")),
            400,
        )

    results = []
    with sqlite3.connect(current_app.config["DB_PATH"]) as conn:
        for item in data:
            entry_id = item.get("id")
            if not entry_id:
                results.append(OperationResult(False, None, "Missing 'id' field"))
                continue

            # Dynamic SQL construction
            updates = []
            params = []

            if "title" in item:
                updates.append("title = ?")
                params.append(item["title"])

            if "mediaType" in item:
                media_type = item["mediaType"]
                if media_type and media_type not in ["image", "video", "gallery"]:
                    results.append(
                        OperationResult(
                            False, entry_id, f"Invalid mediaType: {media_type!r}"
                        )
                    )
                    continue

                updates.append("media_type = ?")
                params.append(item["mediaType"])

            if not updates:
                results.append(OperationResult(False, entry_id, "No fields to update"))
                continue

            # Execution
            try:
                cursor = conn.cursor()
                sql = f"UPDATE downloads SET {', '.join(updates)} WHERE id = ?"
                params.append(entry_id)
                cursor.execute(sql, params)

                if cursor.rowcount == 0:
                    results.append(
                        OperationResult(False, entry_id, "ID not found in database")
                    )
                else:
                    conn.commit()
                    results.append(OperationResult(True, entry_id, None))

            except Exception as e:
                conn.rollback()
                results.append(OperationResult(False, entry_id, str(e)))

    master_result = OperationResult(True, results)
    return jsonify(master_result.to_dict()), 200


@api_bp.route("/bulkDelete", methods=["POST"])
def bulk_delete():
    data = request.get_json(silent=True) or {}
    ids = data.get("ids", [])

    if not ids or not isinstance(ids, list):
        return (
            jsonify(
                OperationResult(False, None, "Invalid or empty 'ids' list").to_dict()
            ),
            400,
        )

    unique_ids = list(set(ids))

    results = []
    with sqlite3.connect(current_app.config["DB_PATH"]) as conn:
        for entry_id in unique_ids:
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM downloads WHERE id = ?", (entry_id,))

                if cursor.rowcount > 0:
                    conn.commit()
                    results.append(OperationResult(True, entry_id))
                else:
                    results.append(
                        OperationResult(False, entry_id, "Record ID not found")
                    )

            except Exception as e:
                conn.rollback()
                results.append(OperationResult(False, entry_id, str(e)))

    master_result = OperationResult(True, results)
    return jsonify(master_result.to_dict()), 200

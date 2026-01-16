import sqlite3
from datetime import datetime, timezone

from flask import Blueprint, Response, current_app, jsonify, request

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


@api_bp.route("/entry/<int:entry_id>", methods=["PUT"])
def update_entry(entry_id):
    data = request.json or {}
    new_title = data.get("title")
    new_type = data.get("mediaType")

    with sqlite3.connect(current_app.config["DB_PATH"]) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE downloads SET title = ?, media_type = ? WHERE id = ?",
            (new_title, new_type, entry_id),
        )
        conn.commit()
    return jsonify({"status": "updated"})


@api_bp.route("/entry/<int:entry_id>", methods=["DELETE"])
def delete_entry(entry_id):
    with sqlite3.connect(current_app.config["DB_PATH"]) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM downloads WHERE id = ?", (entry_id,))
        conn.commit()
    return jsonify({"status": "deleted"})


@api_bp.route("/delete_bulk", methods=["POST"])
def delete_bulk():
    data = request.json or {}
    ids = data.get("ids", [])
    if not ids:
        return jsonify({"status": "no_action"})

    # Generate SQL placeholders (?, ?, ?) based on list length
    placeholders = ", ".join(["?"] * len(ids))
    sql = f"DELETE FROM downloads WHERE id IN ({placeholders})"

    with sqlite3.connect(current_app.config["DB_PATH"]) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, ids)
        conn.commit()

    return jsonify({"status": "deleted", "count": len(ids)})

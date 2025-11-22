import sqlite3

from flask import Blueprint, Response, current_app, jsonify, request
from scripts.media_server.src.core import require_api_key

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/history")
@require_api_key
def history():
    with sqlite3.connect(current_app.config["DB_PATH"]) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM downloads ORDER BY id DESC")
        rows = [dict(row) for row in cursor.fetchall()]
    return jsonify(rows)


@api_bp.route("/stream")
@require_api_key
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
@require_api_key
def update_entry(entry_id):
    data = request.json or {}
    new_title = data.get("title")
    new_type = data.get("media_type")

    with sqlite3.connect(current_app.config["DB_PATH"]) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE downloads SET title = ?, media_type = ? WHERE id = ?",
            (new_title, new_type, entry_id),
        )
        conn.commit()
    return jsonify({"status": "updated"})


@api_bp.route("/entry/<int:entry_id>", methods=["DELETE"])
@require_api_key
def delete_entry(entry_id):
    with sqlite3.connect(current_app.config["DB_PATH"]) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM downloads WHERE id = ?", (entry_id,))
        conn.commit()
    return jsonify({"status": "deleted"})


@api_bp.route("/delete_bulk", methods=["POST"])
@require_api_key
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

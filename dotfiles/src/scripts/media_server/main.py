#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
from pathlib import Path

from common.logger import logger, setup_logging
from common.variables import flex_data_path, flex_scripts
from flask import Flask, abort, current_app, redirect, render_template, request
from flask_cors import CORS
from scripts.media_server.routes.api import api_bp
from scripts.media_server.routes.media import media_bp
from scripts.media_server.src.core import MessageAnnouncer, init_db
from scripts.media_server.src.logging_middleware import register_logging

app = Flask(
    __name__,
    template_folder=Path(flex_scripts / "media_server" / "templates"),
    static_folder=Path(flex_scripts / "media_server" / "static"),
)

app.register_blueprint(api_bp, url_prefix="/api")
app.register_blueprint(media_bp, url_prefix="/api/media")


@app.before_request
def check_auth():
    if request.path.startswith("/api/"):
        # Check header OR query string (for SSE)
        provided_key = request.headers.get("X-API-Key") or request.args.get("apiKey")

        expected_key = current_app.config.get("MEDIA_SERVER_KEY")
        if not provided_key or provided_key != expected_key:
            abort(401)


@app.route("/")
def index():
    return redirect("/dashboard")


@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Media server to download files from the web."
    )

    parser.add_argument(
        "--db-path",
        type=Path,
        default=flex_data_path / "media.db",
        help="Path to the database",
    )

    parser.add_argument("--verbose", action="store_true", help="enable debug output")

    return parser


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.WARNING)
    logger.debug(args)

    register_logging(app)

    CORS(app)  # Enable CORS for all routes

    app.config["MEDIA_SERVER_KEY"] = "{{@@ _vars['media_server_key'] @@}}"

    app.config["DB_PATH"] = args.db_path
    init_db(app.config["DB_PATH"])

    announcer = MessageAnnouncer()
    app.config["ANNOUNCER"] = announcer

    app.run(
        port=int("{{@@ _vars['media_server_port'] @@}}"), debug=False, threaded=True
    )


if __name__ == "__main__":
    main()

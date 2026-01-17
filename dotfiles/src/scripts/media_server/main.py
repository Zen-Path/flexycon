#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import os
from pathlib import Path

from common.logger import logger, setup_logging
from common.variables import flex_data_path, flex_scripts
from dotenv import load_dotenv
from flask import Flask, abort, current_app, redirect, render_template, request
from flask_cors import CORS
from scripts.media_server.routes.api import api_bp
from scripts.media_server.routes.media import media_bp
from scripts.media_server.src.logging_middleware import register_logging
from scripts.media_server.src.utils import MessageAnnouncer, init_db

__version__ = "1.1.0"

load_dotenv(flex_scripts / "media_server" / ".env")

app = Flask(
    __name__,
    template_folder=Path(flex_scripts / "media_server" / "templates"),
    static_folder=Path(flex_scripts / "media_server" / "static"),
)

app.register_blueprint(api_bp, url_prefix="/api")
app.register_blueprint(media_bp, url_prefix="/api/media")


@app.before_request
def check_auth():
    if request.path.startswith("/api/") and request.path != "/api/health":
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

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="show the script's version and exit",
    )

    return parser


def main():
    args = build_parser().parse_args()

    setup_logging(logger, logging.DEBUG if args.verbose else logging.WARNING)
    logger.debug(args)

    register_logging(app)

    CORS(app)  # Enable CORS for all routes

    app.config["APP_VERSION"] = __version__

    app.config["MEDIA_SERVER_KEY"] = "{{@@ _vars['media_server_key'] @@}}"

    app.config["DB_PATH"] = args.db_path
    init_db(app.config["DB_PATH"])

    app.config["ANNOUNCER"] = MessageAnnouncer()

    # .env value > xdg value > fallback location
    app.config["DOWNLOAD_DIR"] = Path(
        os.getenv("DOWNLOAD_DIR") or os.getenv("XDG_DOWNLOAD_DIR") or "downloads"
    )

    app.run(
        port=int("{{@@ _vars['media_server_port'] @@}}"), debug=False, threaded=True
    )


if __name__ == "__main__":
    main()

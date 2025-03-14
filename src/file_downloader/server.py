import logging
import os
import subprocess

from flask import Flask, jsonify, request
from flask_cors import CORS


# -----------------------------
# Colored Logging Formatter
# -----------------------------
class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[95m",  # Magenta
        "RESET": "\033[0m",  # Reset color
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]
        log_msg = super().format(record)
        return f"{color}{log_msg}{reset}"


# -----------------------------
# Logger Configuration
# -----------------------------
log_format = "[%(asctime)s] [%(levelname)s] %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter(fmt=log_format, datefmt=date_format))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# -----------------------------
# Flask App Setup
# -----------------------------
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


class Gallery:
    BASE_DIR = os.path.join(
        os.getenv("XDG_DOWNLOAD_DIR", os.path.join("~", "Downloads")), "Galleries"
    )
    FILES_DIR = os.path.join(BASE_DIR, "files")

    def download(urls, range_=None):
        # Check if the directory exists
        if not os.path.exists(Gallery.FILES_DIR):
            os.makedirs(Gallery.FILES_DIR)
            logger.info(f"Directory '{Gallery.FILES_DIR}' created.")

        command = (
            ["gallery-dl", "-o", f"base-directory={Gallery.BASE_DIR}"]
            + urls
            + (["--range", f"{range_[0]}-{range_[1]}"] if range_ else [])
            + [
                "--exec",
                f'if [ -f "{Gallery.FILES_DIR}/{{_path}}" ]; then rm {{_path}}; else mv {{_path}} {Gallery.FILES_DIR}; fi && ln --symbolic {Gallery.FILES_DIR}/{{_filename}} {{_directory}}',
            ]
        )

        logger.info(f"Running: '{' '.join(command)}'")

        output = []

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True,
        )

        # Stream output line-by-line in real-time
        for line in process.stdout:
            output.append(line)
            logger.info(line.strip())

        returncode = process.wait()

        logger.info(f"Command finished with return code {returncode}")

        return returncode, output


@app.route("/download_galleries", methods=["POST"])
def download_galleries():
    data = request.json
    urls = data.get("urls")

    if not urls or not isinstance(urls, list):
        logger.warning("Invalid or missing 'urls' list in request.")
        return jsonify({"error": "Invalid or missing 'urls' list"}), 400

    try:
        returncode, output = Gallery.download(urls)

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


if __name__ == "__main__":
    app.run(port=5000, debug=True)

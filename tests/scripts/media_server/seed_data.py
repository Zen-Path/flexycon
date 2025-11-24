import os
import tempfile
from pathlib import Path

from scenarios import get_default_data
from scripts.media_server.src.core import seed_db


def main():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    print(
        f"Temporary database path: {db_path!r}. \n"
        "Run together with media_server --db-path for custom data."
    )
    seed_db(Path(db_path), get_default_data())


if __name__ == "__main__":
    main()

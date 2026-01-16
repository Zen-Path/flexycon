import os
import sqlite3
import tempfile
import threading
import time
from pathlib import Path

import pytest
from scripts.media_server.main import app
from scripts.media_server.src.core import MessageAnnouncer, init_db, seed_db
from werkzeug.serving import make_server

from .scenarios import get_default_data

# --- CONFIGURATION ---
TEST_PORT = 5002
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"


@pytest.fixture(scope="session")
def db_instance():
    """
    Creates a temporary database file and CONFIGURES the global app.
    This is the 'root' fixture that runs once per test session.
    """
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    announcer = MessageAnnouncer()

    app.config.update(
        {
            "DB_PATH": db_path,
            "MEDIA_SERVER_KEY": "test-secret-key",
            "TESTING": True,
            "ANNOUNCER": announcer,
        }
    )

    with app.app_context():
        init_db(Path(db_path))

    yield Path(db_path)

    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture(scope="session", autouse=True)
def run_server(db_instance):
    """
    Launches the Flask server using Werkzeug's make_server.
    This allows for a clean shutdown, preventing 'Address already in use'.
    """
    server = make_server("127.0.0.1", TEST_PORT, app, threaded=True)

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()

    # Give it a moment to bind
    time.sleep(1)

    yield

    server.shutdown()
    server_thread.join()


@pytest.fixture(autouse=True)
def reset_db_state(db_instance):
    """
    Runs BEFORE every test function.
    Cleans the DB so every test starts with a blank slate.
    """
    with sqlite3.connect(db_instance) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM downloads")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='downloads'")
        conn.commit()
    yield


@pytest.fixture
def seed(db_instance):
    """
    Helper fixture to allow tests to seed data on demand.
    Usage: seed() for defaults, or seed(custom_list).
    """

    def _seed(data=None):
        data_to_use = data if data is not None else get_default_data()
        seed_db(db_instance, data_to_use)

    return _seed


@pytest.fixture
def client(db_instance):
    """
    Flask Test Client for direct API testing.
    """
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_headers():
    return {"X-API-Key": "test-secret-key"}


@pytest.fixture
def dashboard_url():
    return f"{BASE_URL}"

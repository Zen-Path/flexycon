from unittest.mock import MagicMock, patch

from ..conftest import API_BULK_DELETE, API_GET_DOWNLOADS


@patch("scripts.media_server.routes.media.sqlite3.connect")
def test_bulk_delete_variations(mock_connect, create_mock_cursor, client, auth_headers):
    mock_conn = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn

    # No IDs
    res = client.post(API_BULK_DELETE, headers=auth_headers, json={"ids": []})
    assert res.status_code == 400
    data = res.get_json()
    assert not data["status"]
    assert data["error"] == "Invalid or empty 'ids' list"

    # One invalid ID
    mock_conn.cursor.return_value = create_mock_cursor(0)
    res = client.post(API_BULK_DELETE, headers=auth_headers, json={"ids": [999]})
    data = res.get_json()
    assert res.status_code == 200
    assert not data["status"]
    assert data["data"][0]["error"] == "Record ID not found"

    # One valid ID
    mock_conn.cursor.return_value = create_mock_cursor(1)
    res = client.post(API_BULK_DELETE, headers=auth_headers, json={"ids": [1]})
    data = res.get_json()
    assert data["status"]
    assert data["data"][0]["status"]

    # Multiple valid IDs
    mock_conn.cursor.return_value = create_mock_cursor(1)
    res = client.post(API_BULK_DELETE, headers=auth_headers, json={"ids": [1, 2, 3]})
    data = res.get_json()
    assert data["status"]
    assert len(data["data"]) == 3
    assert all(item["status"] for item in data["data"])

    # Mixed IDs status
    cursor_success = create_mock_cursor(1)
    cursor_fail = create_mock_cursor(0)
    mock_conn.cursor.side_effect = [cursor_success, cursor_fail]

    res = client.post(API_BULK_DELETE, headers=auth_headers, json={"ids": [1, 999]})
    data = res.get_json()
    assert data["status"]
    assert data["data"][0]["status"]
    assert not data["data"][1]["status"]

    # Multiple invalid IDs
    mock_conn.cursor.side_effect = None
    mock_conn.cursor.return_value = create_mock_cursor(0)
    res = client.post(API_BULK_DELETE, headers=auth_headers, json={"ids": [888, 999]})
    data = res.get_json()
    assert not data["status"]
    assert all(not item["status"] for item in data["data"])

    # Duplicate IDs
    mock_conn.cursor.return_value = create_mock_cursor(1)
    res = client.post(API_BULK_DELETE, headers=auth_headers, json={"ids": [5, 5]})
    data = res.get_json()
    assert data["status"]
    assert len(data["data"]) == 1
    assert data["data"][0]["status"] is True


def test_database_clearing(client, auth_headers, seed):
    """Test that rows are removed from the database."""
    initial_data = [
        ("http://to-delete.com", "Delete Me", "image", "2025-01-01", "2025-01-01")
    ]
    seed(initial_data)

    history = client.get(API_GET_DOWNLOADS, headers=auth_headers).json
    target_id = history[0]["id"]

    res = client.post(API_BULK_DELETE, headers=auth_headers, json={"ids": [target_id]})
    data = res.get_json()
    assert data["status"]

    history_after = client.get(API_GET_DOWNLOADS, headers=auth_headers).json
    assert len(history_after) == 0


@patch("scripts.media_server.routes.media.sqlite3.connect")
def test_bulk_delete_database_exception(mock_connect, client, auth_headers):
    """Test behavior when the database throws an actual operational error."""
    mock_conn = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.side_effect = Exception("Database Locked")

    res = client.post(API_BULK_DELETE, headers=auth_headers, json={"ids": [1]})
    data = res.get_json()
    assert not data["status"]
    assert "Database Locked" in data["data"][0]["error"]

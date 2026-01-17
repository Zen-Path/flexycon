import json
from unittest.mock import MagicMock, patch

import pytest

from ..conftest import API_BULK_EDIT, API_GET_DOWNLOADS


@patch("scripts.media_server.routes.media.sqlite3.connect")
def test_bulk_edit_variations(mock_connect, create_mock_cursor, client, auth_headers):
    mock_conn = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn

    # Wrong data type
    res = client.patch(
        API_BULK_EDIT, headers=auth_headers, json={"id": 1, "title": "Not a list"}
    )
    assert res.status_code == 400
    data = res.get_json()
    assert not data["status"]
    assert "Payload must be a list" in data["error"]

    # Invalid ID
    res = client.patch(
        API_BULK_EDIT, headers=auth_headers, json=[{"title": "No ID here"}]
    )
    data = res.get_json()
    assert not data["status"]
    assert data["data"][0]["error"] == "Missing 'id' field"

    # Invalid media type
    res = client.patch(
        API_BULK_EDIT, headers=auth_headers, json=[{"id": 1, "mediaType": "pizza"}]
    )
    data = res.get_json()
    assert not data["status"]
    assert "Invalid mediaType" in data["data"][0]["error"]

    # No field passed
    res = client.patch(API_BULK_EDIT, headers=auth_headers, json=[{"id": 1}])
    data = res.get_json()
    assert not data["status"]
    assert data["data"][0]["error"] == "No fields to update"

    # One valid
    mock_conn.cursor.return_value = create_mock_cursor(1)
    res = client.patch(
        API_BULK_EDIT, headers=auth_headers, json=[{"id": 1, "title": "Updated"}]
    )
    data = res.get_json()
    assert data["status"]
    assert data["data"][0]["status"]

    # Multiple valid
    mock_conn.cursor.return_value = create_mock_cursor(1)
    payload = [
        {"id": 1, "title": "One"},
        {"id": 2, "mediaType": "video"},
        {"id": 3, "title": "Three", "mediaType": "gallery"},
    ]
    res = client.patch(API_BULK_EDIT, headers=auth_headers, json=payload)
    data = res.get_json()
    assert data["status"]
    assert len(data["data"]) == 3
    assert all(item["status"] for item in data["data"])

    # Mixed status
    cursor_success = create_mock_cursor(1)
    cursor_not_found = create_mock_cursor(0)
    mock_conn.cursor.side_effect = [cursor_success, cursor_success, cursor_not_found]

    payload = [
        {"id": 1, "title": "Ok"},
        {"id": 2, "title": "Ok Too"},
        {"id": 99, "title": "I don't exist"},
    ]
    res = client.patch(API_BULK_EDIT, headers=auth_headers, json=payload)
    data = res.get_json()

    assert data["status"]
    assert data["data"][0]["status"]
    assert data["data"][1]["status"]

    assert not data["data"][2]["status"]
    assert "ID not found" in data["data"][2]["error"]


@pytest.mark.parametrize(
    "payload,new_title,new_media_type",
    [
        ({"title": "New Title", "mediaType": "gallery"}, "New Title", "gallery"),
        # Partial updating
        ({"title": "New Title"}, "New Title", "image"),
        ({"mediaType": "video"}, "Edit Me", "video"),
        # Resetting
        ({"title": None, "mediaType": None}, None, None),
        ({"title": None}, None, "image"),
        ({"mediaType": None}, "Edit Me", None),
    ],
)
def test_bulk_edit_persistence(
    payload, new_title, new_media_type, client, auth_headers, seed
):
    """Test that rows are updated in the database."""
    initial_data = [
        ("http://to-edit.com", "Edit Me", "image", "2025-01-01", "2025-01-01")
    ]
    seed(initial_data)

    history = client.get(API_GET_DOWNLOADS, headers=auth_headers).json
    target_id = history[0]["id"]

    res = client.patch(
        API_BULK_EDIT, headers=auth_headers, json=[{"id": target_id, **payload}]
    )
    data = res.get_json()
    assert data["status"]
    assert data["data"][0]["status"]

    history_after = client.get(API_GET_DOWNLOADS, headers=auth_headers).json
    assert len(history_after) == 1
    assert history_after[0]["title"] == new_title
    assert history_after[0]["mediaType"] == new_media_type

    # Other data shouldn't be affected
    assert history_after[0]["startTime"] == "2025-01-01"

from unittest.mock import patch


def test_unauthorized_access(client):
    """Verify that API endpoints reject requests without a key."""
    response = client.get("/api/history")

    assert response.status_code == 401


def test_authorized_access(client, auth_headers, seed):
    """Verify that valid keys allow access."""
    # Explicitly seed data so we have something to fetch
    seed()

    response = client.get("/api/history", headers=auth_headers)
    assert response.status_code == 200

    data = response.json
    assert len(data) > 0
    assert data[0]["url"] is not None


def test_edit_entry(client, auth_headers, seed):
    """Test updating an existing entry's title and media type."""
    initial_data = [
        ("http://to-edit.com", "Original Title", "image", "2025-01-01", "2025-01-01")
    ]
    seed(initial_data)

    # Get the ID of the item we just seeded
    history_before = client.get("/api/history", headers=auth_headers).json
    target_id = history_before[0]["id"]

    # Send PUT request to update
    payload = {"title": "Updated Title", "media_type": "video"}
    response = client.put(f"/api/entry/{target_id}", headers=auth_headers, json=payload)

    assert response.status_code == 200
    assert response.json["status"] == "updated"

    # Verify changes in DB
    history_after = client.get("/api/history", headers=auth_headers).json
    updated_item = history_after[0]

    assert updated_item["title"] == "Updated Title"
    assert updated_item["media_type"] == "video"


def test_delete_single_entry(client, auth_headers, seed):
    """Test deleting a specific entry by ID."""
    initial_data = [
        ("http://delete-single.com", "Delete Me", "image", "2025-01-01", "2025-01-01")
    ]
    seed(initial_data)

    # Get the ID
    history = client.get("/api/history", headers=auth_headers).json
    target_id = history[0]["id"]

    # Send DELETE request
    response = client.delete(f"/api/entry/{target_id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json["status"] == "deleted"

    # Verify it's gone from DB
    history_after = client.get("/api/history", headers=auth_headers).json
    assert len(history_after) == 0


def test_delete_bulk(client, auth_headers, seed):
    """Test deleting items."""
    initial_data = [
        ("http://to-delete.com", "Delete Me", "image", "2025-01-01", "2025-01-01")
    ]
    seed(initial_data)

    # Get ID of the item we just seeded
    history = client.get("/api/history", headers=auth_headers).json
    target_id = history[0]["id"]

    # Delete it via API
    res = client.post(
        "/api/delete_bulk", headers=auth_headers, json={"ids": [target_id]}
    )
    assert res.status_code == 200

    # Verify it is gone
    history_after = client.get("/api/history", headers=auth_headers).json
    assert len(history_after) == 0


def test_download(client, auth_headers):
    """Test the download endpoint with mocked external requests."""
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<html><title>Mocked Title</title></html>"

        payload = {"urls": ["http://mock-site.com"], "media_type": "video"}
        response = client.post("/media/download", headers=auth_headers, json=payload)

        assert response.status_code == 200
        assert response.json["count"] == 1

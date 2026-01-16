from .conftest import API_GET_DOWNLOADS, API_HEALTH


def test_health_check(client):
    response = client.get(API_HEALTH)
    assert response.status_code == 200

    data = response.json
    assert data["status"] == "healthy"


def test_auth(client, auth_headers, seed):
    """Verify that API endpoints require a key."""
    no_key_response = client.get(API_GET_DOWNLOADS)
    assert no_key_response.status_code == 401

    invalid_key_response = client.get(
        API_GET_DOWNLOADS, headers={"X-API-Key": "abc123"}
    )
    assert invalid_key_response.status_code == 401

    valid_key_response = client.get(API_GET_DOWNLOADS, headers=auth_headers)
    assert valid_key_response.status_code == 200


def test_edit_entry(client, auth_headers, seed):
    """Test updating an existing entry's title and media type."""
    initial_data = [
        ("http://to-edit.com", "Original Title", "image", "2025-01-01", "2025-01-01")
    ]
    seed(initial_data)

    # Get the ID of the item we just seeded
    history_before = client.get(API_GET_DOWNLOADS, headers=auth_headers).json
    target_id = history_before[0]["id"]

    # Send PUT request to update
    payload = {"title": "Updated Title", "mediaType": "video"}
    response = client.put(f"/api/entry/{target_id}", headers=auth_headers, json=payload)

    assert response.status_code == 200
    assert response.json["status"] == "updated"

    # Verify changes in DB
    history_after = client.get(API_GET_DOWNLOADS, headers=auth_headers).json
    updated_item = history_after[0]

    assert updated_item["title"] == "Updated Title"
    assert updated_item["mediaType"] == "video"


def test_delete_single_entry(client, auth_headers, seed):
    """Test deleting a specific entry by ID."""
    initial_data = [
        ("http://delete-single.com", "Delete Me", "image", "2025-01-01", "2025-01-01")
    ]
    seed(initial_data)

    # Get the ID
    history = client.get(API_GET_DOWNLOADS, headers=auth_headers).json
    target_id = history[0]["id"]

    # Send DELETE request
    response = client.delete(f"/api/entry/{target_id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json["status"] == "deleted"

    # Verify it's gone from DB
    history_after = client.get(API_GET_DOWNLOADS, headers=auth_headers).json
    assert len(history_after) == 0


def test_delete_bulk(client, auth_headers, seed):
    """Test deleting items."""
    initial_data = [
        ("http://to-delete.com", "Delete Me", "image", "2025-01-01", "2025-01-01")
    ]
    seed(initial_data)

    # Get ID of the item we just seeded
    history = client.get(API_GET_DOWNLOADS, headers=auth_headers).json
    target_id = history[0]["id"]

    # Delete it via API
    res = client.post(
        "/api/delete_bulk", headers=auth_headers, json={"ids": [target_id]}
    )
    assert res.status_code == 200

    # Verify it is gone
    history_after = client.get(API_GET_DOWNLOADS, headers=auth_headers).json
    assert len(history_after) == 0

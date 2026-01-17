from ..conftest import API_BULK_EDIT, API_GET_DOWNLOADS, API_HEALTH


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


def test_bulk_edit(client, auth_headers, seed):
    """Test editing of existing entries."""
    initial_data = [
        ("http://to-edit.com", "Original Title", "image", "2025-01-01", "2025-01-01")
    ]
    seed(initial_data)

    history_before = client.get(API_GET_DOWNLOADS, headers=auth_headers).json
    target_id = history_before[0]["id"]

    payload = [{"id": target_id, "title": "Updated Title", "mediaType": "video"}]
    response = client.patch(API_BULK_EDIT, headers=auth_headers, json=payload)

    assert response.status_code == 200
    assert response.json["status"] == "success"

    assert len(response.json["results"]) == 1
    assert response.json["results"][0]["status"] == True
    assert response.json["results"][0]["error"] == None

    # Verify changes in DB
    history_after = client.get(API_GET_DOWNLOADS, headers=auth_headers).json
    updated_item = history_after[0]

    assert updated_item["title"] == "Updated Title"
    assert updated_item["mediaType"] == "video"

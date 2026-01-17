from ..conftest import API_GET_DOWNLOADS, API_HEALTH


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

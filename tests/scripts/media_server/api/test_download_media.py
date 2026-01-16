from unittest.mock import MagicMock, patch

from scripts.media_server.routes.media import expand_collection_urls

from ..conftest import API_DOWNLOAD


class MockCmdResult:
    def __init__(self, return_code=0, output="Success"):
        self.return_code = return_code
        self.output = output
        self.success = return_code == 0


def test_download_media_invalid_input(client, auth_headers):
    """Verify that bad payloads return 400."""
    # Test missing URLs
    res = client.post(API_DOWNLOAD, headers=auth_headers, json={"mediaType": "image"})
    assert res.status_code == 400

    # Test bad range
    res = client.post(
        API_DOWNLOAD,
        headers=auth_headers,
        json={
            "urls": ["http://test.com"],
            "mediaType": "gallery",
            "rangeStart": "not-an-int",
        },
    )
    assert res.status_code == 400


@patch("scripts.media_server.routes.media.start_download_record")
def test_initial_recording_deduplication(mock_start, client, auth_headers):
    """Verify that the initial recording phase uses list(set(urls))."""
    mock_start.return_value = (True, 1, None)
    urls = ["http://dup.com", "http://dup.com", "http://unique.com"]

    client.post(
        API_DOWNLOAD, headers=auth_headers, json={"urls": urls, "mediaType": "image"}
    )

    # Should only be called twice because of the set()
    assert mock_start.call_count == 2


@patch("scripts.media_server.routes.media.expand_collection_urls")
@patch("scripts.media_server.routes.media.Gallery.download")
@patch("requests.get")
def test_gallery_expansion_flow(
    mock_get, mock_gallery, mock_expand, client, auth_headers
):
    """Verify Phase 2 correctly expands one URL into multiple child records."""
    parent_url = "http://gallery.com/main"
    child_urls = ["http://gallery.com/1", "http://gallery.com/2"]

    mock_expand.return_value = child_urls
    mock_gallery.return_value = MockCmdResult(0)

    # Mock title scrape response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><title>Test Page</title></html>"
    mock_get.return_value = mock_response

    payload = {"urls": [parent_url], "mediaType": "gallery"}
    res = client.post(API_DOWNLOAD, headers=auth_headers, json=payload)

    data = res.get_json()

    # Check parent entry
    assert parent_url in data
    assert "Expanded into 2 items" in data[parent_url]["log"]

    # Check child entries exist in the report
    assert child_urls[0] in data
    assert data[child_urls[0]]["log"] == "Child of #1"


@patch("requests.get")
@patch("scripts.media_server.routes.media.Gallery.download")
def test_title_scrape_failure_handling(mock_gallery, mock_get, client, auth_headers):
    """Verify that a failed title scrape adds a warning but doesn't fail the download."""
    mock_get.side_effect = Exception("Connection Timeout")
    mock_gallery.return_value = MockCmdResult(0)

    url = "http://slow-site.com/img.jpg"
    res = client.post(
        API_DOWNLOAD, headers=auth_headers, json={"urls": [url], "mediaType": "image"}
    )

    data = res.get_json()
    assert data[url]["status"] is True
    assert any("Title scrape failed" in w for w in data[url]["warnings"])


@patch("scripts.media_server.routes.media.Gallery.download")
def test_gallery_dl_failure_reporting(mock_gallery, client, auth_headers):
    """Verify that a non-zero return code from gallery-dl marks status as False."""
    mock_gallery.return_value = MockCmdResult(return_code=1, output="403 Forbidden")

    url = "http://blocked.com/gallery"
    res = client.post(
        API_DOWNLOAD, headers=auth_headers, json={"urls": [url], "mediaType": "gallery"}
    )

    data = res.get_json()
    assert data[url]["status"] is False
    assert data[url]["output"] == "403 Forbidden"
    assert data[url]["error"] == "Gallery-dl command failed"


# Helpers


def test_expand_collection_urls_depth_limit():
    """Ensure recursion stops at depth 3."""
    with patch("scripts.media_server.routes.media.run_command") as mock_run:
        # If it didn't stop, it would call run_command indefinitely

        result = expand_collection_urls("http://test.com", depth=4)
        assert result == []
        assert mock_run.call_count == 0

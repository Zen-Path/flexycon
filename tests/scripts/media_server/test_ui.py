import json
import re
from datetime import datetime
from urllib.parse import urljoin

import pytest
import requests
from playwright.sync_api import Dialog, Page, expect
from scripts.media_server.src.constants import MediaType

from .conftest import API_DOWNLOAD, BASE_URL, DASHBOARD_URL

pytestmark = [pytest.mark.ui]


def test_dashboard_visuals(page: Page, seed):
    """Check that the dashboard renders seeded data correctly."""
    seed()

    page.goto(DASHBOARD_URL)

    expect(page).to_have_title("Downloads | Media Server")

    # Check that we have rows
    rows = page.locator(".data-row")
    expect(rows).not_to_have_count(0)

    # Check each column
    first_row = page.locator(".data-row").first
    expect(first_row).to_be_visible(timeout=100)

    expect(first_row.locator(".col-checkbox input[type='checkbox']")).to_be_visible(
        timeout=100
    )

    # ID: Matches # followed by digits (e.g., #123)
    expect(first_row.locator(".col-id")).to_have_text(
        re.compile(r"^#\d+$"), timeout=100
    )

    expect(first_row.locator(".col-media-type.type-video")).to_be_visible(timeout=100)

    # Title
    expect(first_row.locator(".col-name a")).to_have_attribute(
        "href", re.compile(r"^https?://"), timeout=100
    )
    expect(first_row.locator(".col-name .title")).to_contain_text(
        "Channel Intro", timeout=100
    )

    # Time
    time_text = first_row.locator(".col-start-time").inner_text(timeout=100)
    _ = datetime.strptime(time_text, "%Y-%m-%d %H:%M:%S")

    # Actions
    expect(first_row.locator(".col-actions .action-btn")).to_be_visible(timeout=100)

    # Theme toggle
    expect(page.locator("#themeToggle")).to_be_visible(timeout=100)


def test_search(page: Page, seed):
    """Test the Javascript search filter."""
    seed()

    page.goto(DASHBOARD_URL)

    page.fill("#searchInput", "Cat Memes")
    page.pause()
    expect(page.locator(".data-table-body")).to_contain_text("Best Cat Memes")
    expect(page.locator(".data-table-body")).not_to_contain_text("Rick Astley")

    # Clear search
    page.click("#clearBtn")
    expect(page.locator(".data-table-body")).to_contain_text("Rick Astley")


def test_sorting_by_url(page: Page, seed):
    """
    Test 2: Sorting
    - Title column should sort by URL, not Title.
    - Verify Sort Indicators.
    """
    initial_data = [
        {
            "url": "http://a_start.com",
            "title": "Zebra Title",
            "start_time": datetime.now(),
        },
        {
            "url": "http://z_end.com",
            "title": "Apple Title",
            "start_time": datetime.now(),
        },
    ]
    seed(initial_data)

    page.goto(DASHBOARD_URL)

    name_column_class = ".header-cell .col-name"
    sort_indicator_class = ".header-cell .col-name .sort-indicator"

    # Click 'Title' header -> Sort ASC
    page.click(name_column_class)

    # Verify Indicator
    expect(page.locator(sort_indicator_class)).to_have_class("fa-caret-up")

    # Verify Order (Using expect to wait for re-render)
    expect(page.locator(".data-row").first).to_contain_text("Apple Title", timeout=100)

    # Click again -> Sort DESC
    page.click(name_column_class)
    expect(page.locator(sort_indicator_class)).to_have_class("fa-caret-down")

    expect(page.locator(".data-row").first).to_contain_text("Zebra Title")


def test_search_and_sort(page: Page, seed):
    """
    Test 3: Search + Sort
    """
    initial_data = [
        {
            "url": "http://python-1.com",
            "title": "Python Tutorial A",
            "start_time": datetime.now(),
        },
        {
            "url": "http://python-2.com",
            "title": "Python Tutorial Z",
            "start_time": datetime.now(),
        },
        {
            "url": "http://java-1.com",
            "title": "Java Tutorial",
            "start_time": datetime.now(),
        },
    ]
    seed(initial_data)

    page.goto(DASHBOARD_URL)

    # Search
    page.fill("#searchInput", "Python")
    rows = page.locator(".data-row")
    expect(rows).to_have_count(2)

    name_column_class = ".header-cell .col-name"

    # Sort ASC
    page.click(name_column_class)
    expect(rows.nth(0)).to_contain_text("Tutorial A")

    # Sort DESC
    page.click(name_column_class)
    expect(rows.nth(0)).to_contain_text("Tutorial Z")

    # Ensure Java hidden
    expect(page.locator(".data-table-body")).not_to_contain_text("Java Tutorial")


def test_edit_feature_ui(page: Page, seed, sample_download_row):
    """
    Test Edit Flow:
    1. Click Edit button on a row.
    2. Change Title and Media Type in Modal.
    3. Save.
    4. Verify Table updates immediately.
    """
    seed([sample_download_row])

    page.goto(DASHBOARD_URL)

    page.click(".cell .action-btn")
    page.click(".dropdown-content .menu-item")

    # Verify Modal is visible
    expect(page.locator("#editModal")).to_be_visible()

    # Check that input was pre-filled correctly
    expect(page.locator("#editTitle")).to_have_value(sample_download_row["title"])

    # Type new values
    page.fill("#editTitle", "New UI Title")
    page.select_option("#editMediaType", str(MediaType.GALLERY))

    # Save
    page.click("button:has-text('Save Changes')")

    # Modal should close
    expect(page.locator("#editModal")).not_to_be_visible()

    # Text should update in the table
    expect(page.locator("body")).to_contain_text("New UI Title")
    expect(page.locator("body")).not_to_contain_text(sample_download_row["title"])

    # Icon should update
    expect(page.locator(".type-gallery")).to_be_visible()


def test_delete_single_ui(page: Page, seed, sample_download_row):
    """
    Test Delete Flow:
    1. Click Delete button.
    2. Handle browser 'Confirm' dialog.
    3. Verify row disappears.
    """
    seed([sample_download_row])

    page.goto(DASHBOARD_URL)

    # Verify row exists
    expect(page.locator(".data-row")).to_have_count(1)

    # Setup Dialog Handler (IMPORTANT)
    # By default, Playwright dismisses dialogs. We must tell it to 'accept' (Click OK).
    page.on("dialog", lambda dialog: dialog.accept())

    page.click(".cell .action-btn")
    page.click(".dropdown-content .fa-pen")

    # Verify Row is Gone
    # The API call is async, so expect().to_have_count(0) waits automatically until
    # it happens
    expect(page.locator(".data-row")).to_have_count(0)
    expect(page.locator("body")).not_to_contain_text(sample_download_row["title"])


def test_delete_all_visible_no_search(page: Page, seed):
    """
    Test Delete Visible (No Filter):
    1. Seed 3 items.
    2. Click 'Delete Visible'.
    3. Accept Confirmation.
    4. Verify Table is completely empty.
    """
    initial_data = [
        {"url": "http://1.com", "title": "Item One", "start_time": datetime.now()},
        {"url": "http://2.com", "title": "Item Two", "start_time": datetime.now()},
        {"url": "http://3.com", "title": "Item Three", "start_time": datetime.now()},
    ]
    seed(initial_data)

    page.goto(DASHBOARD_URL)
    expect(page.locator(".data-row")).to_have_count(3)

    # Setup Dialog Handler (Click OK on alert)
    page.on("dialog", lambda dialog: dialog.accept())

    # Click Delete Visible
    page.click("button:has-text('Delete Selected')")

    # Verify Empty Table
    expect(page.locator(".data-row")).to_have_count(0)
    expect(page.locator("body")).not_to_contain_text("Item One")


def test_bulk_delete_failure_alert(page: Page, seed):
    """
    Test Alert Message on Failure:
    1. Seed 1 item.
    2. Intercept the network to return a 'failed' status for that ID.
    3. Verify the alert message shows the correct failure count.
    """
    initial_data = [
        {
            "url": "http://fail.com",
            "title": "Faulty Item",
            "start_time": datetime.now(),
        },
        {
            "url": "http://success.com",
            "title": "Valid Item",
            "start_time": datetime.now(),
        },
    ]
    seed(initial_data)

    page.goto(DASHBOARD_URL)

    # Capture the dialog message
    dialog_messages = []

    def handle_dialog(dialog: Dialog) -> None:
        """Explicit handler to satisfy mypy."""
        dialog_messages.append(dialog.message)
        dialog.accept()

    page.on("dialog", handle_dialog)

    # Intercept the Delete API call
    # We simulate a "failed" response where status is 'failed'
    # and results show the ID was not found.
    page.route(
        "**/api/bulkDelete",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(
                {
                    "status": True,
                    "error": None,
                    "data": [
                        {
                            "status": False,
                            "error": "Record ID not found",
                            "data": 1,  # Simulating the ID that failed
                        },
                        {"status": True, "error": None, "data": 2},
                    ],
                }
            ),
        ),
    )

    page.click("button:has-text('Delete Selected')")

    # Since JS alerts are blocking, Playwright needs a moment
    # to catch the second event.
    page.wait_for_timeout(100)

    assert "Delete all 2" in dialog_messages[0]
    assert "Could not delete 1 items" in dialog_messages[1]

    # Verify that only the entry that failed to download is still in the table
    expect(page.locator(".data-row")).to_have_count(1)
    expect(page.locator("body")).to_contain_text("Faulty Item")


def test_delete_visible_with_search(page: Page, seed):
    """
    Test Delete Visible (With Filter):
    1. Seed mixed items ("Keep Me" vs "Delete Me").
    2. Search for "Delete".
    3. Click 'Delete Visible'.
    4. Verify "Delete Me" items are gone.
    5. Clear search.
    6. Verify "Keep Me" items are STILL there.
    """
    initial_data = [
        {
            "url": "http://keep.com",
            "title": "Keep Me Safe",
            "start_time": datetime.now(),
        },
        {
            "url": "http://del-1.com",
            "title": "Delete Me Please",
            "start_time": datetime.now(),
        },
        {
            "url": "http://del-2.com",
            "title": "Delete Me Also",
            "start_time": datetime.now(),
        },
    ]
    seed(initial_data)

    page.goto(DASHBOARD_URL)

    # Search for "Delete" (Should show 2 rows)
    page.fill("#searchInput", "Delete")
    expect(page.locator(".data-row")).to_have_count(2)

    # Handle Dialog & Click Delete
    page.on("dialog", lambda dialog: dialog.accept())
    page.click("button:has-text('Delete Selected')")

    # Verify current view is empty (because all matching items were deleted)
    expect(page.locator(".data-row")).to_have_count(0)

    # Clear Search to reveal remaining items
    page.click("#clearBtn")

    # Verify "Keep Me" is still there, but "Delete" items are gone
    expect(page.locator(".data-row")).to_have_count(1)
    expect(page.locator("body")).to_contain_text("Keep Me Safe")
    expect(page.locator("body")).not_to_contain_text("Delete Me")


def test_realtime_updates(page: Page, auth_headers, seed, sample_download_row):
    """
    1. Seed some initial data.
    2. Load Dashboard.
    3. Trigger API in background (simulating backend process).
    4. Verify SSE update.
    """
    initial_data = [sample_download_row]
    seed(initial_data)

    page.goto(DASHBOARD_URL)
    initial_rows_count = page.locator(".data-row").count()
    assert initial_rows_count == len(initial_data)

    new_item_count = 5
    for i in range(new_item_count):
        payload = {
            "urls": [urljoin("https://example.com", str(i))],
            "mediaType": None,
        }
        requests.post(
            urljoin(BASE_URL, API_DOWNLOAD), json=payload, headers=auth_headers
        )

    all_titles = page.locator("#table-container .title").all_inner_texts()
    assert len(all_titles) == initial_rows_count + new_item_count
    assert sample_download_row["title"] in all_titles
    assert "No Title Found" in all_titles

    all_urls = page.locator("#table-container .url-subtext").all_inner_texts()
    assert len(all_urls) == len(all_titles)
    assert sample_download_row["url"] in all_urls
    assert "https://example.com/1" in all_urls

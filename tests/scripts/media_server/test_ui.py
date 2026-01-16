import re
from datetime import datetime

import pytest
import requests
from playwright.sync_api import Page, expect

from .conftest import API_DOWNLOAD

pytestmark = [pytest.mark.ui]


def test_dashboard_visuals(page: Page, dashboard_url, seed):
    """Check that the dashboard renders seeded data correctly."""
    seed()

    page.goto(dashboard_url)

    expect(page).to_have_title("Live Dashboard")

    # Check that we have rows
    rows = page.locator("#table-body tr")
    expect(rows).not_to_have_count(0)

    # Check each column
    first_row = page.locator("#table-body tr").first
    expect(first_row).to_be_visible()

    expect(first_row.locator(".col-check input[type='checkbox']")).to_be_visible(
        timeout=0
    )

    # ID: Matches # followed by digits (e.g., #123)
    expect(first_row.locator(".col-id")).to_have_text(re.compile(r"^#\d+$"), timeout=0)

    expect(first_row.locator(".col-type .type-video")).to_be_visible(timeout=0)

    # Title
    expect(first_row.locator(".col-title a")).to_have_attribute(
        "href", re.compile(r"^https?://"), timeout=0
    )
    expect(first_row.locator(".col-title .title-text")).to_contain_text("Channel Intro")

    # Time
    time_text = first_row.locator(".col-time").inner_text()
    parsed_date = datetime.strptime(time_text, "%Y-%m-%d %H:%M:%S")

    # Actions
    expect(first_row.locator(".col-actions .btn-edit")).to_be_visible(timeout=0)
    expect(first_row.locator(".col-actions .btn-delete")).to_be_visible(timeout=0)


def test_search(page: Page, dashboard_url, seed):
    """Test the Javascript search filter."""
    seed()

    page.goto(dashboard_url)

    page.fill("#searchInput", "Cat Memes")
    expect(page.locator("body")).to_contain_text("Best Cat Memes")
    expect(page.locator("body")).not_to_contain_text("Rick Astley")

    # Clear search
    page.click("#clearBtn")
    expect(page.locator("body")).to_contain_text("Rick Astley")


def test_sorting_by_url(page: Page, dashboard_url, seed):
    """
    Test 2: Sorting
    - Title column should sort by URL, not Title.
    - Verify Sort Indicators.
    """
    initial_data = [
        ("http://a_start.com", "Zebra Title", "image", "2025-01-01", "2025-01-01"),
        ("http://z_end.com", "Apple Title", "image", "2025-01-01", "2025-01-01"),
    ]
    seed(initial_data)

    page.goto(dashboard_url)

    # Click 'Title' header -> Sort ASC
    page.click("#th-title")

    # Verify Indicator
    expect(page.locator("#th-title")).to_have_class(re.compile(r"active.*asc"))

    # Verify Order (Using expect to wait for re-render)
    expect(page.locator("#table-body tr").first).to_contain_text("Apple Title")

    # Click again -> Sort DESC
    page.click("#th-title")
    expect(page.locator("#th-title")).to_have_class(re.compile(r"active.*desc"))

    expect(page.locator("#table-body tr").first).to_contain_text("Zebra Title")


def test_search_and_sort(page: Page, dashboard_url, seed):
    """
    Test 3: Search + Sort
    """
    initial_data = [
        (
            "http://python-1.com",
            "Python Tutorial A",
            "video",
            "2025-01-01",
            "2025-01-01",
        ),
        (
            "http://python-2.com",
            "Python Tutorial Z",
            "video",
            "2025-01-02",
            "2025-01-02",
        ),
        ("http://java-1.com", "Java Tutorial", "video", "2025-01-03", "2025-01-03"),
    ]
    seed(initial_data)

    page.goto(dashboard_url)

    # Search
    page.fill("#searchInput", "Python")
    rows = page.locator("#table-body tr")
    expect(rows).to_have_count(2)

    # Sort ASC
    page.click("#th-title")
    expect(rows.nth(0)).to_contain_text("Tutorial A")

    # Sort DESC
    page.click("#th-title")
    expect(rows.nth(0)).to_contain_text("Tutorial Z")

    # Ensure Java hidden
    expect(page.locator("body")).not_to_contain_text("Java Tutorial")


def test_edit_feature_ui(page: Page, dashboard_url, seed):
    """
    Test Edit Flow:
    1. Click Edit button on a row.
    2. Change Title and Media Type in Modal.
    3. Save.
    4. Verify Table updates immediately.
    """
    initial_data = [
        ("http://ui-edit.com", "Old UI Title", "image", "2025-01-01", "2025-01-01")
    ]
    seed(initial_data)

    page.goto(dashboard_url)

    page.click(".btn-edit")

    # Verify Modal is visible
    expect(page.locator("#editModal")).to_be_visible()

    # Check that input was pre-filled correctly
    expect(page.locator("#editTitle")).to_have_value("Old UI Title")

    # Type new values
    page.fill("#editTitle", "New UI Title")
    page.select_option("#editMediaType", "gallery")

    # Save
    page.click("button:has-text('Save')")

    # Modal should close
    expect(page.locator("#editModal")).not_to_be_visible()

    # Text should update in the table
    expect(page.locator("body")).to_contain_text("New UI Title")
    expect(page.locator("body")).not_to_contain_text("Old UI Title")

    # Icon should update
    expect(page.locator(".type-gallery")).to_be_visible()


def test_delete_single_ui(page: Page, dashboard_url, seed):
    """
    Test Delete Flow:
    1. Click Delete button.
    2. Handle browser 'Confirm' dialog.
    3. Verify row disappears.
    """
    initial_data = [
        ("http://ui-delete.com", "To Be Deleted", "image", "2025-01-01", "2025-01-01")
    ]
    seed(initial_data)

    page.goto(dashboard_url)

    # Verify row exists
    expect(page.locator("#table-body tr")).to_have_count(1)

    # Setup Dialog Handler (IMPORTANT)
    # By default, Playwright dismisses dialogs. We must tell it to 'accept' (Click OK).
    page.on("dialog", lambda dialog: dialog.accept())

    # Click Delete
    page.click(".btn-delete")

    # Verify Row is Gone
    # The API call is async, so expect().to_have_count(0) waits automatically until it happens
    expect(page.locator("#table-body tr")).to_have_count(0)
    expect(page.locator("body")).not_to_contain_text("To Be Deleted")


def test_delete_all_visible_no_search(page: Page, dashboard_url, seed):
    """
    Test Delete Visible (No Filter):
    1. Seed 3 items.
    2. Click 'Delete Visible'.
    3. Accept Confirmation.
    4. Verify Table is completely empty.
    """
    initial_data = [
        ("http://1.com", "Item One", "image", "2025-01-01", "2025-01-01"),
        ("http://2.com", "Item Two", "video", "2025-01-01", "2025-01-01"),
        ("http://3.com", "Item Three", "gallery", "2025-01-01", "2025-01-01"),
    ]
    seed(initial_data)

    page.goto(dashboard_url)
    expect(page.locator("#table-body tr")).to_have_count(3)

    # Setup Dialog Handler (Click OK on alert)
    page.on("dialog", lambda dialog: dialog.accept())

    # Click Delete Visible
    page.click("button:has-text('Delete Selected')")

    # Verify Empty Table
    expect(page.locator("#table-body tr")).to_have_count(0)
    expect(page.locator("body")).not_to_contain_text("Item One")


def test_delete_visible_with_search(page: Page, dashboard_url, seed):
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
        ("http://keep.com", "Keep Me Safe", "image", "2025-01-01", "2025-01-01"),
        ("http://del-1.com", "Delete Me Please", "video", "2025-01-01", "2025-01-01"),
        ("http://del-2.com", "Delete Me Also", "video", "2025-01-01", "2025-01-01"),
    ]
    seed(initial_data)

    page.goto(dashboard_url)

    # Search for "Delete" (Should show 2 rows)
    page.fill("#searchInput", "Delete")
    expect(page.locator("#table-body tr")).to_have_count(2)

    # Handle Dialog & Click Delete
    page.on("dialog", lambda dialog: dialog.accept())
    page.click("button:has-text('Delete Selected')")

    # Verify current view is empty (because all matching items were deleted)
    expect(page.locator("#table-body tr")).to_have_count(0)

    # Clear Search to reveal remaining items
    page.click("#clearBtn")

    # Verify "Keep Me" is still there, but "Delete" items are gone
    expect(page.locator("#table-body tr")).to_have_count(1)
    expect(page.locator("body")).to_contain_text("Keep Me Safe")
    expect(page.locator("body")).not_to_contain_text("Delete Me")


def test_realtime_updates(page: Page, auth_headers, dashboard_url, seed):
    """
    1. Seed some initial data.
    2. Load Dashboard.
    3. Trigger API in background (simulating backend process).
    4. Verify SSE update.
    """
    initial_data = [
        (
            "http://initial.com",
            "Initial Item",
            "image",
            "2025-01-01 10:00:00",
            "2025-01-01 10:05:00",
        )
    ]
    seed(initial_data)

    page.goto(dashboard_url)
    initial_rows_count = page.locator("#table-body tr").count()
    assert initial_rows_count == 1

    # Trigger Download via API
    new_item_count = 5
    for _ in range(new_item_count):
        payload = {"urls": ["https://example.com/"], "mediaType": "unknown"}
        requests.post(
            f"{dashboard_url}{API_DOWNLOAD}", json=payload, headers=auth_headers
        )

    # Verify Dashboard Updates
    expect(page.locator("#table-body tr")).to_have_count(
        initial_rows_count + new_item_count
    )
    expect(page.locator("body")).to_contain_text("https://example.com/")

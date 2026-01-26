import pytest
from playwright.sync_api import expect


@pytest.fixture
def search_items(mock_downloads):
    data = [
        {"id": 1, "title": "Alpha Video", "url": "https://a.com"},
        {"id": 2, "title": "Beta Movie", "url": "https://b.com"},
        {"id": 3, "title": "Gamma Clip", "url": "https://c.com"},
    ]
    mock_downloads(data)
    return data


def test_search_filtering_visibility(dashboard, search_items):
    """Verify rows hide/show as the user types sequentially."""
    dashboard.navigate()

    # Initially all visible
    expect(dashboard.rows).to_have_count(3)

    dashboard.search_for("Video")

    expect(dashboard.row_by_title("Alpha Video")).to_be_visible()
    expect(dashboard.row_by_title("Beta Movie")).to_be_hidden()
    expect(dashboard.row_by_title("Gamma Clip")).to_be_hidden()

    # Editing the search term
    for _ in range(3):
        dashboard.search_input.press("Backspace")

    expect(dashboard.row_by_title("Alpha Video")).to_be_visible(timeout=1000)
    expect(dashboard.row_by_title("Beta Movie")).to_be_visible(timeout=1000)
    expect(dashboard.row_by_title("Gamma Clip")).to_be_hidden(timeout=1000)


def test_search_clear_flow(dashboard, search_items):
    """Verify that the clear button resets visibility and its own state."""
    dashboard.navigate()

    # Input empty, button hidden
    expect(dashboard.clear_btn).to_be_hidden()

    # Button should appear immediately
    dashboard.search_for("Gamma")
    expect(dashboard.clear_btn).to_be_visible()
    expect(dashboard.row_by_title("Alpha Video")).to_be_hidden()

    dashboard.clear_btn.click()

    # Result: Input cleared, button hidden, rows restored
    expect(dashboard.search_input).to_have_value("")
    expect(dashboard.clear_btn).to_be_hidden()
    expect(dashboard.row_by_title("Alpha Video")).to_be_visible()
    expect(dashboard.rows.filter(visible=True)).to_have_count(3)


@pytest.mark.parametrize(
    "test_name, query, expected_row_count",
    [
        ("case_insensitive", "MOVIE", 1),
        ("special_chars", "!!!??###🐍", 0),
        ("untrimmed", "   Beta   ", 1),
        ("spaces_only", "   ", 3),
    ],
    ids=lambda x: x if isinstance(x, str) else "",
)
def test_search_query_variants(
    test_name, query, expected_row_count, dashboard, search_items
):
    dashboard.navigate()
    dashboard.search_for(query)

    expect(dashboard.rows.filter(visible=True)).to_have_count(expected_row_count)

    if "MOVIE" in query.upper() or "BETA" in query.upper():
        expect(dashboard.row_by_title("Beta Movie")).to_be_visible()


def test_filter_hides_but_keeps_dom(dashboard, search_items):
    dashboard.navigate()

    dashboard.search_for("Python")

    alpha_row = dashboard.row_by_title("Alpha Video")
    expect(alpha_row).to_be_attached()

    # But it is not visible to the user
    expect(alpha_row).to_be_hidden()

from media_server.conftest import BASE_URL
from playwright.sync_api import Page


class DashboardPage:
    def __init__(self, page: Page):
        self.page = page
        self.url = f"{BASE_URL}/dashboard"

        self.icon_label_container = ".icon-label-group"

        # Static elements
        self.search_input = page.locator("#searchInput")
        self.clear_btn = page.locator("#clearBtn")
        self.table_info_btn = page.locator("#tableInfo")
        self.theme_toggle = page.locator("#themeToggle")
        self.footer = page.locator("footer")

        # Table
        self.table_container = "#downloadsTable"
        self.table = ".data-table-wrapper"
        self.table_header = page.locator(".data-table-header")
        self.table_body = ".data-table-body"

        self.rows = page.locator(".data-row")
        self.cells = ".cell"

        # Header
        self.h_cell = ".header-cell"

        self.h_checkbox = ".col-checkbox input"
        self.h_col_id = ".col-id"
        self.h_col_media = ".col-media-type"
        self.h_col_name = ".col-name"
        self.h_col_start_time = ".col-start-time"
        self.h_col_status = ".col-status"

        # Body
        self.cell_checkbox = ".col-checkbox input"
        self.b_col_id = ".col-id"

        self.b_col_media = ".col-media-type"
        self.b_col_media_container = f"{self.b_col_media} {self.icon_label_container}"
        self.b_col_media_label = f"{self.b_col_media} .label"
        self.b_col_media_icon = f"{self.b_col_media} i"

        self.b_col_name = ".col-name"
        self.b_col_name_link = f"{self.b_col_name} a"
        self.b_col_title = f"{self.b_col_name} .title"
        self.b_col_url = f"{self.b_col_name} .url"

        self.b_col_start_time = ".col-start-time"

        self.b_col_status = ".col-status"
        self.b_col_status_container = f"{self.b_col_status} {self.icon_label_container}"
        self.b_col_status_label = f"{self.b_col_status} .label"
        self.b_col_status_icon = f"{self.b_col_status} i"

    def navigate(self):
        self.page.goto(self.url)

    def is_visually_truncated(self, locator):
        return locator.evaluate("el => el.scrollWidth > el.clientWidth")

    def get_cell_tooltip(self, locator):
        return locator.get_attribute("title")

from pathlib import Path

from common.variables import GB
from scripts.dunst_config_compiler.src.schema import (
    DunstConfig,
    FullscreenConfig,
    GlobalConfig,
    UrgencyConfig,
)

DUNST_SETTINGS = DunstConfig(
    global_=GlobalConfig(  # pyright: ignore[reportCallIssue]
        follow="keyboard",
        enable_posix_regex=True,
        width=350,
        height=(0, 400),
        notification_limit=5,
        origin="bottom-right",
        offset=(20, 20),
        #
        progress_bar_height=12,
        progress_bar_min_width=100,
        progress_bar_max_width=1000,
        progress_bar_corner_radius=5,
        #
        icon_corner_radius=5,
        transparency=10,
        separator_height=0,
        gap_size=8,
        sort="urgency_descending",
        font="Monospace 12",
        line_height=1,
        #
        icon_path=[Path("/usr/share/icons/Papirus")],
        icon_theme=["Papirus"],
        #
        enable_recursive_icon_lookup=True,
        history_length=10000,
        always_run_script=False,
        corner_radius=10,
        #
        mouse_left_click=["do_action", "close_current"],
        mouse_middle_click=["close_all"],
        mouse_right_click=["close_current"],
        #
        ignore_dbusclose=True,
    ),
    urgency_low=UrgencyConfig(
        foreground=GB.GRAY,
        background=GB.DARK_0_HARD,
        timeout=5,
    ),
    urgency_normal=UrgencyConfig(
        foreground=GB.LIGHT_1,
        background=GB.NEUTRAL_BLUE,
        timeout=7,
    ),
    urgency_critical=UrgencyConfig(
        foreground=GB.LIGHT_1,
        background=GB.FADED_RED,
        frame_color=GB.BRIGHT_YELLOW,
        timeout=10,
    ),
    fullscreen_delay_everything=FullscreenConfig(
        fullscreen="delay",
    ),
    fullscreen_show_critical=FullscreenConfig(
        msg_urgency="critical",
        fullscreen="show",
    ),
)

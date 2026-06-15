from pathlib import Path
from typing import Literal

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StrictInt,
)
from typing_extensions import Annotated

type NonNegativeInt = Annotated[StrictInt, Field(ge=0)]

type ConstantOrRange = NonNegativeInt | tuple[int, int]
"""
Values:
- x: constant width
- (x_min, x_max): expand from min to max as necessary
"""

type Corners = list[
    Literal[
        "none",
        "all",
        "bottom-right",
        "bottom-left",
        "top-right",
        "top-left",
        "top",
        "bottom",
        "left",
        "right",
    ]
]

type MouseAction = list[
    Literal[
        "none",
        "do_action",
        "close_current",
        "close_all",
        "context",
        "context_all",
    ]
]
"""
Values:
- none: Don't do anything.
- do_action: Invoke the action determined by the action_name rule. If there is no such action, open the context menu.
- open_url: If the notification has exactly one url, open it. If there are multiple ones, open the context menu.
- close_current: Close current notification.
- close_all: Close all notifications.
- context: Open context menu for the notification.
- context_all: Open context menu for all notifications.
"""


def validate_dunst_hex_color(v: object) -> str:
    """
    Accepts #RGB or #RRGGBB and #RGBA or #RRGGBBAA.
    """
    if not isinstance(v, str):
        raise ValueError("Color must be a string value")

    color = v.lower()

    # Check the structural requirements
    if not color.startswith("#"):
        raise ValueError("Hex color must start with a '#' character")

    color = color[1:]

    # Validate length
    if len(color) not in (3, 4, 6, 8):
        raise ValueError(
            "Hex color must be exactly 3, 4, 6, or 8 characters long (excluding #)"
        )

    # Ensure every character after the '#' is a valid hex digit
    if not all(char in "0123456789abcdef" for char in color):
        raise ValueError("Color contains invalid non-hexadecimal characters")

    return f"#{color}"


HexColor = Annotated[str, BeforeValidator(validate_dunst_hex_color)]


class StrictModel(BaseModel):
    """Base class to enforce strict typing across all config sections."""

    model_config = ConfigDict(strict=True, populate_by_name=True, validate_default=True)


class GlobalConfig(StrictModel):
    default_pause_level: int = Field(default=0, ge=0, le=100)
    """
    Specify a pause level to be set on dunst startup. Notifications are only shown if
    their urgency level is higher than the pause level.
    """

    monitor: NonNegativeInt | str = 0
    """
    Display notifications on a specific monitor.
    Can be either the id (number) or the name of a monitor. You can get a full list of
    monitors by running `xrandr --listmonitors`.

    Ignored if `follow` is set to "keyboard" or "mouse".
    """

    # TODO: Check behavior of dwm - does it follow mouse or keyboard
    follow: Literal["none", "mouse", "keyboard"] = "none"
    """
    Defines where the notifications should be placed in a multi-monitor setup.

    All values except none override `monitor`.

    Values:
    - none: The notifications will be placed on the monitor specified by the monitor setting.
    - mouse: The notifications will be placed on the monitor that the mouse is currently in.
    - keyboard: The notifications will be placed on the monitor that contains the window
        with keyboard focus.
    """

    enable_posix_regex: bool = False
    """
    Use POSIX regex for filtering rules.

    Values:
    - True: use POSIX regex
    - False: use `fnmatch` for matching strings

    Syntax: https://en.m.wikibooks.org/wiki/Regular_Expressions/POSIX-Extended_Regular_Expressions
    """

    width: ConstantOrRange
    """
    The width of the notification window in pixels.

    If `width` > screen width, clamp to screen width.
    To have dynamic full-screen notifications, set value to a high number (e.g 10000)
    """

    height: ConstantOrRange
    """
    The height of each notification in pixels.
    """

    notification_limit: NonNegativeInt = 20
    """
    The number of notifications that can appear at one time.
    When this limit is reached, additional notifications will be queued and displayed
    when the currently displayed ones either time out or are manually dismissed.

    If `indicate_hidden` is true, then limit is reduced by 1, and last notification is
    the hidden count.

    Value '0' means no limit.
    """

    origin: Literal[
        "top-left",
        "top-center",
        "top-right",
        "bottom-left",
        "bottom-center",
        "bottom-right",
        "left-center",
        "center",
        "right-center",
    ] = "top-right"
    """
    The origin of the notification window on the screen.

    It can then be moved with `offset`.
    """

    offset: tuple[int, int] = (10, 50)
    """
    Offset in pixels from the corner of the screen specified by `origin`

    A negative value will lead to the notification being off screen.
    """

    scale: NonNegativeInt = 0
    """
    Specifies a scale factor for dimensions to adapt notifications to HiDPI screens on X11.
    Try to use a whole number scaling factor.

    Value '0' means the scale factor is auto-detected.
    """

    progress_bar: bool = True
    """
    Draw a progress bar at the bottom of the notification

    Only applies when an integer value is passed to dunst as a hint, like
    `notify-send "Downloading File" "Progress" -h "int:value:100"`
    """

    progress_bar_horizontal_alignment: Literal["left", "center", "right"] = "center"
    """
    Horizontal alignment of the progress bar.

    The progress bar will always keep a distance of `horizontal_padding` from the edge
    of the notification.
    """

    progress_bar_height: NonNegativeInt = 10
    """
    The height of the progress bar in pixel.

    This includes the frame. Make sure this value is bigger than twice the frame width.
    """

    progress_bar_min_width: NonNegativeInt = 150
    """
    The minimum width of the progress bar in pixels.

    If `progress_bar_min_width` > `width`, will throw a warning.
    """

    progress_bar_max_width: NonNegativeInt = 300
    """
    The maximum width of the progress bar in pixels.

    If `progress_bar_max_width` > `width`, will clamp to `width`.
    """

    progress_bar_frame_width: NonNegativeInt = 1
    """
    The frame width of the progress bar in pixels.

    Value should be smaller than half of `progress_bar_height`.
    """

    progress_bar_corner_radius: NonNegativeInt = 0
    """
    The corner radius of the progress bar in pixels.

    Value '0' means disabled.
    """

    progress_bar_corners: Corners = ["all"]
    """
    Define which corners to round when drawing the progress bar.

    If `progress_bar_corner_radius` is set to 0 this option will be ignored.
    """

    icon_corner_radius: NonNegativeInt = 0
    """
    The corner radius of the icon image in pixels.

    Value '0' means disabled.

    This setting will be ignored if `icon_corners` is set to "none".
    """

    icon_corners: Corners = ["all"]
    """
    Define which corners to round when drawing the icon image.

    If `icon_corner_radius` is set to 0 this option will be ignored.
    """

    indicate_hidden: bool = True
    """
    Display currently hidden notification count.

    If value is True, then limit is reduced by 1, and last notification is
    the hidden count.
    """

    transparency: NonNegativeInt = Field(default=0, ge=0, le=100)
    """
    Notification transparency scale

    Values:
    - 0: fully opaque
    - 100: fully invisible

    On Wayland, set the transparency part of a color. Requires a running compositor.
    """

    separator_height: NonNegativeInt = 2
    """
    The height in pixels of the separator between notifications.
    """

    padding: NonNegativeInt = 8
    horizontal_padding: NonNegativeInt = 8
    text_icon_padding: NonNegativeInt = 0
    frame_width: NonNegativeInt = 3
    gap_size: NonNegativeInt = 0

    separator_color: Literal["auto", "foreground", "frame"] | HexColor = "frame"
    """
    Sets the color of the separator line between two notifications.

    Values:
    - auto: Dunst tries to find a color that fits the rest of the notification color
        scheme automatically.
    - foreground: The color will be set to the same as the foreground color of the topmost
        notification that's being separated.
    - frame: The color will be set to the frame color of the notification with the highest
        urgency between the 2 notifications that are being separated.
    - _: Any other value is interpreted as a color.
    """

    sort: Literal[
        "true",
        "false",
        "id",
        "urgency_ascending",
        "urgency_descending",
        "update",
    ] = "true"
    """
    If set to true or urgency_descending, display notifications with higher urgency above the others. critical first, then normal, then low.

    If set to false or id, sort notifications by id.

    If set to urgency_ascending, notifications are sorted by urgency, low first, then normal, then critical.

    If set to update, notifications are sorted by their update_time. So the most recent is always at the top. This means that if you set sort to update, and stack_duplicates to true, the duplicate will always be at the top.

    When the notification window is at the bottom of the screen, this order is automatically reversed.
    """

    idle_threshold: int | str = 0
    layer: str = "overlay"
    force_xwayland: bool = False
    font: str = "Monospace 8"
    line_height: NonNegativeInt = 0

    format: str = "<b>%s</b>\n%b"
    """
    Specifies how the various attributes of the notification should be formatted on the notification window.

    Regardless of the status of the markup setting, any markup tags that are present in the format will be parsed. Note that because of that, if a literal ampersand (&) is needed it needs to be escaped as '&amp;'.

    If '\n' or '\t' is present anywhere in the format, it will be replaced with a literal newline or tab respectively.

    If any of the following strings are present, they will be replaced with the equivalent notification attribute.

    For a complete markup reference, see <https://docs.gtk.org/Pango/pango_markup.html>.

    %a appname
    %s summary
    %b body
    %c category
    %S stack_tag
    %i iconname (including its path)
    %I iconname (without its path)
    %p progress value ([ 0%] to [100%])
    %n progress value without any extra characters
    %% literal %

    If any of these exists in the format but hasn't been specified in the notification (e.g. no icon has been set), the placeholders will simply be removed from the format.
    """

    vertical_alignment: Literal["top", "center", "bottom"] = "center"

    show_age_threshold: int | str = 60
    """
    Show age of message if message is older than this time.

    Set to -1 to disable.
    """

    ignore_newline: bool = False
    stack_duplicates: bool = True
    hide_duplicate_count: bool = False
    show_indicators: bool = True

    icon_path: list[Path] = [
        Path("/usr/share/icons/gnome/16x16/status/"),
        Path("/usr/share/icons/gnome/16x16/devices/"),
    ]
    """
    Can be set to a colon-separated list of paths to search for icons to use with notifications.

    Dunst doens't search outside of these direcories. For a recursive icon lookup system,
    see `enable_recursive_icon_lookup`. This new system will eventually replace icon_path search.
    """

    icon_theme: list[str] = ["Adwaita"]
    """
    Comma-separated list of names of the themes to use for looking up icons. This has
    to be the name of the directory in which the theme is located, not the human-friendly
    name of the theme. So for example, the theme Breeze Dark is located in
    /usr/share/icons/breeze-dark. In this case you have to set the theme to breeze-dark.

    The first theme in the list is the most important. Only if the icon cannot be found
    in that theme, the next theme will be tried.

    Dunst will look for the themes in XDG_DATA_HOME/icons and $XDG_DATA_DIRS/icons as
    specified in the icon theme specification:
    https://specifications.freedesktop.org/icon-theme-spec/icon-theme-spec-latest.html.

    If the theme inherits from other themes, they will be used as a backup.

    This setting is not enabled by default. See enable_recursive_icon_lookup for how to
    enable it.
    """

    enable_recursive_icon_lookup: bool = True
    """
    This setting enables the new icon lookup method. This new system will eventually be
    the old icon lookup.

    Currently icons are looked up in the icon_path. Since the icon_path wasn't recursive,
    one had to add a ton of paths to this list. This has been drastically simplified by
    the new lookup method. Now you only have to set icon_theme to the name of the theme
    you want. To enable this new behavior, set `enable_recursive_icon_lookup` to True.
    """

    sticky_history: bool = True
    history_length: NonNegativeInt = 20
    dmenu: str = "/usr/local/bin/dmenu -p dunst"
    browser: str | Path = Path("/usr/bin/xdg-open")
    always_run_script: bool = True
    title: str = "Dunst"
    class_: str = Field(default="Dunst", alias="class")
    force_xinerama: bool = False
    corner_radius: NonNegativeInt = 0
    corners: Corners = ["all"]

    mouse_left_click: MouseAction = ["close_current"]
    mouse_middle_click: MouseAction = ["do_action", "close_current"]
    mouse_right_click: MouseAction = ["close_all"]

    ignore_dbusclose: bool = False
    override_pause_level: NonNegativeInt = 0


class UrgencyConfig(StrictModel):
    background: HexColor
    foreground: HexColor
    highlight: HexColor | None = None
    frame_color: HexColor | None = None
    timeout: NonNegativeInt
    icon: Path | None = None


class FullscreenConfig(StrictModel):
    fullscreen: Literal["show", "delay", "pushback"]
    """
    Values:
    - show: show the notifications, regardless if there is a fullscreen window opened
    - delay: displays the new notification, if there is no fullscreen window active
        If the notification is already drawn, it won't get undrawn.
    - pushback: same as delay, but when switching into fullscreen, the notification will
        get withdrawn from screen again and will get delayed like a new notification
    """

    msg_urgency: str | None = None


class DunstConfig(StrictModel):
    """
    Config object for Dunst.

    Docs: https://dunst-project.org/documentation/
    """

    global_: GlobalConfig = Field(..., alias="global")

    urgency_low: UrgencyConfig
    urgency_normal: UrgencyConfig
    urgency_critical: UrgencyConfig

    fullscreen_delay_everything: FullscreenConfig
    fullscreen_show_critical: FullscreenConfig

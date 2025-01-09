import textwrap

from configobj import ConfigObj
from validate import Validator

MAX_COMMENT_LENGTH = 72

configspec = {
    "global": {
        # "monitor": "integer(default=0)",
        "follow": "option('none', 'mouse', 'keyboard')",
        "enable_posix_regex": "boolean(default=false)",
        # "geometry": "string", # DEPRECATED
        # "width": "string",
        # "height": "string",
        "notification_limit": "integer(default=20)",
        "origin": "option('top-left', 'top-center', 'top-right', 'bottom-left', 'bottom-center', 'bottom-right', 'left-center', 'center', 'right-center')",
        "offset": "string",
        "scale": "float(default=0)",
        "progress_bar": "boolean(default=true)",
        "progress_bar_horizontal_alignment": "option('left', 'center', 'right')",
        "progress_bar_height": "integer(default=10)",
        "progress_bar_min_width": "integer(default=150)",
        "progress_bar_max_width": "integer(default=300)",
        "progress_bar_frame_width": "integer(default=1)",
        "progress_bar_corner_radius": "integer(default=0)",
        "progress_bar_corners": "string(default='all')",
        "icon_corner_radius": "integer(default=0)",
        "icon_corners": "string(default='all')",
        "indicate_hidden": "boolean(default=true)",
        "transparency": "integer(default=0)",
        # "separator_height": "integer(default=2)",
        # "padding": "integer(default=8)",
        # "horizontal_padding": "integer(default=8)",
        # "text_icon_padding": "integer(default=0)",
        # "frame_width": "integer(default=3)",
        # "gap_size": "integer(default=0)",
        # "separator_color": "option('auto', 'foreground', 'frame', '#RRGGBB')",
        # "sort": "option('true', 'false', 'id', 'urgency_ascending', 'urgency_descending', 'update')",
        # "idle_threshold": "integer(default=0)",
        # "layer": "option('bottom', 'top', 'overlay')",
        # "force_xwayland": "boolean(default=true)",
        # "font": "string",
        # "line_height": "integer(default=0)",
        # "format": "string",
        # "vertical_alignment": "option('top', 'center', 'bottom')",
        # "show_age_threshold": "integer(default=60)",
        # "ignore_newline": "boolean(default=true)",
        # "stack_duplicates": "boolean(default=true)",
        # "hide_duplicate_count": "boolean(default=true)",
        # "show_indicators": "boolean(default=true)",
        # "icon_path": "string",
        # "icon_theme": "string",
        # "enable_recursive_icon_lookup": "boolean(default=false)",
        # "sticky_history": "boolean(default=true)",
        # "history_length": "integer(default=20)",
        # "dmenu": "string",
        # "browser": "string",
        # "always_run_script": "boolean(default=true)",
        # "title": "string",
        # "class": "string",
        # "force_xinerama": "boolean(default=true)",
        # "corner_radius": "integer(default=0)",
        # "corners": "option('none', 'all', 'bottom-right', 'bottom-left', 'top-right', 'top-left', 'top', 'bottom', 'left', 'right')",
        # "mouse_[left/middle/right]_click": "option('none', 'do_action', 'close_current', 'close_all', 'context', 'context_all')",
        # "ignore_dbusclose": "boolean(default=false)",
        # "override_pause_level": "option('0-100')",
    }
}

configspec["global"]["monitor"] = "integer(default=0)"

config = ConfigObj(
    indent_type="    ",
    configspec=configspec,
)


def set_option(section: str, key: str, value: str, description: list[str] = None):
    """
    Helper function to set a function and its comments.
    Uses 'config' and 'configspec' vars implicitly.
    """
    # Ensure the section exists
    if section not in config:
        config[section] = {}

    config[section][key] = value

    spec = configspec.get(section, {}).get(key, None)
    spec_fmt = f":: {spec}"
    spec_included = False

    if not description:
        description = []

    if "{spec}" in description and spec:
        description[description.index("{spec}")] = spec_fmt
        spec_included = True

    # Wrap long comments
    comments_fmt = []
    for comment in description:
        if len(comment) > MAX_COMMENT_LENGTH:
            comments_fmt += textwrap.wrap(comment, width=MAX_COMMENT_LENGTH)
        else:
            comments_fmt += [comment]

    # Include the spec if not already included
    if key not in config[section].comments:
        config[section].comments[key] = []

    config[section].comments[key] += comments_fmt + (
        [spec_fmt] if spec and not spec_included else []
    )

    # Add an empty line between options when appropriate
    if (len(description) > 1 or spec) and len(config[section]) > 1:
        config[section].comments[key].insert(0, "")


spec = "{spec}"

config["global"] = {
    "monitor": "0",
    "follow": "keyboard",
    "enable_posix_regex": "true",
    "width": "350",
    "height": ["(0", "300)"],
    "notification_limit": "5",
    "origin": "bottom-right",
    "offset": "20x20",
    "scale": "0",
    "progress_bar": "true",
    "progress_bar_horizontal_alignment": "center",
    "progress_bar_height": "12",
    "progress_bar_min_width": "100",
    "progress_bar_max_width": "1000",
    "progress_bar_frame_width": "1",
    "progress_bar_corner_radius": "5",
    "icon_corner_radius": "5",
    "icon_corners": "all",
    "indicate_hidden": "true",
    "transparency": "10",
    "separator_height": "0",
    "padding": "8",
    "horizontal_padding": "8",
    "text_icon_padding": "0",
    "frame_width": "3",
    "gap_size": "8",
    "separator_color": "frame",
    "sort": "urgency_descending",
    "idle_threshold": "0",
    "layer": "overlay",
    "force_xwayland": "false",
    "font": "Monospace 12",
    "line_height": "1",
    "format": "<b>%s</b>\\n%b",
    "vertical_alignment": "center",
    "show_age_threshold": "60",
    "ignore_newline": "false",
    "stack_duplicates": "true",
    "hide_duplicate_count": "false",
    "show_indicators": "true",
    "icon_path": "/usr/share/icons/Papirus",
    "icon_theme": "Papirus",
    "enable_recursive_icon_lookup": "true",
    "sticky_history": "true",
    "history_length": "10000",
    "dmenu": "/usr/local/bin/dmenu -p dunst",
    "browser": "/usr/bin/xdg-open",
    "always_run_script": "false",
    "title": "Dunst",
    "class": "Dunst",
    "force_xinerama": "false",
    "corner_radius": "10",
    "mouse_left_click": ["do_action", "close_current"],
    "mouse_middle_click": "close_all",
}

for conf, item in config["global"].items():
    print(f"Option(name='{conf}', value='{item}'),")


set_option(
    "global",
    "monitor",
    "0",
    [
        "Display notifications on a specific monitor.",
        spec,
        "#",
        "Can be either the name or the number of a monitor.",
        "Use `xrandr --listmonitors`.",
        "#",
        "Ignored if 'follow' is set to 'keyboard' or 'mouse'.",
    ],
)

set_option(
    "global",
    "follow",
    "keyboard",
    [
        "Defines where the notifications should be placed in a multi-monitor setup. All values except none override the monitor setting. On Wayland there is no difference between mouse and keyboard focus. When either of them is used, the compositor will choose an output. This will generally be the output last interacted with. none The notifications will be placed on the monitor specified by the monitor setting. mouse The notifications will be placed on the monitor that the mouse is currently in. keyboard The notifications will be placed on the monitor that contains the window with keyboard focus.",
    ],
)


# Urgency
urg_low_section = Section("urgency_low")
urg_low_section.options = [
Option(name="background", value="urgency_low"),
Option(name="foreground", value="urgency_low"),
Option(name="timeout", value="urgency_low"),
]

urg_normal_section = Section("urgency_normal")
urg_normal_section.options = [
Option(name="foreground", value="urgency_normal"),
Option(name="background", value="urgency_normal"),
Option(name="timeout", value="urgency_normal"),
]

urg_critical_section = Section("urgency_critical")
urg_critical_section.options = [
Option(name="background", value="urgency_critical"),
Option(name="foreground", value="urgency_critical"),
Option(name="frame_color", value="urgency_critical"),
Option(name="timeout", value="urgency_critical"),
]

fullscreen_delay_everything_section = Section("fullscreen_delay_everything")
fullscreen_delay_everything_section.options = [
Option(name="fullscreen", value="fullscreen_delay_everything"),
Option(name="msg_urgency", value="fullscreen_show_critical"),
Option(name="fullscreen", value="fullscreen_show_critical"),
]


config.initial_comment = ["Dunst Docs: https://dunst-project.org/documentation/", ""]

validator = Validator()
result = config.validate(validator, preserve_errors=True)

if result is True:
    config.filename = "formatted_config.ini"
    config.write()
else:
    print("ERR: Configuration validation failed!")
    print(result)

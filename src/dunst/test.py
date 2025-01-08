from configobj import ConfigObj
from validate import Validator


class F_Base:
    def __str__(self):
        class_name = self.__class__.__name__
        attributes = "\n".join(f"\t{key}: {value}" for key, value in vars(self).items())
        return f"{class_name}:\n{attributes}"


class Option(F_Base):
    def __init__(
        self,
        name: str = None,
        value: str = None,
        description: list[str] = None,
        type_: str = None,
        default: str = None,
        valid_values: list[str] = None,
    ):
        self.name = name
        self.value = value
        self.description = description
        self.type_ = type_
        self.default = default
        self.valid_values = valid_values

    def compose_spec(self):
        default_fmt = f"default={self.default}" if self.default else None
        options_fmt = (
            ", ".join(map(lambda x: f"'{x}'", self.valid_values))
            if self.valid_values
            else None
        )
        parts = ", ".join(list(filter(bool, [default_fmt, options_fmt])))
        spec = f"{self.type_}{f"({parts})" if parts else ""}"

        return spec


class Section(F_Base):
    def __init__(
        self,
        name: str = None,
        options: list[Option] = None,
        description: str = None,
    ):
        self.name = name
        self.options = options
        self.description = description

    def add_config(self, config):
        if not self.options or len(self.options) == 0:
            return

        if self.name not in config:
            config[self.name] = {}

        for option in self.options:
            config[self.name][option.name] = option.value

    def add_spec(self, config_spec):
        if not self.options or len(self.options) == 0:
            return

        print(self.options, type(self.options), "hey")

        if self.name not in config_spec:
            config_spec[self.name] = {}

        for option in self.options:
            if not option.type_ or (not option.default or not option.valid_values):
                continue
            spec = option.compose_spec()
            config_spec[self.name][option.name] = spec


def write_config(sections):
    config_spec = {}

    # print(config_spec)
    for section in sections:
        section.add_spec(config_spec)

    config = ConfigObj(indent_type=" " * 4, configspec=config_spec)
    config.filename = "config.ini"
    config.initial_comment = [
        "Dunst Docs: https://dunst-project.org/documentation/",
        "",
    ]

    for section in sections:
        section.add_config(config)

    validator = Validator()
    result = config.validate(validator, preserve_errors=True)

    if result is True:
        config.write()
        print(f"Configuration written to '{config.filename}'")
    else:
        print("ERR: Configuration validation failed!")
        print(result)


global_section = Section("global")
global_section.options = [
    Option(
        name="monitor",
        value="0",
        description=[
            "Display notifications on a specific monitor.",
            "Can be monitor name or number (`xrandr --listmonitors`)",
            "",
            "Ignored if 'follow' is set to 'keyboard' or 'mouse'.",
        ],
        type_="string",
        default="0",
    ),
    Option(
        name="follow",
        value="keyboard",
        description="""
Display notifications on the focused monitor.
Values:
  [none]      don't follow anything
  mouse       follow mouse pointer
  keyboard    follow window with keyboard focus

"keyboard" needs a window manager that exports the _NET_ACTIVE_WINDOW property.

Ignore `monitor` if value is set to "keyboard" or "mouse".
TODO: Check behavior of dwm - does if follow mouse or keyboard""",
        type_="option",
        valid_values=["none", "mouse", "keyboard"],
    ),
    Option(name="enable_posix_regex", value="true"),
    Option(name="width", value="350"),
    Option(name="height", value="(0, 300)"),
    Option(name="notification_limit", value="5"),
    Option(name="origin", value="bottom-right"),
    Option(name="offset", value="20x20"),
    Option(name="scale", value="0"),
    Option(name="progress_bar", value="true"),
    Option(name="progress_bar_horizontal_alignment", value="center"),
    Option(name="progress_bar_height", value="12"),
    Option(name="progress_bar_min_width", value="100"),
    Option(name="progress_bar_max_width", value="1000"),
    Option(name="progress_bar_frame_width", value="1"),
    Option(name="progress_bar_corner_radius", value="5"),
    Option(name="icon_corner_radius", value="5"),
    Option(name="icon_corners", value="all"),
    Option(name="indicate_hidden", value="true"),
    Option(name="transparency", value="10"),
    Option(name="separator_height", value="0"),
    Option(name="padding", value="8"),
    Option(name="horizontal_padding", value="8"),
    Option(name="text_icon_padding", value="0"),
    Option(name="frame_width", value="3"),
    Option(name="gap_size", value="8"),
    Option(name="separator_color", value="frame"),
    Option(name="sort", value="urgency_descending"),
    Option(name="idle_threshold", value="0"),
    Option(name="layer", value="overlay"),
    Option(name="force_xwayland", value="false"),
    Option(name="font", value="Monospace 12"),
    Option(name="line_height", value="1"),
    Option(name="format", value="<b>%s</b>\\n%b"),
    Option(name="vertical_alignment", value="center"),
    Option(name="show_age_threshold", value="60"),
    Option(name="ignore_newline", value="false"),
    Option(name="stack_duplicates", value="true"),
    Option(name="hide_duplicate_count", value="false"),
    Option(name="show_indicators", value="true"),
    Option(name="icon_path", value="/usr/share/icons/Papirus"),
    Option(name="icon_theme", value="Papirus"),
    Option(name="enable_recursive_icon_lookup", value="true"),
    Option(name="sticky_history", value="true"),
    Option(name="history_length", value="10000"),
    Option(name="dmenu", value="/usr/local/bin/dmenu -p dunst"),
    Option(name="browser", value="/usr/bin/xdg-open"),
    Option(name="always_run_script", value="false"),
    Option(name="title", value="Dunst"),
    Option(name="class", value="Dunst"),
    Option(name="force_xinerama", value="false"),
    Option(name="corner_radius", value="10"),
    Option(name="mouse_left_click", value='["do_action", "close_current"]'),
    Option(name="mouse_middle_click", value="close_all"),
]

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
    Option(name="fullscreen", value="show"),
]


def main():
    sections = [
        global_section,
        urg_low_section,
        urg_normal_section,
        urg_critical_section,
        fullscreen_delay_everything_section,
    ]

    write_config(sections)


main()

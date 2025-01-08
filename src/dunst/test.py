import textwrap

from configobj import ConfigObj
from validate import Validator

MAX_COMMENT_LENGTH = 72

config_spec = {}

config = ConfigObj(
    indent_type=" " * 4,
    configspec=config_spec,
)


class Option:
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

    def compose_description_fmt(self):
        if self.description:
            # Wrap long comments
            comments_fmt = []
            for comment in option.description:
                if len(comment) > MAX_COMMENT_LENGTH:
                    comments_fmt += textwrap.wrap(comment, width=MAX_COMMENT_LENGTH)
                else:
                    comments_fmt += [comment]

        return comments_fmt + [f":: {self.compose_spec()}"]

    def add_config(self, section: str):
        pass


class Section:
    CONFIG_SPEC = config_spec
    CONFIG = config

    def __init__(
        self,
        name: str = None,
        options: list[Option] = None,
        description: list[str] = None,
    ):
        self.name = name
        self.options = options
        self.description = description

    def add_config(self):
        for d in [self.CONFIG, self.CONFIG_SPEC]:
            if self.name not in d:
                d[self.name] = {}

        for option in self.options:
            self.CONFIG[self.name][option.name] = option.value

            spec = option.compose_spec()

            self.CONFIG_SPEC[self.name][option.name] = spec

            if option.name not in config[self.name].comments:
                config[self.name].comments[option.name] = []

            config[self.name].comments[option.name] += option.compose_description_fmt()


global_section = Section(
    "global",
    [
        Option(
            "monitor",
            "0",
            [
                "Display notifications on a specific monitor.",
                "Can be monitor name or number (`xrandr --listmonitors`)",
                "Ignored if 'follow' is set to 'keyboard' or 'mouse'.",
            ],
            "string",
            "0",
        ),
        Option(
            "follow",
            "keyboard",
            [
                "Defines where the notifications should be placed in a multi-monitor setup. All values except none override the monitor setting. On Wayland there is no difference between mouse and keyboard focus. When either of them is used, the compositor will choose an output. This will generally be the output last interacted with. none The notifications will be placed on the monitor specified by the monitor setting. mouse The notifications will be placed on the monitor that the mouse is currently in. keyboard The notifications will be placed on the monitor that contains the window with keyboard focus.",
            ],
            "option",
            None,
            ["none", "mouse", "keyboard"],
        ),
    ],
)

global_section.add_config()

# print(config, config_spec)

config.initial_comment = ["Dunst Docs: https://dunst-project.org/documentation/", ""]

validator = Validator()
result = config.validate(validator, preserve_errors=True)

if result is True:
    config.filename = "formatted_config.ini"
    config.write()
else:
    print("ERR: Configuration validation failed!")
    print(result)

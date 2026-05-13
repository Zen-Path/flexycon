import os
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError, model_validator

from common.io_utilities import load_json
from common.logger import logger


class GlobalConfig(BaseModel):
    """Schema for global config"""

    ignore: list[str] = Field(default_factory=list)


class LocalConfig(BaseModel):
    """Schema for local config"""

    ignore: list[str] | None = None
    ignore_append: list[str] | None = Field(None, alias="ignore-append")

    @model_validator(mode="after")
    def check_exclusive_fields(self):
        """Ensure both 'ignore' and 'ignore-append' are not set."""
        if self.ignore and self.ignore_append:
            raise ValueError("Cannot define both 'ignore' and 'ignore-append'.")
        return self


class Config(BaseModel):
    """Resolved config from global and local config"""

    ignore: list[str]


def load_global_config() -> GlobalConfig | None:
    """Load and validate the global configuration."""
    config_home = Path(os.getenv("XDG_CONFIG_HOME") or Path.home() / ".config")
    global_path = config_home / "flexycon" / "sync" / "config.json"

    data = load_json(global_path)
    if not data:
        return None

    try:
        return GlobalConfig.model_validate(data)
    except ValidationError as e:
        logger.error(f"Problem validating global config at {str(global_path)!r}: {e}")
        return None


def load_local_config() -> LocalConfig | None:
    """Load and validate the local configuration."""
    local_path = Path.cwd() / ".sync-config.json"
    data = load_json(local_path)
    if not data:
        return None

    try:
        return LocalConfig.model_validate(data)
    except ValidationError as e:
        logger.error(f"Problem validating local config at {str(local_path)!r}: {e}")
        return None


def load_config() -> Config:
    """
    Combine global and local configs according to business rules.
    """
    global_cfg = load_global_config()
    local_cfg = load_local_config()

    # Start with global ignore list or empty
    ignore_patterns = list(global_cfg.ignore) if global_cfg else []

    if local_cfg:
        if local_cfg.ignore is not None:
            # Replace global ignores
            ignore_patterns = list(local_cfg.ignore)
        elif local_cfg.ignore_append is not None:
            # Append to global ignores
            ignore_patterns.extend(local_cfg.ignore_append)

    ignore_patterns = list(dict.fromkeys(ignore_patterns))

    return Config(ignore=ignore_patterns)

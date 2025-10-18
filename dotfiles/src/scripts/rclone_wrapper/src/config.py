import os
from typing import List, Optional

from common.helpers import load_json
from common.logger import logger
from pydantic import BaseModel, Field, ValidationError, model_validator


class GlobalConfig(BaseModel):
    """Schema for global config"""

    ignore: List[str] = Field(default_factory=list)


class LocalConfig(BaseModel):
    """Schema for local config"""

    ignore: Optional[List[str]] = None
    ignore_append: Optional[List[str]] = Field(None, alias="ignore-append")

    @model_validator(mode="after")
    def check_exclusive_fields(self):
        """Ensure both 'ignore' and 'ignore-append' are not set."""
        if self.ignore and self.ignore_append:
            raise ValueError("Cannot define both 'ignore' and 'ignore-append'.")
        return self


def load_global_config() -> Optional[GlobalConfig]:
    """Load and validate the global configuration."""
    xdg_config_home = os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    global_path = os.path.join(xdg_config_home, "flexycon", "sync", "config.json")

    data = load_json(global_path)
    if not data:
        return None

    try:
        return GlobalConfig.model_validate(data)
    except ValidationError as e:
        logger.error(f"Error validating global config at {global_path}: {e}")
        return None


def load_local_config() -> Optional[LocalConfig]:
    """Load and validate the local configuration."""
    local_path = os.path.join(os.getcwd(), ".sync-config.json")

    data = load_json(local_path)
    if not data:
        return None

    try:
        return LocalConfig.model_validate(data)
    except ValidationError as e:
        logger.error(f"Error validating local config at {local_path}: {e}")
        return None


def load_config() -> dict:
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

    ignore_patterns = list(set(ignore_patterns))

    return {"ignore": ignore_patterns}

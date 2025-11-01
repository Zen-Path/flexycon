import os
from pathlib import Path

# When installing flexycon for the first time, env vars aren't set
# yet, so we want to provide a fallback, otherwise we want the
# shortcut consumer to decide weather to expand or not
flex_home = (
    ["$FLEXYCON_HOME"]
    if os.getenv("FLEXYCON_HOME")
    else ["$HOME", ".local", "src", "flexycon"]
)

flex_data_path = (
    Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local/share")) / "flexycon"
)

import os
from enum import Enum
from pathlib import Path


class TargetAction(Enum):
    COPY = "copy"
    LINK = "link"


class TargetPresentAction(Enum):
    OVERWRITE = "overwrite"
    PASS = "pass"


class TargetMissingAction(Enum):
    CREATE = "create"
    PASS = "pass"


class F_File:
    def __init__(
        self,
        source_path,
        target_path,
        file_type="f",
        source_base_dir=os.path.expanduser("~/.local/src/flexycon"),
        target_base_dir=os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
        target_present_action=TargetPresentAction.OVERWRITE,
        target_missing_action=TargetMissingAction.CREATE,
        target_action=TargetAction.LINK,
        git_branch_name=None,
        use_contents=False
    ):
        if source_base_dir:
            self.source_path = os.path.join(source_base_dir, source_path)
        else:
            self.source_path = os.path.expanduser(source_path)
        self.source_path = Path(self.source_path)

        if target_base_dir:
            self.target_path = os.path.join(target_base_dir, target_path)
        else:
            self.target_path = os.path.expanduser(target_path)
        self.target_path = Path(self.target_path)

        if self.source_path == self.target_path:
            raise ValueError(
                f"Source and target path cannot be the same: {self.source_path}"
            )

        self.file_type = file_type
        self.source_base_dir = source_base_dir
        self.target_base_dir = target_base_dir
        self.target_present_action = target_present_action
        self.target_missing_action = target_missing_action
        self.target_action = target_action

        self.git_branch_name = git_branch_name
        self.use_contents = use_contents

    def handle(self):
        if not self.source_path.exists():
            print(f"Source is missing: {self.source_path}, skipping.")
            return

        match self.target_action:
            case TargetAction.LINK:
                pass
            case TargetAction.COPY:
                pass
            case _:
                pass



    def __str__(self):
        return "\n".join(f"{key}: {value}" for key, value in vars(self).items())



Files = [
    F_File("config/alacritty/alacritty.toml", "alacritty/alacritty.toml"),
    F_File("config/bottom/bottom.toml", "bottom/bottom.toml"),
    F_File("~/.local/bin/sysact", "~/.local/src/sysact", source_base_dir=None, target_base_dir=None),
    # F_File("~/.local/bin/sysact", "~/.local/bin/sysact", source_base_dir=None, target_base_dir=None),
]

for file in Files:
    file.handle()
    print(file, '\n')

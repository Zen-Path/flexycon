import os
from pathlib import Path

class F_Path:
    def __init__(
        self,
        path: str,
        base_dir=None,
        git_branch_name=None,
    ):
        """
        Initialize a flexycon path object.

        Args:
            path (str): Absolute file path, or relative to 'base_dir'.
            base_dir (str): Absolute directory path to resolve 'path'.
            git_branch_name (str): Associated Git branch name.
        """
        self.path = Path(
            os.path.join(os.path.expanduser(base_dir), path)
            if base_dir
            else os.path.expanduser(path)
        )

    def __str__(self):
        class_name = self.__class__.__name__
        attributes = "\n".join(f"\t{key}: {value}" for key, value in vars(self).items())
        return f"{class_name}:\n{attributes}"


class F_File(F_Path):
    """
    Flexycon file object.
    """

    def create(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch()


class F_Dir(F_Path):
    def __init__(self, path, base_dir=None, git_branch_name=None, use_contents=False):
        """
        Initialize a flexycon directory object.

        Args:
            use_contents (bool, optional): Whether to use directory contents. Defaults to False.
        """
        super().__init__(path, base_dir, git_branch_name)
        self.use_contents = use_contents

        def get_contents(self):
            self.contents = (
                list(self.path.iterdir()) if self.path.exists() and use_contents else []
            )

    def create(self):
        self.path.mkdir(parents=True, exist_ok=True)


def ensure_exist_files(files):
    """
    Ensure all specified files or directories exist. Create them if necessary.

    Args:
        files (list): List of F_File or F_Dir instances.
    """
    for file in files:
        if not file.path.exists():
            file.create()
            if isinstance(file, F_File):
                print(f"File '{file.path}' created.")
            elif isinstance(file, F_Dir):
                print(f"Directory '{file.path}' created.")
        else:
            # Check if the existing path is of the correct type
            if isinstance(file, F_File) and not file.path.is_file():
                print(f"WRN: Path '{file.path}' exists but is not a file.")
                continue
            elif isinstance(file, F_Dir) and not file.path.is_dir():
                print(f"WRN: Path '{file.path}' exists but is not a directory.")
                continue

            print(f"'{file.path}' exists.")

if __name__ == "__main__":
    files_to_ensure = [
        F_File("test_file.txt", base_dir="~/.local/src/test"),
        F_File("example_directory", base_dir="~/.local/src/test"),
        F_Dir("example_directory/new-file.txt", base_dir="~/.local/src/test"),
    ]
    ensure_exist_files(files_to_ensure)

    # Print the objects
    for file in files_to_ensure:
        print(file)

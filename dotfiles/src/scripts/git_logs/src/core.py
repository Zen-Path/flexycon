from common.helpers import resolve_path


class GitRepo:
    def __init__(self, name: str, path_parts: list[str]):
        self.name = name
        self.path_parts = path_parts
        self.path = resolve_path(self.path_parts)

    def __str__(self):
        return f'GitRepo(name="{self.name}", path="{self.path}")'

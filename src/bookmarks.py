import os
from abc import ABC, abstractmethod
from pathlib import Path


def expand_path(path, expand_vars=True):
    path_str = str(path)
    return Path(os.path.expandvars(path_str) if expand_vars else path_str).resolve()


class Bookmark:
    def __init__(self, key, path):
        self.path = path
        self.key = key


class BookmarkFile(ABC):
    def __init__(self, path, bookmarks, expand_vars=True):
        self.path = expand_path(path)
        self.bookmarks = bookmarks
        self.expand_vars = expand_vars

    @abstractmethod
    def stringify(self):
        pass

    def process(self):
        self.content = self.stringify()
        with open(self.path, "w") as f:
            f.write(self.content)


class ShortcutRc(BookmarkFile):
    def stringify(self):
        result = "# vim: filetype=sh\n\n"
        for bookmark in self.bookmarks:
            result += f'alias {bookmark.key}="{expand_path(bookmark.path) if self.expand_vars else bookmark.path}"\n'
        return result


class ZshNamedDirRc(BookmarkFile):
    def stringify(self):
        result = "# vim: filetype=sh\n\n"
        for bookmark in self.bookmarks:
            result += f"hash -d {bookmark.key}={expand_path(bookmark.path) if self.expand_vars else bookmark.path}\n"
        return result


def main():
    bookmarks = [
        Bookmark("d", "$HOME/Documents"),
        Bookmark("D", "$HOME/Downloads"),
        Bookmark("h", "$HOME"),
        Bookmark("m", "$HOME/Music"),
        Bookmark("p", "$HOME/Pictures"),
        Bookmark("v", "$HOME/Videos"),
        Bookmark("C", "$XDG_CACHE_HOME"),
    ]

    ShortcutRc(
        os.path.join(os.getenv("XDG_CONFIG_HOME", "$HOME/.config"), "shell", "test"),
        bookmarks,
        False,
    ).process()
    ZshNamedDirRc(
        os.path.join(os.getenv("XDG_CONFIG_HOME", "$HOME/.config"), "shell", "test2"),
        bookmarks,
    ).process()


if __name__ == "__main__":
    main()

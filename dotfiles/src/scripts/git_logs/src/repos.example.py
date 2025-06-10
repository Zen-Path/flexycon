from src.core import GitRepo

src_dir = "$XDG_SRC_HOME"

GIT_REPOS = [
    GitRepo("University", ["$HOME", "University"]),
    # Source Repos
    GitRepo("dwm", [src_dir, "dwm-flexipatch"]),
]

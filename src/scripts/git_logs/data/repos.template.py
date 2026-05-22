from common.variables import (
    FLEXYCON_HOME,
    UNIVERSITY_HOME,
)
from scripts.git_logs.src.core import GitRepo

GIT_REPOS = [
    GitRepo("University", UNIVERSITY_HOME),
    GitRepo("flexycon", FLEXYCON_HOME),
]

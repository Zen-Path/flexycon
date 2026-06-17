#!/usr/bin/env python3

# This file is used to customize the Python REPL experience.
# It handles automatic imports for common imports, pretty printing etc.

import datetime as dt
import decimal
import json
import math
import os
import pathlib
import pprint
import random
import shutil
import statistics
import subprocess as sp
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from fractions import Fraction
from math import cos, degrees, log, log2, log10, pi, sin, tan
from os import getenv
from pathlib import Path
from shutil import rmtree, which
from subprocess import Popen, run

# Suppress the "Import not used" warnings
# fmt: off
__all__ = [
    "dt", "datetime", "timedelta",
    "decimal", "Decimal",
    "json",
    "math", "pi", "cos", "sin", "tan", "degrees", "log", "log2", "log10",
    "os", "getenv",
    "pathlib", "Path",
    "random",
    "shutil", "rmtree", "which",
    "statistics",
    "sp", "Popen", "run",
    "Fraction",
]
# fmt: on

sys.displayhook = pprint.pprint


def ls(path: Path | str = ".") -> list[Path] | None:
    """List directory contents and return a list of Path objects."""
    target = Path(os.path.expanduser(str(path)))

    if not target.exists():
        print(f"❌ Error: {str(target)!r} does not exist.")
        return None

    try:
        # Separate directories and files visually
        items = sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))

        output = f"📁 Contents of {str(target.resolve())!r}:\n"
        output += "\n".join(
            f"  {'📁' if item.is_dir() else '📄'} {item.name}" for item in items
        )
        print(output)

        return items

    except Exception as e:
        print(f"❌ Error: Unable to list contents: {e}")
        return None


def cd(path: Path | str = "~") -> Path | None:
    """Change the current working directory and return the new Path object."""
    target = os.path.expanduser(str(path))
    try:
        os.chdir(target)
        new_path = Path(os.getcwd())
        print(f"📁 Current Directory: {str(new_path)!r}")
        return new_path

    except Exception as e:
        print(f"❌ Error: Unable to change directory to '{str(path)!r}': {e}")
        return None


print("🐍 Python REPL ready!\n")

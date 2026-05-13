#!/usr/bin/env python3

# This file is used to customize the Python REPL experience.
# It handles automatic imports for common imports, pretty printing etc.

import json
import os
import pprint
import sys
from datetime import datetime, timedelta
from pathlib import Path

# To suppress the "Import not used" warnings
for i in [json, os, datetime, timedelta, Path]:
    _ = i

sys.displayhook = pprint.pprint

print("🐍 Python REPL ready!\n")

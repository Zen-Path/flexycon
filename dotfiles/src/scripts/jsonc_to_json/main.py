#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import json
import sys

import commentjson

if len(sys.argv) != 3:
    print("Usage: python jsonc2json.py input.jsonc output.json")
    sys.exit(1)

inp, outp = sys.argv[1], sys.argv[2]

with open(inp, "r") as f:
    data = commentjson.load(f)

with open(outp, "w") as f:
    json.dump(data, f, indent=4)

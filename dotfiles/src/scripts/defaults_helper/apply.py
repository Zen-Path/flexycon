#!/usr/bin/env python3
import argparse
import base64
import json
import subprocess
import sys


def apply_value(domain, key, value):
    """Apply a single key/value to the given domain using defaults."""
    try:
        if isinstance(value, bool):
            subprocess.run(
                [
                    "defaults",
                    "write",
                    domain,
                    key,
                    "-bool",
                    "TRUE" if value else "FALSE",
                ],
                check=True,
            )
        elif isinstance(value, int):
            subprocess.run(
                ["defaults", "write", domain, key, "-int", str(value)], check=True
            )
        elif isinstance(value, float):
            subprocess.run(
                ["defaults", "write", domain, key, "-float", str(value)], check=True
            )
        elif isinstance(value, str):
            # Attempt to decode base64, otherwise write as string
            try:
                decoded = base64.b64decode(value, validate=True)
                subprocess.run(
                    ["defaults", "write", domain, key, "-data", decoded.hex()],
                    check=True,
                )
            except Exception:
                subprocess.run(["defaults", "write", domain, key, value], check=True)
        else:
            print(f"⚠️ Skipping {domain}:{key} unsupported type {type(value)}")
    except subprocess.CalledProcessError:
        print(f"❌ Failed to write {domain}:{key}")


def apply_domain(domain, settings):
    """Apply all settings in a domain."""
    for key, value in settings.items():
        apply_value(domain, key, value)


def main():
    parser = argparse.ArgumentParser(
        description="Apply macOS defaults from a JSON dump."
    )
    parser.add_argument(
        "json_file", help="Path to the JSON file containing macOS defaults"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Suppress domain processing messages"
    )
    args = parser.parse_args()

    try:
        with open(args.json_file) as f:
            all_data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to read JSON file: {e}")
        sys.exit(1)

    total = len(all_data)
    print(f"Applying defaults for {total} domains…")

    for i, (domain, settings) in enumerate(all_data.items(), 1):
        apply_domain(domain, settings)
        if not args.quiet and i % 25 == 0:
            print(f"Processed {i}/{total} domains...")

    print("✅ All defaults applied.")
    print(
        "⚠️ Some settings may require logout/restart or restarting apps to take effect."
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nCancelled.")

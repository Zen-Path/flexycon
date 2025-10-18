#!/usr/bin/env python3
import base64
import datetime
import json
import plistlib
import subprocess
import sys


def get_domains():
    """Get a list of all defaults domains on the system."""
    result = subprocess.run(["defaults", "domains"], capture_output=True, text=True)
    domains = [d.strip() for d in result.stdout.split(",") if d.strip()]
    return domains


def read_domain(domain):
    """Read all keys for a given domain and return a dictionary of settings."""
    try:
        result = subprocess.run(
            ["defaults", "export", domain, "-"], capture_output=True
        )
        if result.returncode != 0 or not result.stdout:
            return None
        return plistlib.loads(result.stdout)
    except Exception:
        return None


def safe_convert(obj):
    """Recursively make data JSON serializable."""
    if isinstance(obj, dict):
        return {safe_convert(k): safe_convert(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [safe_convert(v) for v in obj]
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, bytes):
        return base64.b64encode(obj).decode("utf-8")
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    else:
        return str(obj)


def main():
    all_data = {}
    domains = get_domains()
    print(f"Found {len(domains)} domains. Reading…")

    for i, domain in enumerate(domains, 1):
        data = read_domain(domain)
        if data is not None:
            all_data[domain] = safe_convert(data)
        else:
            print(f"⚠️  Skipped: {domain}")
        if i % 25 == 0:
            print(f"Processed {i}/{len(domains)} domains...")

    with open("macos_defaults_dump.json", "w") as f:
        json.dump(all_data, f, indent=2, sort_keys=True, ensure_ascii=False)

    print("✅ Dump complete: macos_defaults_dump.json")
    print(f"Total domains saved: {len(all_data)}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nCancelled.")

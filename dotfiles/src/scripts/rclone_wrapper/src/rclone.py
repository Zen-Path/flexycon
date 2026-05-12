import argparse
import json
from typing import Any


def build_rclone_command(args: argparse.Namespace, config: dict[str, Any]) -> list[str]:
    command = ["rclone"]

    match args.action:
        case "copy" | "c":
            command.append("copy")
        case "sync" | "s":
            command.extend(["sync", "--track-renames"])
        case _:
            return []

    if args.dry_run:
        command.extend(["--dry-run", "--use-json-log"])
    else:
        command.append("--progress")

    command.append("--create-empty-src-dirs")

    for ignore_pattern in config["ignore"]:
        command.extend(["--exclude", ignore_pattern])

    command.extend([args.source, args.destination])

    return command


def parse_rclone_output(output: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    operations_data: list[dict[str, Any]] = []
    stats: dict[str, Any] = {}

    for line in output.splitlines():
        if not line:
            continue

        log_obj = json.loads(line)

        if log_obj.get("stats"):
            stats = log_obj["stats"]

        if log_obj.get("skipped"):
            operations_data.append(
                {
                    "type": log_obj.get("skipped"),
                    "file": log_obj.get("object"),
                    "size": log_obj.get("size", 0),
                }
            )

    return operations_data, stats

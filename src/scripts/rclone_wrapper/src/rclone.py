import argparse
import json
import sys

from pydantic import ValidationError

from common.logger import log
from scripts.rclone_wrapper.src.config import Config
from scripts.rclone_wrapper.src.models import RcloneOperation, RcloneStats


def build_rclone_command(args: argparse.Namespace, config: Config) -> list[str]:
    command = ["rclone"]

    match args.action:
        case "copy" | "c":
            command.append("copy")
        case "sync" | "s":
            command.extend(["sync", "--track-renames"])
        case _:
            raise ValueError(f"Unsupported action {args.action!r}")

    if args.dry_run:
        command.extend(["--dry-run", "--use-json-log"])
    else:
        command.append("--progress")

    command.append("--create-empty-src-dirs")

    for ignore_pattern in config.ignore:
        command.extend(["--exclude", ignore_pattern])

    command.extend([args.source, args.destination])

    return command


def parse_rclone_output(
    output: str,
) -> tuple[list[RcloneOperation], RcloneStats | None]:
    operations: list[RcloneOperation] = []
    stats = None

    for line in output.splitlines():
        if not line:
            continue

        log_obj = json.loads(line)

        if "stats" in log_obj:
            try:
                log.debug(f"Rclone stats:\n{json.dumps(log_obj['stats'], indent=4)}")
                stats = RcloneStats.model_validate(log_obj["stats"])
            except ValidationError as e:
                log.error(f"Problem validating stats: {e}.")

        if log_obj.get("skipped"):
            try:
                operations.append(RcloneOperation.model_validate(log_obj))
            except ValidationError as e:
                log.error(f"Problem validating operation: {e}.")
                sys.exit(1)

    return operations, stats

import csv
import hashlib
import io
import json
import sys
from pathlib import Path
from typing import Any, NotRequired, TypedDict

import openpyxl
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from common.cmd_utilities import run_cmd
from common.logger import log

DEFAULT_STORE_FILE = Path("documents_store.json")

SUPPORTED_EXTENSIONS = {
    ".docx": ".html",
    ".pdf": ".txt",
    ".xlsx": ".csv",
}


class StoreEntry(TypedDict):
    source_path: str
    source_hash: NotRequired[str]
    destination_path: NotRequired[str]
    destination_hash: NotRequired[str]


type DocumentStore = dict[str, StoreEntry]


def normalize_path(filepath: Path | str) -> str:
    """Returns a clean, POSIX-style relative path string for consistent store keys."""
    return Path(filepath).as_posix()


def get_file_hash(filepath: Path) -> str:
    """Returns the SHA-256 hash of a file."""
    if not filepath.exists():
        return ""

    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)

    return hasher.hexdigest()


def load_store(store_path: Path | None = None) -> DocumentStore:
    """Loads the JSON store and returns a dictionary keyed by normalized source_path."""
    store_file = store_path or DEFAULT_STORE_FILE

    try:
        with open(store_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            store: DocumentStore = {}
            for item in data:
                if "source_path" not in item:
                    continue
                norm_key = normalize_path(item["source_path"])
                item["source_path"] = norm_key
                store[norm_key] = item
            return store

    except FileNotFoundError:
        log.warning(f"Store file {str(store_file)!r} not found. Starting fresh.")

    except json.JSONDecodeError:
        log.warning(f"Store file {str(store_file)!r} is corrupted. Starting fresh.")

    return {}


def save_store(store_dict: DocumentStore, store_path: Path | None = None) -> None:
    """Saves the dictionary back to the JSON file as a sorted list of dicts."""
    store_file = store_path or DEFAULT_STORE_FILE

    sorted_data = sorted(store_dict.values(), key=lambda item: item["source_path"])

    with open(store_file, "w", encoding="utf-8") as f:
        json.dump(sorted_data, f, indent=4)

    run_cmd(["prettier", store_file, "-w"])


def get_destination_path(source_file: Path) -> Path | None:
    """Calculates the destination path based on the source file's extension."""
    target_suffix = SUPPORTED_EXTENSIONS.get(source_file.suffix.lower())
    if not target_suffix:
        return None

    return source_file.with_suffix(target_suffix)


# CONVERTERS


def convert_docx(source_file: Path, dest_file: Path) -> tuple[bool, str | None]:
    """
    Convert a Word (.docx) file to HTML.

    Returns:
        tuple of (success, error_msg)
    """
    pandoc_result = run_cmd(
        ["pandoc", source_file, "-t", "html"],
    )
    if not pandoc_result.success:
        return False, f"Conversion with 'pandoc' failed.\n{pandoc_result.output}"

    with open(dest_file, "w", encoding="utf-8") as f:
        f.write(pandoc_result.output)

    # Format destination contents
    prettier_result = run_cmd(
        ["prettier", "--parser", "html", dest_file, "--write"],
    )
    if not prettier_result.success:
        return False, f"Formatting with 'prettier' failed.\n{prettier_result.output}"

    return True, None


def convert_excel(source_file: Path, dest_file: Path) -> tuple[bool, str | None]:
    """
    Convert all sheets of an Excel workbook into a single consolidated CSV file.

    Returns:
        tuple of (success, error_msg)
    """
    wb: Workbook = openpyxl.load_workbook(filename=str(source_file), data_only=True)
    combined_output: list[str] = []

    for sheet_name in wb.sheetnames:
        sheet: Worksheet = wb[sheet_name]
        raw_data: list[tuple[Any, ...]] = list(sheet.iter_rows(values_only=True))

        min_r: int = -1
        max_r: int = -1
        min_c: int = -1
        max_c: int = -1

        for r_idx, row in enumerate(raw_data):
            for c_idx, val in enumerate(row):
                if val is not None and str(val).strip() != "":
                    if min_r == -1 or r_idx < min_r:
                        min_r = r_idx
                    if max_r == -1 or r_idx > max_r:
                        max_r = r_idx
                    if min_c == -1 or c_idx < min_c:
                        min_c = c_idx
                    if max_c == -1 or c_idx > max_c:
                        max_c = c_idx

        # Checking min_r alone is sufficient to know if the sheet had data
        if min_r == -1:
            continue

        sheet_buffer: io.StringIO = io.StringIO()
        writer = csv.writer(sheet_buffer, lineterminator="\n")

        for r_idx in range(min_r, max_r + 1):
            raw_row: tuple[Any, ...] = raw_data[r_idx]
            sliced_row: tuple[Any, ...] = raw_row[min_c : max_c + 1]
            cleaned_row: list[str] = [
                ""
                if v is None
                else str(v).strip().replace("\n", " ").replace("\r", " ")
                for v in sliced_row
            ]
            writer.writerow(cleaned_row)

        sheet_csv_content: str = sheet_buffer.getvalue().strip()

        if sheet_csv_content:
            formatted_sheet: str = f"--- {sheet_name} ---\n{sheet_csv_content}"
            combined_output.append(formatted_sheet)

    if not combined_output:
        return False, "Spreadsheet contains no data across all sheets."

    final_csv_content: str = "\n\n".join(combined_output) + "\n"

    with open(dest_file, "w", encoding="utf-8") as f:
        f.write(final_csv_content)

    return True, None


def convert_pdf(source_file: Path, dest_file: Path) -> tuple[bool, str | None]:
    """
    Convert PDF file to plain text.

    Returns:
        tuple of (success, error_msg)
    """
    result = run_cmd(["pdftotext", source_file, dest_file])
    if not result.success:
        return False, f"Conversion with 'pdftotext' failed.\n{result.output}"

    return True, None


def run_conversion(source_file: Path, dest_file: Path) -> bool:
    """Convert source file to destination based on the source's extension."""
    log.info(f"Processing: {normalize_path(source_file)!r} -> {dest_file.name!r}")

    extension = source_file.suffix.lower()
    match extension:
        case ".docx":
            conversion_fn = convert_docx
        case ".pdf":
            conversion_fn = convert_pdf
        case ".xlsx":
            conversion_fn = convert_excel
        case _:
            log.warning(f"Unknown source file extension {extension!r}")
            return False

    try:
        success, error_msg = conversion_fn(source_file, dest_file)
        if success:
            return True

        log.error(f"Conversion failed for {normalize_path(source_file)!r}: {error_msg}")

    except Exception as e:
        log.error(f"Unable to convert {normalize_path(source_file)!r}: {e}")

    return False


def cmd_sync(
    store: DocumentStore,
    store_path: Path | None,
    pre_commit_hook: bool,
) -> None:
    any_changes_made = False
    conversion_count = 0

    # Clean up the store: remove paths that no longer exist on disk
    missing_paths = [path for path in store if not Path(path).exists()]
    for path in missing_paths:
        log.info(f"Removing missing file from store: {path!r}")
        del store[path]
        any_changes_made = True

    for str_source_path in list(store.keys()):
        source_file = Path(str_source_path)
        destination_file = get_destination_path(source_file)
        if not destination_file:
            log.warning(
                f"Unsupported extension in store, skipping: {str_source_path!r}"
            )
            continue

        current_source_hash = get_file_hash(source_file)
        current_dest_hash = get_file_hash(destination_file)
        store_entry = store[str_source_path]

        needs_conversion = (
            not destination_file.exists()
            or store_entry.get("source_hash") != current_source_hash
            or store_entry.get("destination_hash") != current_dest_hash
        )

        if needs_conversion:
            success = run_conversion(source_file, destination_file)
            if success:
                conversion_count += 1
                store[str_source_path] = {
                    "source_path": str_source_path,
                    "source_hash": current_source_hash,
                    "destination_path": normalize_path(destination_file),
                    "destination_hash": get_file_hash(destination_file),
                }
                any_changes_made = True

    if not any_changes_made:
        return

    save_store(store, store_path)

    if conversion_count > 0:
        log.info("All tracked documents successfully synced.")

    if pre_commit_hook:
        sys.exit(1)


def cmd_add(
    paths: list[Path],
    store: DocumentStore,
    store_path: Path | None,
) -> None:
    added_any = False

    for raw_path in paths:
        if not raw_path.exists() or not raw_path.is_file():
            log.error(f"File not found: {str(raw_path)!r}")
            continue

        if raw_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            supported = ", ".join(SUPPORTED_EXTENSIONS.keys())
            log.error(
                f"Unsupported file extension {raw_path.suffix!r} for {str(raw_path)!r} "
                f"(supported: {supported})"
            )
            continue

        norm_source = normalize_path(raw_path)
        if norm_source in store:
            log.info(f"Already tracked: {norm_source!r}")
        else:
            log.info(f"Tracking document: {norm_source!r}")
            store[norm_source] = {"source_path": norm_source}
            added_any = True

    if added_any:
        # Immediately run sync so hashes and converted files are generated right away
        cmd_sync(store, store_path, pre_commit_hook=False)


def cmd_remove(
    paths: list[Path],
    store: DocumentStore,
    store_path: Path | None,
    delete_generated: bool,
) -> None:
    removed_any = False

    for raw_path in paths:
        norm_source = normalize_path(raw_path)
        entry = store.pop(norm_source, None)

        if not entry:
            log.warning(f"Document is not currently tracked: {norm_source!r}")
            continue

        log.info(f"Stopped tracking: {norm_source!r}")
        removed_any = True

        if delete_generated:
            dest_str = entry.get("destination_path")
            dest_path = Path(dest_str) if dest_str else get_destination_path(raw_path)
            if dest_path and dest_path.exists():
                dest_path.unlink()
                log.info(f"Deleted generated file: {normalize_path(dest_path)!r}")

    if removed_any:
        save_store(store, store_path)

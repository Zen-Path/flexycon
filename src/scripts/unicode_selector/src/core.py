import argparse
import sys

from common.clipboard_utilities import ClipboardManager
from common.cmd_utilities import run_cmd
from common.logger import log
from common.notification_utilities import Notification
from common.prompt_utilities import prompt_options
from scripts.unicode_selector.data.characters import ASCII_BRAILLE, CHARACTERS


def format_char_entries(chars: dict[str, str]) -> list[str]:
    result: list[str] = []
    for char in chars:
        result.append(f"{char} - {chars[char]}")
    return result


def bin_to_braille(
    patterns: list[str], symbols: dict[str, str], by_row: bool = False
) -> list[tuple[str, str]]:
    bin_to_braille = {bin_str: symbol for symbol, bin_str in symbols.items()}
    results: list[tuple[str, str]] = []

    for raw_pattern in patterns:
        if len(raw_pattern) > 8:
            log.warning(
                f"Pattern {raw_pattern!r} exceeds maximum length of 8 characters."
            )
            continue

        if not set(raw_pattern).issubset({"0", "1"}):
            log.warning(
                f"Pattern {raw_pattern!r} contains invalid characters (only '0' and '1' allowed)."
            )
            continue

        # Ensure the pattern is exactly 8 bits long by right-padding with '0'
        padded_pattern = raw_pattern.ljust(8, "0")

        if by_row:
            # Transform row-major input into column-major if requested
            p = padded_pattern
            lookup_key = p[0] + p[2] + p[4] + p[6] + p[1] + p[3] + p[5] + p[7]
        else:
            lookup_key = padded_pattern

        if lookup_key in bin_to_braille:
            symbol = bin_to_braille[lookup_key]
            results.append((symbol, padded_pattern))
        else:
            log.warning(
                f"Pattern {raw_pattern!r} (lookup key: {lookup_key}) not found in data."
            )

    return results


# TODO: handle encoding by row as well
def braille_to_bin(chars: list[str], symbols: dict[str, str]) -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []
    for char in chars:
        if char in symbols:
            results.append((symbols[char], char))
        else:
            log.warning(f"Unknown braille char {char!r}.")

    return results


def ascii_to_braille(
    chars: list[str], symbols: dict[str, str]
) -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []
    for char in chars:
        if char in symbols:
            results.append((symbols[char], char))
        else:
            log.warning(f"Character {char!r} doesn't have a Braille mapping.")

    return results


def handle_braille_mode(args: argparse.Namespace):
    results: list[tuple[str, str]] = []
    output_joiner = " "

    match args.pattern_type:
        case "bin_col" | "bin_row":
            results = bin_to_braille(
                patterns=args.patterns,
                symbols=CHARACTERS["braille"],
                by_row=args.pattern_type == "bin_row",
            )
            output_joiner = ""
        case "ascii":
            results = ascii_to_braille(
                chars=list(" ".join(args.patterns)), symbols=ASCII_BRAILLE
            )
        case "encode":
            results = braille_to_bin(
                chars=list("".join(args.patterns)), symbols=CHARACTERS["braille"]
            )
        case _:
            log.error(f"Unknown pattern type: {args.pattern_type!r}")

    if not results:
        log.debug("Result is empty.")
        return

    if args.pretty_print:
        output = "\n".join(f"{braille} - {pattern!r}" for braille, pattern in results)
    else:
        output = output_joiner.join(braille for braille, _pattern in results)

    print(output)

    if args.copy:
        ClipboardManager.copy_text(output)


def handle_default_mode(args: argparse.Namespace):
    row_count = 20

    char_categories = list(CHARACTERS.keys())
    log.debug(f"char_categories: {char_categories}")

    # Prompt user for a category or common emojis
    selection = prompt_options(
        prompt="Emoji",
        options=char_categories + format_char_entries(CHARACTERS["emoji"]),
        row_count=row_count,
    )

    if selection is None:
        log.error("Selection is empty.")
        sys.exit(1)

    if selection in char_categories:
        selection = prompt_options(
            prompt="Emoji",
            options=format_char_entries(CHARACTERS[selection]),
            row_count=row_count,
        )

        if selection is None:
            log.error("Selection is empty.")
            sys.exit(1)

    selected_chars_parts = [
        line.split(" - ", maxsplit=1) for line in selection.splitlines() if line
    ]
    log.debug(f"Raw selection: {selected_chars_parts}")

    chars = [char_parts[0] for char_parts in selected_chars_parts]

    if args.insert_selection:
        try:
            run_cmd(["xdotool", "type", "".join(chars)])
            log.info("Selection inserted.")
        except Exception as e:
            log.error(f"Could not insert selection: {e}")

    if args.copy:
        ClipboardManager.copy_text("".join(chars))
        log.info("Selection copied.")

        if args.notify:
            Notification("Selection copied", f"Copied {chars}.").send()

from common.logger import log


def format_char_entries(chars: dict[str, str]) -> list[str]:
    result: list[str] = []
    for char in chars:
        result.append(f"{char} - {chars[char]}")
    return result


def braille_bin_to_symbol(
    patterns: list[str], symbols: dict[str, str], by_row: bool = False
) -> dict[str, str] | None:
    bin_to_braille = {bin_str: symbol for symbol, bin_str in symbols.items()}
    results: dict[str, str] = {}

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
            results[symbol] = padded_pattern
        else:
            log.warning(
                f"Pattern {raw_pattern!r} (lookup key: {lookup_key}) not found in data."
            )

    return results

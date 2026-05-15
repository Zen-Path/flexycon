def format_char_entries(chars: dict[str, str]) -> list[str]:
    result: list[str] = []
    for char in chars:
        result.append(f"{char} - {chars[char]}")
    return result

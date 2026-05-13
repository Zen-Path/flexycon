import re
import unicodedata
from typing import Callable


def truncate(
    text: str,
    max_length: int,
    placeholder: str = "…",
    truncate_from_end: bool = True,
) -> str:
    """
    Truncate a string to max_length.

    Parameters:
    - text: the original string
    - max_length: maximum length including placeholder
    - placeholder: string to indicate truncation
    - truncate_start: if True, truncate the start; else truncate the end

    Returns:
    - truncated string with placeholder if necessary
    """
    if len(text) <= max_length:
        return text

    if max_length == 0:
        return ""

    if len(placeholder) >= max_length:
        return truncate(placeholder, max_length, "", truncate_from_end)

    truncated_length = max_length - len(placeholder)
    if truncate_from_end:
        return text[:truncated_length] + placeholder
    else:
        return placeholder + text[-truncated_length:]


def split_acronyms(token: str) -> list[str]:
    """
    Handle acronyms.
    If there's no uppercase letter, return the token as-is. Otherwise, detect
    sequences of 2+ uppercase chars (acronyms). If an acronym is immediately
    followed by a lowercase letter, the last capital joins the lowercase word.

    Examples:
    - HTMLParser → HTML + Parser
    - parseURLString → parse + URL + String
    """
    if not re.search(r"[A-Z]", token):
        return [token]

    parts: list[str] = []
    i = 0
    n = len(token)

    while i < n:
        # Match acronym (2+ uppercase letters)
        match = re.match(r"[A-Z]{2,}", token[i:])
        if match:
            acronym = match.group(0)
            end = i + len(acronym)

            # If next char exists and is lowercase, merge last capital with next word
            if end < n and token[end].islower():
                parts.append(acronym[:-1])
                i = end - 1  # start new word from last uppercase
            else:
                parts.append(acronym)
                i = end
        else:
            # Otherwise, grab the next "normal" word segment
            match = re.match(r"[A-Z][a-z]+|[a-z]+|\d+", token[i:])
            if match:
                parts.append(match.group(0))
                i += len(match.group(0))
            else:
                # fallback: add single char (rare, safety net)
                parts.append(token[i])
                i += 1

    return parts


def split_tokens(tokens: list[str], splitter: Callable[[str], list[str]]) -> list[str]:
    result: list[str] = []
    for token in tokens:
        result.extend(splitter(token))

    return [t for t in result if t]


def split_numbers(token: str) -> list[str]:
    # Split between digit and non-digit boundaries
    return re.split(r"(?<=\D)(?=\d)|(?<=\d)(?=\D)", token)


def split_camel_case(token: str) -> list[str]:
    # Insert space between lowercase and uppercase letter boundaries
    return re.split(r"(?<=[a-z])(?=[A-Z])", token)


def split_into_words(name: str, boundaries: list[str] = [" ", "-", "_"]) -> list[str]:
    """
    Split a string into words in multiple stages.
    """
    if not name:
        return []

    tokens: list[str]
    if boundaries:
        pattern = "|".join(map(re.escape, boundaries))
        tokens = [t for t in re.split(pattern, name) if t]
    else:
        tokens = [name]

    tokens = split_tokens(tokens, split_numbers)
    tokens = split_tokens(tokens, split_camel_case)
    tokens = split_tokens(tokens, split_acronyms)

    return tokens


def remove_diacritics(text: str) -> str:
    # Normalize to decompose characters (e.g., 'ă' becomes 'a' + '˘')
    normalized = unicodedata.normalize("NFD", text)

    # Filter out the "combining" marks (category 'Mn')
    result = "".join(c for c in normalized if unicodedata.category(c) != "Mn")

    return result

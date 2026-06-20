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


def split_into_words(
    text: str, boundaries: list[str] = [" ", "-", "_", "."]
) -> list[str]:
    """
    Split a string into words in multiple stages.
    """
    if not text:
        return []

    tokens: list[str]
    if boundaries:
        pattern = "|".join(map(re.escape, boundaries))
        tokens = [t for t in re.split(pattern, text) if t]
    else:
        tokens = [text]

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


# Converters


def to_alternate_case(text: str, delimiter: str = " ", upper_first: bool = True) -> str:
    """
    Alternates between upper and lower case chars, if available.
    'Simple file name1' -> 'SiMpLe FiLe NaMe 1'
    """
    words = split_into_words(text)

    result: list[str] = []
    upper_next = upper_first

    for word in words:
        new_word = ""

        for char in word:
            # Check if the character is case-sensitive
            if char.upper() != char.lower():
                new_word += char.upper() if upper_next else char.lower()
                upper_next = not upper_next
            else:
                # Keep as-is if alternate case not found
                new_word += char

        result.append(new_word)

    return delimiter.join(result)


def to_camel_case(text: str, delimiter: str = "") -> str:
    """
    First word is lowercase. All other words are in pascal case.
    'Simple file name1' -> 'simpleFileName1'
    """
    words = split_into_words(text)
    if not words:
        return ""

    first = words[0].lower()
    rest = [w[:1].upper() + w[1:].lower() if w else "" for w in words[1:]]

    return delimiter.join([first] + rest)


def to_pascal_case(text: str, delimiter: str = "") -> str:
    """
    Capitalize the first char of each word. All other chars are lowercase.
    'Simple file name1' -> 'SimpleFileName1'
    """
    words = split_into_words(text)
    capitalized_words = [w[:1].upper() + w[1:].lower() if w else "" for w in words]
    return delimiter.join(capitalized_words)


def to_lower_case(text: str, delimiter: str = " ") -> str:
    """
    'Simple file name1' -> 'simple file name 1'
    """
    words = split_into_words(text)
    return delimiter.join(words).lower()


def to_upper_case(text: str, delimiter: str = " ") -> str:
    """
    'Simple file name1' -> 'SIMPLE FILE NAME 1'
    """
    words = split_into_words(text)
    return delimiter.join(words).upper()

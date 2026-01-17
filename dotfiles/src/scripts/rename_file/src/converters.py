from typing import List


def to_camel_case(words: List[str], ext: str = "") -> str:
    if not words:
        return ext.lower()

    # Make first word lowercase
    first = words[0][:1].lower() + words[0][1:]

    # Capitalize each following word
    rest = [w[:1].upper() + w[1:] if w else "" for w in words[1:]]

    return f"{''.join([first] + rest)}{ext.lower()}"


def to_camel_snake_case(words: List[str], ext: str = "") -> str:
    return to_pascal_case(words, ext, "_")


def to_flat_case(words: List[str], ext: str = "") -> str:
    return ("".join(words) + ext).lower()


def to_flat_upper_case(words: List[str], ext: str = "") -> str:
    return to_flat_case(
        words,
        ext,
    ).upper()


def to_kebab_case(words: List[str], ext: str = "") -> str:
    return f"{'-'.join(words)}{ext}".lower()


def to_kebab_upper_case(words: List[str], ext: str = "") -> str:
    return to_kebab_case(words, ext).upper()


def to_lower_case(words: List[str], ext: str = "") -> str:
    return f"{' '.join(words)}{ext}".lower()


def to_pascal_case(words: List[str], ext: str = "", delimiter: str = "") -> str:
    capitalized_words = [w[:1].upper() + w[1:] if w else "" for w in words]
    return delimiter.join(capitalized_words) + ext.lower()


def to_snake_case(words: List[str], ext: str = "") -> str:
    return f"{'_'.join(words)}{ext}".lower()


def to_snake_upper_case(words: List[str], ext: str = "") -> str:
    return to_snake_case(words, ext).upper()


def to_train_case(words: List[str], ext: str = "") -> str:
    return to_pascal_case(words, ext, "-")


def to_upper_case(words: List[str], ext: str = "") -> str:
    return f"{' '.join(words)}{ext}".upper()

import pytest
from common.helpers import split_acronyms, truncate


@pytest.mark.parametrize(
    "token,expected",
    [
        ("userID", ["user", "ID"]),
        ("HTTPRequest", ["HTTP", "Request"]),
        ("HTTPRequestHandler", ["HTTP", "Request", "Handler"]),
        ("parseURLString", ["parse", "URL", "String"]),
    ],
)
def test_acronyms(token, expected):
    assert split_acronyms(token) == expected


@pytest.mark.parametrize(
    "text, max_length, expected",
    [
        # text shorter than max_length
        ("Hello", 10, "Hello"),
        # text equal
        ("HelloWorld", 10, "HelloWorld"),
        # text longer
        ("HelloWorld!", 6, "Hello…"),
        # empty string
        ("", 6, ""),
    ],
)
def test_truncate_simple(text, max_length, expected):
    assert truncate(text, max_length) == expected


@pytest.mark.parametrize(
    "text, max_length, truncate_from_end, expected",
    [
        (
            "HelloWorld",
            6,
            True,
            "Hello…",
        ),
        ("HelloWorld", 6, False, "…World"),
    ],
)
def test_truncate_position(text, max_length, truncate_from_end, expected):
    assert truncate(text, max_length, truncate_from_end=truncate_from_end) == expected


@pytest.mark.parametrize(
    "text, max_length, placeholder, truncate_from_end, expected",
    [
        ("HelloWorld", 6, ">", True, "Hello>"),
        ("HelloWorld", 6, ">>", True, "Hell>>"),
        ("HelloWorld", 6, ">", False, ">World"),
        ("HelloWorld", 6, ">>", False, ">>orld"),
        ("HelloWorld", 6, "", True, "HelloW"),
        ("HelloWorld", 6, "", False, "oWorld"),
        ("Hello", 6, ">>", True, "Hello"),
        # placeholder longer than max_length → truncate placeholder
        ("Hello", 2, "1234", True, "12"),
        ("Hello", 2, "12", True, "12"),
        ("Hello", 2, "34", False, "34"),
    ],
)
def test_truncate_placeholder(
    text, max_length, placeholder, truncate_from_end, expected
):
    assert truncate(text, max_length, placeholder, truncate_from_end) == expected


def test_truncate_max_length_zero():
    assert truncate("Hello", 0) == ""

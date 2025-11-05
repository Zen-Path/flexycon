import pytest
from common.helpers import split_acronyms


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

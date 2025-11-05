import pytest
from common.helpers import split_into_words


@pytest.mark.parametrize(
    "input_str,expected",
    [
        ("lower", ["lower"]),
        ("Title", ["Title"]),
        ("UPPER", ["UPPER"]),
        ("hello world", ["hello", "world"]),
        ("one two three", ["one", "two", "three"]),
        ("hello_world", ["hello", "world"]),
        ("hello-world", ["hello", "world"]),
        ("one-two-three", ["one", "two", "three"]),
    ],
)
def test_simple(input_str, expected):
    assert split_into_words(input_str) == expected


@pytest.mark.parametrize(
    "input_str,expected",
    [
        (
            "here are-mixed_word boundaries",
            ["here", "are", "mixed", "word", "boundaries"],
        ),
        ("hello---world", ["hello", "world"]),
        ("hello---___world", ["hello", "world"]),
        ("one--two  three_four", ["one", "two", "three", "four"]),
        ("hello--world__test", ["hello", "world", "test"]),
        ("--Hello__World--", ["Hello", "World"]),
        ("_Leading_and_trailing_", ["Leading", "and", "trailing"]),
        ("", []),
        (" ", []),
        ("---", []),
        ("___", []),
    ],
)
def test_boundaries(input_str, expected):
    assert split_into_words(input_str) == expected


def test_custom_boundaries():
    assert split_into_words("hello.world+test", boundaries=[".", "+"]) == [
        "hello",
        "world",
        "test",
    ]
    assert split_into_words("foo+bar.baz_qux", boundaries=["+", ".", "_"]) == [
        "foo",
        "bar",
        "baz",
        "qux",
    ]
    assert split_into_words("hello world", boundaries=[]) == ["hello world"]


@pytest.mark.parametrize(
    "input_str,expected",
    [
        ("helloWorld", ["hello", "World"]),
        ("hereAreMultipleWords", ["here", "Are", "Multiple", "Words"]),
    ],
)
def test_camel_case(input_str, expected):
    assert split_into_words(input_str) == expected


@pytest.mark.parametrize(
    "input_str,expected",
    [
        ("HelloWorld", ["Hello", "World"]),
        ("MyFileName", ["My", "File", "Name"]),
    ],
)
def test_pascal_case(input_str, expected):
    assert split_into_words(input_str) == expected


@pytest.mark.parametrize(
    "input_str,expected",
    [
        ("HTTPRequestHandler", ["HTTP", "Request", "Handler"]),
        ("parseURLString", ["parse", "URL", "String"]),
    ],
)
def test_acronyms(input_str, expected):
    assert split_into_words(input_str) == expected


@pytest.mark.parametrize(
    "input_str,expected",
    [
        ("hello_World-Test", ["hello", "World", "Test"]),
        ("My_fileName-Test_case", ["My", "file", "Name", "Test", "case"]),
        ("Almost_snake_case", ["Almost", "snake", "case"]),
        ("almost-Kebab-Case", ["almost", "Kebab", "Case"]),
    ],
)
def test_mixed_styles(input_str, expected):
    assert split_into_words(input_str) == expected


@pytest.mark.parametrize(
    "input_str,expected",
    [
        ("123", ["123"]),
        ("file1", ["file", "1"]),
        ("file123", ["file", "123"]),
        ("1file", ["1", "file"]),
        ("123file", ["123", "file"]),
        ("file1test", ["file", "1", "test"]),
        ("file123test", ["file", "123", "test"]),
        ("file1Version2", ["file", "1", "Version", "2"]),
        ("a1b12c123d1234", ["a", "1", "b", "12", "c", "123", "d", "1234"]),
        ("fileVersion10Alpha2", ["file", "Version", "10", "Alpha", "2"]),
        ("Test_2025Data", ["Test", "2025", "Data"]),
        ("data_2025_11_04_sample", ["data", "2025", "11", "04", "sample"]),
    ],
)
def test_numbers(input_str, expected):
    assert split_into_words(input_str) == expected


@pytest.mark.parametrize(
    "input_str,expected",
    [
        ("helloWorld_test-XML2File", ["hello", "World", "test", "XML", "2", "File"]),
        ("MyURLParser_v2-TestCase", ["My", "URL", "Parser", "v", "2", "Test", "Case"]),
        (
            "DataSet2025_Results-vFinal",
            ["Data", "Set", "2025", "Results", "v", "Final"],
        ),
        ("parseURL2HTTPResponse", ["parse", "URL", "2", "HTTP", "Response"]),
        ("HTML5CanvasAPI", ["HTML", "5", "Canvas", "API"]),
        ("hello123world456", ["hello", "123", "world", "456"]),
    ],
)
def test_complex_combinations(input_str, expected):
    assert split_into_words(input_str) == expected

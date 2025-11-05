import os
from pathlib import Path

import pytest
from common.helpers import split_into_words
from scripts.rename_file.src.converters import (
    to_camel_case,
    to_camel_snake_case,
    to_flat_case,
    to_flat_upper_case,
    to_kebab_case,
    to_kebab_upper_case,
    to_lower_case,
    to_pascal_case,
    to_snake_case,
    to_snake_upper_case,
    to_train_case,
    to_upper_case,
)


def process_path(path_str: str):
    root, ext = os.path.splitext(Path(path_str).name)
    words = split_into_words(root)
    return {"words": words, "ext": ext}


@pytest.mark.parametrize(
    "path,expected",
    [
        ("hello world", "helloWorld"),
        ("hello world.EXT", "helloWorld.ext"),
        ("Hello World.ext", "helloWorld.ext"),
    ],
)
def test_camel_case(path, expected):
    assert to_camel_case(**process_path(path)) == expected


@pytest.mark.parametrize(
    "path,expected",
    [
        ("hello world", "Hello_World"),
        ("hello world.EXT", "Hello_World.ext"),
        ("Hello World.ext", "Hello_World.ext"),
    ],
)
def test_camel_snake_case(path, expected):
    assert to_camel_snake_case(**process_path(path)) == expected


@pytest.mark.parametrize(
    "path,expected",
    [
        ("hello world", "helloworld"),
        ("hello world.EXT", "helloworld.ext"),
        ("Hello World.ext", "helloworld.ext"),
    ],
)
def test_flat_case(path, expected):
    assert to_flat_case(**process_path(path)) == expected


@pytest.mark.parametrize(
    "path,expected",
    [
        ("hello world", "HELLOWORLD"),
        ("hello world.EXT", "HELLOWORLD.EXT"),
        ("Hello World.ext", "HELLOWORLD.EXT"),
    ],
)
def test_flat_upper_case(path, expected):
    assert to_flat_upper_case(**process_path(path)) == expected


@pytest.mark.parametrize(
    "path,expected",
    [
        ("hello world", "hello-world"),
        ("hello world.EXT", "hello-world.ext"),
        ("Hello World.ext", "hello-world.ext"),
    ],
)
def test_kebab_case(path, expected):
    assert to_kebab_case(**process_path(path)) == expected


@pytest.mark.parametrize(
    "path,expected",
    [
        ("hello world", "HELLO-WORLD"),
        ("hello world.EXT", "HELLO-WORLD.EXT"),
        ("Hello World.ext", "HELLO-WORLD.EXT"),
    ],
)
def test_kebab_upper_case(path, expected):
    assert to_kebab_upper_case(**process_path(path)) == expected


@pytest.mark.parametrize(
    "path,expected",
    [
        ("hello world", "hello world"),
        ("hello world.EXT", "hello world.ext"),
        ("Hello World.ext", "hello world.ext"),
    ],
)
def test_lower_case(path, expected):
    assert to_lower_case(**process_path(path)) == expected


@pytest.mark.parametrize(
    "path,expected",
    [
        ("hello world", "HelloWorld"),
        ("hello world.EXT", "HelloWorld.ext"),
        ("Hello World.ext", "HelloWorld.ext"),
    ],
)
def test_pascal_case(path, expected):
    assert to_pascal_case(**process_path(path)) == expected


@pytest.mark.parametrize(
    "path,expected",
    [
        ("hello world", "hello_world"),
        ("hello world.EXT", "hello_world.ext"),
        ("Hello World.ext", "hello_world.ext"),
    ],
)
def test_snake_case(path, expected):
    assert to_snake_case(**process_path(path)) == expected


@pytest.mark.parametrize(
    "path,expected",
    [
        ("hello world", "HELLO_WORLD"),
        ("hello world.EXT", "HELLO_WORLD.EXT"),
        ("Hello World.ext", "HELLO_WORLD.EXT"),
    ],
)
def test_snake_upper_case(path, expected):
    assert to_snake_upper_case(**process_path(path)) == expected


@pytest.mark.parametrize(
    "path,expected",
    [
        ("hello world", "Hello-World"),
        ("hello world.EXT", "Hello-World.ext"),
        ("Hello World.ext", "Hello-World.ext"),
    ],
)
def test_train_case(path, expected):
    assert to_train_case(**process_path(path)) == expected


@pytest.mark.parametrize(
    "path,expected",
    [
        ("hello world", "HELLO WORLD"),
        ("hello world.EXT", "HELLO WORLD.EXT"),
        ("Hello World.ext", "HELLO WORLD.EXT"),
    ],
)
def test_upper_case(path, expected):
    assert to_upper_case(**process_path(path)) == expected

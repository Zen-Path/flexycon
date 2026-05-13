import pytest
from common.prompt_utilities import prompt_bool


@pytest.mark.parametrize("user_input", ["y", "yes", "1", "  Y  ", "YES", "YeS", "yEs"])
def test_positive_responses(monkeypatch: pytest.MonkeyPatch, user_input: str):
    """Checks that all truthy variations return True."""

    def mock_input(_: str) -> str:
        return user_input

    monkeypatch.setattr("builtins.input", mock_input)
    assert prompt_bool("Continue?") is True


@pytest.mark.parametrize("user_input", ["n", "no", "0", "  NO  ", "nO", "No"])
def test_negative_responses(monkeypatch: pytest.MonkeyPatch, user_input: str):
    """Checks that all falsy variations return False."""

    def mock_input(_: str) -> str:
        return user_input

    monkeypatch.setattr("builtins.input", mock_input)
    assert prompt_bool("Exit?") is False


@pytest.mark.parametrize("user_input", ["", "maybe", "yees", "noo", "-1", "999"])
def test_empty_or_invalid_input_returns_default(
    monkeypatch: pytest.MonkeyPatch, user_input: str
):
    """Ensures empty strings or garbage input fall back to the default."""

    def mock_input(_: str) -> str:
        return user_input

    monkeypatch.setattr("builtins.input", mock_input)
    for default_val in [True, False, None]:
        assert prompt_bool("Go?", default=default_val) is default_val


@pytest.mark.parametrize("exception", [KeyboardInterrupt, EOFError])
def test_exceptions_return_default(
    monkeypatch: pytest.MonkeyPatch, exception: Exception
):
    """Simulates Ctrl+C and Ctrl+D to ensure they return the default."""

    def mock_raise(_: str):
        raise exception

    monkeypatch.setattr("builtins.input", mock_raise)
    for default_val in [True, False, None]:
        assert prompt_bool("Interrupted", default=default_val) is default_val


def test_correct_hint_capitalization(monkeypatch: pytest.MonkeyPatch):
    """Verifies the hint format"""
    captured_prompts: list[str] = []

    def mock_input(prompt_str: str) -> str:
        captured_prompts.append(prompt_str)
        return "y"

    monkeypatch.setattr("builtins.input", mock_input)

    prompt_bool("Default True", default=True)
    prompt_bool("Default False", default=False)
    prompt_bool("Default None", default=None)

    assert "Default True (Y/n): " in captured_prompts[0]
    assert "Default False (y/N): " in captured_prompts[1]
    assert "Default None (y/n): " in captured_prompts[2]

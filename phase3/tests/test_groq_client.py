"""
Tests for Groq client. Unit test mocks the SDK; integration test skipped without GROQ_API_KEY.
"""

import os
from unittest.mock import MagicMock, patch

import pytest
from src.groq_client import get_completion, DEFAULT_MODEL


@patch("groq.Groq")
def test_get_completion_returns_content(mock_groq_class):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Hello from Groq."))]
    )
    mock_groq_class.return_value = mock_client

    with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}, clear=False):
        out = get_completion("Hello")
    assert out == "Hello from Groq."
    mock_client.chat.completions.create.assert_called_once()


def test_get_completion_raises_without_api_key():
    orig = os.environ.get("GROQ_API_KEY")
    try:
        os.environ.pop("GROQ_API_KEY", None)
        with pytest.raises(ValueError) as exc_info:
            get_completion("Hi")
        assert "GROQ_API_KEY" in str(exc_info.value)
    finally:
        if orig is not None:
            os.environ["GROQ_API_KEY"] = orig


@pytest.mark.skipif(
    not os.environ.get("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set; run after connecting API key",
)
def test_get_completion_integration_real():
    """Integration test: real Groq API call. Run only when GROQ_API_KEY is set."""
    out = get_completion("Reply with exactly: OK", model=DEFAULT_MODEL, max_tokens=10)
    assert "OK" in out or len(out) >= 1

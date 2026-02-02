"""Shared fixtures for state transition tests."""

from unittest.mock import Mock

import dspy
import pytest
from httpx import Response


def mock_searxng_response(*args, **kwargs):
    """Create a mock httpx Response for SearXNG."""
    mock_response = Mock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {
                "title": "AI Overview",
                "url": "https://example.com/ai",
                "content": "Artificial intelligence is a field of computer science.",
                "engine": "google",
                "score": 0.9,
            }
        ]
    }
    mock_response.raise_for_status = Mock()
    return mock_response


@pytest.fixture(autouse=True)
def configure_dspy_small() -> None:
    """Configure DSPy with small Ollama model for testing."""
    # Use deepseek-r1:1.5b (smallest available model) for faster tests
    lm = dspy.LM(
        "ollama_chat/deepseek-r1:1.5b",
        api_base="http://localhost:11434",
        api_key="",
        temperature=0.7,
        max_tokens=512,
    )
    dspy.configure(lm=lm)

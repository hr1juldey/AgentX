# =============================================================================
# AGENTX R014 - Smoke Tests for External Dependencies
# =============================================================================

import pytest
import httpx


@pytest.mark.requires_ollama
def test_ollama_is_running():
    """Verify Ollama is accessible and has qwen3:8b model."""
    response = httpx.get("http://localhost:11434/api/tags", timeout=5.0)
    assert response.status_code == 200

    models = response.json().get("models", [])
    model_names = [m.get("name", "") for m in models]

    # Check qwen3:8b is available
    has_qwen = any("qwen3:8b" in name for name in model_names)
    assert has_qwen, f"qwen3:8b not found. Available: {model_names}"


@pytest.mark.requires_searxng
def test_searxng_is_accessible():
    """Verify SearXNG is accessible at configured URL."""
    from config.settings import settings

    response = httpx.get(settings.searxng_url, timeout=5.0)
    assert response.status_code == 200
    assert "html" in response.headers.get("content-type", "").lower()

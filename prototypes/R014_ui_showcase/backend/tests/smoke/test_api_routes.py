# =============================================================================
# AGENTX R014 - Smoke Tests for API Routes
# =============================================================================

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    """Test /health endpoint returns valid response."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "llm" in data
    assert data["llm"]["provider"] == "ollama"


@pytest.mark.requires_ollama
def test_mock_generate_endpoint_basic(client):
    """Test /mock/generate endpoint with simple request."""
    response = client.post(
        "/api/v1/mock/generate",
        json={"widget_type": "markdown", "prompt": "Test prompt"},
    )

    # Should either succeed or return error widget
    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert "type" in data
    assert data["type"] == "markdown"


@pytest.mark.requires_ollama
@pytest.mark.slow
def test_generate_widget_endpoint_basic(client):
    """Test /generate-widget endpoint with simple query."""
    response = client.post(
        "/api/v1/generate-widget", json={"prompt": "Show me a chart of stock prices"}
    )

    assert response.status_code == 200
    data = response.json()

    assert "widgets" in data
    assert isinstance(data["widgets"], list)


@pytest.mark.requires_ollama
@pytest.mark.requires_searxng
@pytest.mark.slow
def test_search_endpoint_basic(client):
    """Test /search endpoint with simple query."""
    response = client.post(
        "/api/v1/search", json={"query": "What is the current stock market trend?"}
    )

    assert response.status_code == 200
    data = response.json()

    assert "answer" in data
    assert len(data["answer"]) > 0

# =============================================================================
# AGENTX Prototype - API Tests
# =============================================================================
# Pytest tests for API endpoints
# =============================================================================

from fastapi.testclient import TestClient

from main import app
from models.schemas import ItemCreate


def test_root() -> None:
    """Test root endpoint."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "app" in data


def test_health() -> None:
    """Test health check endpoint."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_item() -> None:
    """Test creating an item."""
    client = TestClient(app)
    item_data = {"name": "Test Item", "description": "Test description"}
    response = client.post("/api/v1/items", json=item_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert "id" in data


def test_get_item() -> None:
    """Test getting an item."""
    client = TestClient(app)
    # First create an item
    create_response = client.post(
        "/api/v1/items", json={"name": "Test Item", "description": "Test"}
    )
    item_id = create_response.json()["id"]
    # Then get it
    response = client.get(f"/api/v1/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["id"] == item_id


def test_list_items() -> None:
    """Test listing items."""
    client = TestClient(app)
    response = client.get("/api/v1/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_delete_item() -> None:
    """Test deleting an item."""
    client = TestClient(app)
    # Create an item
    create_response = client.post(
        "/api/v1/items", json={"name": "ToDelete", "description": "Will be deleted"}
    )
    item_id = create_response.json()["id"]
    # Delete it
    delete_response = client.delete(f"/api/v1/items/{item_id}")
    assert delete_response.status_code == 204
    # Verify it's gone
    get_response = client.get(f"/api/v1/items/{item_id}")
    assert get_response.status_code == 404


def test_get_nonexistent_item() -> None:
    """Test getting a non-existent item."""
    client = TestClient(app)
    response = client.get("/api/v1/items/99999")
    assert response.status_code == 404

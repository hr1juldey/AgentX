# =============================================================================
# R001 Personal Notes - API Tests
# =============================================================================
# Pytest tests for note API endpoints
# =============================================================================

from fastapi.testclient import TestClient

from main import app
from models.schemas import NoteCreate


def test_root() -> None:
    """Test root endpoint."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert data["app"] == "Personal Notes"


def test_health() -> None:
    """Test health check endpoint."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_note() -> None:
    """Test creating a note."""
    client = TestClient(app)
    note_data = {"title": "Test Note", "content": "This is a test note"}
    response = client.post("/api/v1/notes", json=note_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "This is a test note"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_get_note() -> None:
    """Test getting a note."""
    client = TestClient(app)
    # First create a note
    create_response = client.post(
        "/api/v1/notes", json={"title": "Get Test", "content": "Testing get endpoint"}
    )
    note_id = create_response.json()["id"]
    # Then get it
    response = client.get(f"/api/v1/notes/{note_id}")
    assert response.status_code == 200
    assert response.json()["id"] == note_id
    assert response.json()["title"] == "Get Test"


def test_list_notes() -> None:
    """Test listing notes."""
    client = TestClient(app)
    # Create a few notes
    client.post("/api/v1/notes", json={"title": "Note 1", "content": "Content 1"})
    client.post("/api/v1/notes", json={"title": "Note 2", "content": "Content 2"})
    # List notes
    response = client.get("/api/v1/notes")
    assert response.status_code == 200
    data = response.json()
    assert "notes" in data
    assert "total" in data
    assert data["total"] >= 2


def test_update_note() -> None:
    """Test updating a note."""
    client = TestClient(app)
    # Create a note
    create_response = client.post(
        "/api/v1/notes", json={"title": "Original Title", "content": "Original content"}
    )
    note_id = create_response.json()["id"]
    # Update it
    update_response = client.put(
        f"/api/v1/notes/{note_id}", json={"title": "Updated Title"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Title"
    assert update_response.json()["content"] == "Original content"


def test_delete_note() -> None:
    """Test deleting a note."""
    client = TestClient(app)
    # Create a note
    create_response = client.post(
        "/api/v1/notes", json={"title": "To Delete", "content": "Will be deleted"}
    )
    note_id = create_response.json()["id"]
    # Delete it
    delete_response = client.delete(f"/api/v1/notes/{note_id}")
    assert delete_response.status_code == 204
    # Verify it's gone
    get_response = client.get(f"/api/v1/notes/{note_id}")
    assert get_response.status_code == 404


def test_get_nonexistent_note() -> None:
    """Test getting a non-existent note."""
    client = TestClient(app)
    response = client.get("/api/v1/notes/99999")
    assert response.status_code == 404


def test_update_nonexistent_note() -> None:
    """Test updating a non-existent note."""
    client = TestClient(app)
    response = client.put("/api/v1/notes/99999", json={"title": "Won't work"})
    assert response.status_code == 404


def test_delete_nonexistent_note() -> None:
    """Test deleting a non-existent note."""
    client = TestClient(app)
    response = client.delete("/api/v1/notes/99999")
    assert response.status_code == 404


def test_create_note_validation() -> None:
    """Test validation when creating a note."""
    client = TestClient(app)
    # Missing title
    response = client.post("/api/v1/notes", json={"content": "No title"})
    assert response.status_code == 422
    # Missing content
    response = client.post("/api/v1/notes", json={"title": "No content"})
    assert response.status_code == 422
    # Empty title
    response = client.post("/api/v1/notes", json={"title": "", "content": "Content"})
    assert response.status_code == 422

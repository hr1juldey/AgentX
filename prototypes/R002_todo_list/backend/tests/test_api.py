# =============================================================================
# R002 Todo List - API Tests
# =============================================================================
# Pytest tests for todo API endpoints
# =============================================================================

from datetime import datetime

from fastapi.testclient import TestClient

from main import app


def test_root() -> None:
    """Test root endpoint."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert data["app"] == "Todo List"


def test_health() -> None:
    """Test health check endpoint."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_todo() -> None:
    """Test creating a todo."""
    client = TestClient(app)
    todo_data = {
        "title": "Test Todo",
        "description": "This is a test todo",
        "priority": "high",
        "status": "todo",
    }
    response = client.post("/api/v1/todos", json=todo_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["description"] == "This is a test todo"
    assert data["priority"] == "high"
    assert data["status"] == "todo"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_todo_with_defaults() -> None:
    """Test creating a todo with default values."""
    client = TestClient(app)
    todo_data = {"title": "Simple Todo"}
    response = client.post("/api/v1/todos", json=todo_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Simple Todo"
    assert data["priority"] == "medium"  # default
    assert data["status"] == "todo"  # default


def test_create_todo_with_due_date() -> None:
    """Test creating a todo with a due date."""
    client = TestClient(app)
    due_date = datetime.now().isoformat()
    todo_data = {"title": "Todo with due date", "due_date": due_date}
    response = client.post("/api/v1/todos", json=todo_data)
    assert response.status_code == 201
    data = response.json()
    assert data["due_date"] is not None


def test_get_todo() -> None:
    """Test getting a todo."""
    client = TestClient(app)
    # First create a todo
    create_response = client.post(
        "/api/v1/todos", json={"title": "Get Test", "description": "Testing get endpoint"}
    )
    todo_id = create_response.json()["id"]
    # Then get it
    response = client.get(f"/api/v1/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["id"] == todo_id
    assert response.json()["title"] == "Get Test"


def test_list_todos() -> None:
    """Test listing todos."""
    client = TestClient(app)
    # Create a few todos
    client.post("/api/v1/todos", json={"title": "Todo 1", "priority": "low"})
    client.post("/api/v1/todos", json={"title": "Todo 2", "priority": "high"})
    # List todos
    response = client.get("/api/v1/todos")
    assert response.status_code == 200
    data = response.json()
    assert "todos" in data
    assert "total" in data
    assert data["total"] >= 2


def test_list_todos_with_status_filter() -> None:
    """Test listing todos filtered by status."""
    client = TestClient(app)
    # Create todos with different statuses
    client.post("/api/v1/todos", json={"title": "Todo 1", "status": "todo"})
    client.post("/api/v1/todos", json={"title": "Todo 2", "status": "done"})
    # Filter by status
    response = client.get("/api/v1/todos?status=done")
    assert response.status_code == 200
    data = response.json()
    for todo in data["todos"]:
        assert todo["status"] == "done"


def test_list_todos_with_priority_filter() -> None:
    """Test listing todos filtered by priority."""
    client = TestClient(app)
    # Create todos with different priorities
    client.post("/api/v1/todos", json={"title": "Todo 1", "priority": "high"})
    client.post("/api/v1/todos", json={"title": "Todo 2", "priority": "low"})
    # Filter by priority
    response = client.get("/api/v1/todos?priority=high")
    assert response.status_code == 200
    data = response.json()
    for todo in data["todos"]:
        assert todo["priority"] == "high"


def test_update_todo() -> None:
    """Test updating a todo."""
    client = TestClient(app)
    # Create a todo
    create_response = client.post(
        "/api/v1/todos",
        json={"title": "Original Title", "status": "todo", "priority": "low"},
    )
    todo_id = create_response.json()["id"]
    # Update it
    update_response = client.put(
        f"/api/v1/todos/{todo_id}", json={"title": "Updated Title", "status": "in_progress"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Title"
    assert update_response.json()["status"] == "in_progress"
    # Original priority should remain
    assert update_response.json()["priority"] == "low"


def test_delete_todo() -> None:
    """Test deleting a todo."""
    client = TestClient(app)
    # Create a todo
    create_response = client.post("/api/v1/todos", json={"title": "To Delete"})
    todo_id = create_response.json()["id"]
    # Delete it
    delete_response = client.delete(f"/api/v1/todos/{todo_id}")
    assert delete_response.status_code == 204
    # Verify it's gone
    get_response = client.get(f"/api/v1/todos/{todo_id}")
    assert get_response.status_code == 404


def test_get_nonexistent_todo() -> None:
    """Test getting a non-existent todo."""
    client = TestClient(app)
    response = client.get("/api/v1/todos/99999")
    assert response.status_code == 404


def test_update_nonexistent_todo() -> None:
    """Test updating a non-existent todo."""
    client = TestClient(app)
    response = client.put("/api/v1/todos/99999", json={"title": "Won't work"})
    assert response.status_code == 404


def test_delete_nonexistent_todo() -> None:
    """Test deleting a non-existent todo."""
    client = TestClient(app)
    response = client.delete("/api/v1/todos/99999")
    assert response.status_code == 404


def test_create_todo_validation() -> None:
    """Test validation when creating a todo."""
    client = TestClient(app)
    # Missing title
    response = client.post("/api/v1/todos", json={})
    assert response.status_code == 422
    # Empty title
    response = client.post("/api/v1/todos", json={"title": ""})
    assert response.status_code == 422
    # Invalid status
    response = client.post("/api/v1/todos", json={"title": "Test", "status": "invalid"})
    assert response.status_code == 422
    # Invalid priority
    response = client.post("/api/v1/todos", json={"title": "Test", "priority": "urgent"})
    assert response.status_code == 422


def test_update_todo_status() -> None:
    """Test updating todo status through workflow."""
    client = TestClient(app)
    # Create a todo
    create_response = client.post(
        "/api/v1/todos", json={"title": "Workflow Test", "status": "todo"}
    )
    todo_id = create_response.json()["id"]

    # Update to in_progress
    response = client.put(f"/api/v1/todos/{todo_id}", json={"status": "in_progress"})
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"

    # Update to done
    response = client.put(f"/api/v1/todos/{todo_id}", json={"status": "done"})
    assert response.status_code == 200
    assert response.json()["status"] == "done"

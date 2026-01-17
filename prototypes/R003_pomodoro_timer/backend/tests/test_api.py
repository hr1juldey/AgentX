# =============================================================================
# R003 Pomodoro Timer - API Tests
# =============================================================================
# Pytest tests for Pomodoro Timer API endpoints
# =============================================================================

from fastapi.testclient import TestClient

from main import app


def test_root() -> None:
    """Test root endpoint."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert data["app"] == "Pomodoro Timer"
    assert data["websocket"] == "supported"


def test_health() -> None:
    """Test health check endpoint."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_session() -> None:
    """Test creating a Pomodoro session."""
    client = TestClient(app)
    session_data = {
        "title": "Focus Session",
        "work_duration": 25,
        "break_duration": 5,
    }
    response = client.post("/api/v1/sessions", json=session_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Focus Session"
    assert data["status"] == "running"
    assert data["remaining_seconds"] == 1500  # 25 minutes
    assert data["total_seconds"] == 1500
    assert data["work_duration"] == 25
    assert data["break_duration"] == 5
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_session_with_defaults() -> None:
    """Test creating a session with default values."""
    client = TestClient(app)
    session_data = {"title": "Quick Session"}
    response = client.post("/api/v1/sessions", json=session_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Quick Session"
    assert data["work_duration"] == 25  # default
    assert data["break_duration"] == 5  # default
    assert data["status"] == "running"


def test_create_session_with_custom_duration() -> None:
    """Test creating a session with custom duration."""
    client = TestClient(app)
    session_data = {
        "title": "Long Focus",
        "work_duration": 50,
        "break_duration": 10,
    }
    response = client.post("/api/v1/sessions", json=session_data)
    assert response.status_code == 201
    data = response.json()
    assert data["remaining_seconds"] == 3000  # 50 minutes
    assert data["total_seconds"] == 3000


def test_create_session_with_legacy_duration_minutes() -> None:
    """Test creating a session with legacy duration_minutes parameter."""
    client = TestClient(app)
    session_data = {
        "title": "Legacy Session",
        "duration_minutes": 30,
        "work_duration": 25,
        "break_duration": 5,
    }
    response = client.post("/api/v1/sessions", json=session_data)
    assert response.status_code == 201
    data = response.json()
    # duration_minutes should override work_duration
    assert data["remaining_seconds"] == 1800  # 30 minutes
    assert data["total_seconds"] == 1800


def test_get_session() -> None:
    """Test getting a session."""
    client = TestClient(app)
    # First create a session
    create_response = client.post(
        "/api/v1/sessions", json={"title": "Get Test", "work_duration": 25}
    )
    session_id = create_response.json()["id"]
    # Then get it
    response = client.get(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 200
    assert response.json()["id"] == session_id
    assert response.json()["title"] == "Get Test"


def test_list_sessions() -> None:
    """Test listing sessions."""
    client = TestClient(app)
    # Create a few sessions
    client.post("/api/v1/sessions", json={"title": "Session 1", "work_duration": 25})
    client.post("/api/v1/sessions", json={"title": "Session 2", "work_duration": 25})
    # List sessions
    response = client.get("/api/v1/sessions")
    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data
    assert "total" in data
    assert data["total"] >= 2


def test_list_sessions_with_status_filter() -> None:
    """Test listing sessions filtered by status."""
    client = TestClient(app)
    # Create sessions
    response1 = client.post("/api/v1/sessions", json={"title": "Session 1"})
    session_id_1 = response1.json()["id"]

    response2 = client.post("/api/v1/sessions", json={"title": "Session 2"})
    _session_id_2 = response2.json()["id"]

    # Pause one session
    client.put(f"/api/v1/sessions/{session_id_1}", json={"status": "paused"})

    # Filter by status
    response = client.get("/api/v1/sessions?status=paused")
    assert response.status_code == 200
    data = response.json()
    for session in data["sessions"]:
        assert session["status"] == "paused"


def test_update_session_pause() -> None:
    """Test pausing a session."""
    client = TestClient(app)
    # Create a session
    create_response = client.post(
        "/api/v1/sessions", json={"title": "Pause Test", "work_duration": 25}
    )
    session_id = create_response.json()["id"]

    # Pause it
    update_response = client.put(f"/api/v1/sessions/{session_id}", json={"status": "paused"})
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "paused"


def test_update_session_resume() -> None:
    """Test resuming a paused session."""
    client = TestClient(app)
    # Create and pause a session
    create_response = client.post("/api/v1/sessions", json={"title": "Resume Test"})
    session_id = create_response.json()["id"]

    client.put(f"/api/v1/sessions/{session_id}", json={"status": "paused"})

    # Resume it
    update_response = client.put(f"/api/v1/sessions/{session_id}", json={"status": "running"})
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "running"


def test_update_session_cancel() -> None:
    """Test cancelling a session."""
    client = TestClient(app)
    # Create a session
    create_response = client.post("/api/v1/sessions", json={"title": "Cancel Test"})
    session_id = create_response.json()["id"]

    # Cancel it
    update_response = client.put(f"/api/v1/sessions/{session_id}", json={"status": "cancelled"})
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "cancelled"


def test_delete_session() -> None:
    """Test deleting a session."""
    client = TestClient(app)
    # Create a session
    create_response = client.post("/api/v1/sessions", json={"title": "To Delete"})
    session_id = create_response.json()["id"]

    # Delete it
    delete_response = client.delete(f"/api/v1/sessions/{session_id}")
    assert delete_response.status_code == 204

    # Verify it's gone
    get_response = client.get(f"/api/v1/sessions/{session_id}")
    assert get_response.status_code == 404


def test_get_nonexistent_session() -> None:
    """Test getting a non-existent session."""
    client = TestClient(app)
    response = client.get("/api/v1/sessions/99999")
    assert response.status_code == 404


def test_update_nonexistent_session() -> None:
    """Test updating a non-existent session."""
    client = TestClient(app)
    response = client.put("/api/v1/sessions/99999", json={"status": "paused"})
    assert response.status_code == 404


def test_delete_nonexistent_session() -> None:
    """Test deleting a non-existent session."""
    client = TestClient(app)
    response = client.delete("/api/v1/sessions/99999")
    assert response.status_code == 404


def test_create_session_validation() -> None:
    """Test validation when creating a session."""
    client = TestClient(app)

    # Missing title
    response = client.post("/api/v1/sessions", json={})
    assert response.status_code == 422

    # Empty title
    response = client.post("/api/v1/sessions", json={"title": ""})
    assert response.status_code == 422

    # Invalid work_duration (too long)
    response = client.post("/api/v1/sessions", json={"title": "Test", "work_duration": 200})
    assert response.status_code == 422

    # Invalid work_duration (too short)
    response = client.post("/api/v1/sessions", json={"title": "Test", "work_duration": 0})
    assert response.status_code == 422

    # Invalid break_duration (negative)
    response = client.post("/api/v1/sessions", json={"title": "Test", "break_duration": -1})
    assert response.status_code == 422


def test_update_session_remaining_seconds() -> None:
    """Test updating remaining seconds."""
    client = TestClient(app)
    # Create a session
    create_response = client.post("/api/v1/sessions", json={"title": "Adjust Time"})
    session_id = create_response.json()["id"]

    # Update remaining seconds
    update_response = client.put(f"/api/v1/sessions/{session_id}", json={"remaining_seconds": 600})
    assert update_response.status_code == 200
    assert update_response.json()["remaining_seconds"] == 600


def test_session_workflow() -> None:
    """Test complete session workflow: create -> pause -> resume -> complete."""
    client = TestClient(app)

    # Create
    create_response = client.post(
        "/api/v1/sessions", json={"title": "Workflow Test", "work_duration": 25}
    )
    session_id = create_response.json()["id"]
    assert create_response.json()["status"] == "running"

    # Pause
    pause_response = client.put(f"/api/v1/sessions/{session_id}", json={"status": "paused"})
    assert pause_response.json()["status"] == "paused"

    # Resume
    resume_response = client.put(f"/api/v1/sessions/{session_id}", json={"status": "running"})
    assert resume_response.json()["status"] == "running"

    # Complete (manually)
    complete_response = client.put(f"/api/v1/sessions/{session_id}", json={"status": "completed"})
    assert complete_response.json()["status"] == "completed"


def test_websocket_connection_invalid_session() -> None:
    """Test WebSocket connection to non-existent session."""
    # Note: TestClient doesn't fully support WebSocket testing
    # This is a placeholder for proper WebSocket testing
    # In production, use a WebSocket testing library
    _client = TestClient(app)
    pass

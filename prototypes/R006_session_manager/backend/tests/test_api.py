"""API tests for session manager."""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from main import app
from services.service import session_service

client = TestClient(app)

# Test user ID
TEST_USER_ID = "test_user_123"


@pytest.fixture(autouse=True)
def cleanup_sessions():
    """Cleanup sessions before and after each test."""
    # Cleanup before
    import asyncio

    asyncio.run(session_service.delete_all_sessions(TEST_USER_ID))
    yield
    # Cleanup after
    asyncio.run(session_service.delete_all_sessions(TEST_USER_ID))


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Session Manager"
    assert "endpoints" in data


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "storage" in data


def test_create_session():
    """Test creating a new session."""
    session_data = {
        "device_name": "Test Desktop",
        "device_type": "desktop",
        "user_agent": "Mozilla/5.0 Test Browser",
        "ip_address": "192.168.1.100",
    }

    response = client.post(
        "/sessions",
        json=session_data,
        headers={"X-User-Id": TEST_USER_ID},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["device_name"] == "Test Desktop"
    assert data["device_type"] == "desktop"
    assert data["user_id"] == TEST_USER_ID
    assert data["session_token"] is not None
    assert data["id"] is not None
    assert data["is_active"] is True
    assert "created_at" in data
    assert "last_active" in data


def test_list_sessions():
    """Test listing sessions."""
    # Create a session first
    session_data = {
        "device_name": "Test Mobile",
        "device_type": "mobile",
        "user_agent": "Mobile Browser",
    }
    client.post(
        "/sessions",
        json=session_data,
        headers={"X-User-Id": TEST_USER_ID},
    )

    # List sessions
    response = client.get(
        "/sessions",
        headers={"X-User-Id": TEST_USER_ID},
    )

    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data
    assert data["total"] >= 1
    assert data["active"] >= 1
    assert len(data["sessions"]) >= 1


def test_get_session():
    """Test getting a specific session."""
    # Create a session
    session_data = {
        "device_name": "Test Tablet",
        "device_type": "tablet",
    }
    create_response = client.post(
        "/sessions",
        json=session_data,
        headers={"X-User-Id": TEST_USER_ID},
    )
    session_id = create_response.json()["id"]

    # Get the session
    response = client.get(
        f"/sessions/{session_id}",
        headers={"X-User-Id": TEST_USER_ID},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session_id
    assert data["device_name"] == "Test Tablet"


def test_get_session_not_found():
    """Test getting a non-existent session."""
    response = client.get(
        "/sessions/nonexistent_id",
        headers={"X-User-Id": TEST_USER_ID},
    )

    assert response.status_code == 404


def test_update_session():
    """Test updating a session."""
    # Create a session
    session_data = {
        "device_name": "Test Device",
        "device_type": "desktop",
    }
    create_response = client.post(
        "/sessions",
        json=session_data,
        headers={"X-User-Id": TEST_USER_ID},
    )
    session_id = create_response.json()["id"]

    # Update the session (deactivate)
    response = client.put(
        f"/sessions/{session_id}",
        json={"is_active": False},
        headers={"X-User-Id": TEST_USER_ID},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False


def test_delete_session():
    """Test deleting a session."""
    # Create a session
    session_data = {
        "device_name": "Test Device",
        "device_type": "desktop",
    }
    create_response = client.post(
        "/sessions",
        json=session_data,
        headers={"X-User-Id": TEST_USER_ID},
    )
    session_id = create_response.json()["id"]

    # Delete the session
    response = client.delete(
        f"/sessions/{session_id}",
        headers={"X-User-Id": TEST_USER_ID},
    )

    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(
        f"/sessions/{session_id}",
        headers={"X-User-Id": TEST_USER_ID},
    )
    assert get_response.status_code == 404


def test_delete_all_sessions():
    """Test deleting all sessions."""
    # Create multiple sessions
    for i in range(3):
        session_data = {
            "device_name": f"Device {i}",
            "device_type": "desktop",
        }
        client.post(
            "/sessions",
            json=session_data,
            headers={"X-User-Id": TEST_USER_ID},
        )

    # Delete all sessions
    response = client.delete(
        "/sessions",
        headers={"X-User-Id": TEST_USER_ID},
    )

    assert response.status_code == 204

    # Verify all are deleted
    list_response = client.get(
        "/sessions",
        headers={"X-User-Id": TEST_USER_ID},
    )
    assert list_response.json()["total"] == 0


def test_get_storage_status():
    """Test getting storage status."""
    response = client.get("/sessions/status/storage")

    assert response.status_code == 200
    data = response.json()
    assert "storage_type" in data


def test_unauthorized_session_access():
    """Test that users can't access other users' sessions."""
    # Create a session for user1
    session_data = {
        "device_name": "User1 Device",
        "device_type": "desktop",
    }
    create_response = client.post(
        "/sessions",
        json=session_data,
        headers={"X-User-Id": "user1"},
    )
    session_id = create_response.json()["id"]

    # Try to access with user2
    response = client.get(
        f"/sessions/{session_id}",
        headers={"X-User-Id": "user2"},
    )

    assert response.status_code == 403


def test_device_type_enum():
    """Test that only valid device types are accepted."""
    invalid_data = {
        "device_name": "Test Device",
        "device_type": "invalid_type",
    }

    response = client.post(
        "/sessions",
        json=invalid_data,
        headers={"X-User-Id": TEST_USER_ID},
    )

    assert response.status_code == 422  # Validation error


def test_missing_required_fields():
    """Test that required fields are validated."""
    incomplete_data = {
        "device_name": "Test Device",
        # Missing device_type
    }

    response = client.post(
        "/sessions",
        json=incomplete_data,
        headers={"X-User-Id": TEST_USER_ID},
    )

    assert response.status_code == 422  # Validation error

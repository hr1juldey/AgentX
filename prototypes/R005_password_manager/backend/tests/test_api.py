"""API tests for Password Manager."""

import pytest
from fastapi.testclient import TestClient

from main import app
from services.service import users_db, password_entries_db


# Reset databases before each test
@pytest.fixture(autouse=True)
def reset_db():
    """Reset in-memory databases before each test."""
    global users_db, password_entries_db, user_id_counter, entry_id_counter
    users_db.clear()
    password_entries_db.clear()
    user_id_counter = 0
    entry_id_counter = 0
    yield


# Test client
@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestAuth:
    """Tests for authentication endpoints."""

    def test_register_user(self, client):
        """Test user registration."""
        response = client.post(
            "/auth/register",
            json={"username": "testuser", "password": "testpass123"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert "id" in data
        assert "created_at" in data

    def test_register_duplicate_username(self, client):
        """Test registering with duplicate username."""
        client.post(
            "/auth/register",
            json={"username": "testuser", "password": "testpass123"},
        )
        response = client.post(
            "/auth/register",
            json={"username": "testuser", "password": "differentpass"},
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_register_short_password(self, client):
        """Test registration with short password."""
        response = client.post(
            "/auth/register",
            json={"username": "testuser", "password": "short"},
        )
        assert response.status_code == 422  # Validation error

    def test_login_success(self, client):
        """Test successful login."""
        # Register first
        client.post(
            "/auth/register",
            json={"username": "testuser", "password": "testpass123"},
        )
        # Login
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "testpass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "testuser"

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post(
            "/auth/login",
            json={"username": "nonexistent", "password": "wrongpass"},
        )
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]


class TestPasswordEntries:
    """Tests for password entry endpoints."""

    @pytest.fixture
    def auth_headers(self, client):
        """Create a user and return auth headers."""
        # Register and login
        client.post(
            "/auth/register",
            json={"username": "testuser", "password": "testpass123"},
        )
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "testpass123"},
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_create_password_entry(self, client, auth_headers):
        """Test creating a password entry."""
        response = client.post(
            "/passwords",
            json={
                "title": "Gmail",
                "username": "user@gmail.com",
                "password": "gmailpass123",
                "url": "https://gmail.com",
                "notes": "Personal email",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Gmail"
        assert data["username"] == "user@gmail.com"
        assert data["password"] != "gmailpass123"  # Should be encrypted
        assert data["url"] == "https://gmail.com"
        assert data["notes"] == "Personal email"
        assert "id" in data

    def test_list_passwords(self, client, auth_headers):
        """Test listing password entries."""
        # Create a few entries
        client.post(
            "/passwords",
            json={
                "title": "Gmail",
                "username": "user@gmail.com",
                "password": "pass123",
            },
            headers=auth_headers,
        )
        client.post(
            "/passwords",
            json={
                "title": "Facebook",
                "username": "user@fb.com",
                "password": "pass456",
            },
            headers=auth_headers,
        )

        response = client.get("/passwords", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(entry["password"] == "[HIDDEN]" for entry in data)

    def test_get_password_entry(self, client, auth_headers):
        """Test getting a specific password entry."""
        # Create an entry
        create_response = client.post(
            "/passwords",
            json={
                "title": "Gmail",
                "username": "user@gmail.com",
                "password": "gmailpass123",
            },
            headers=auth_headers,
        )
        entry_id = create_response.json()["id"]

        # Get the entry
        response = client.get(f"/passwords/{entry_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Gmail"
        # Password should be decrypted
        assert data["password"] == "gmailpass123"

    def test_update_password_entry(self, client, auth_headers):
        """Test updating a password entry."""
        # Create an entry
        create_response = client.post(
            "/passwords",
            json={
                "title": "Gmail",
                "username": "user@gmail.com",
                "password": "oldpass",
            },
            headers=auth_headers,
        )
        entry_id = create_response.json()["id"]

        # Update the entry
        response = client.put(
            f"/passwords/{entry_id}",
            json={"title": "Gmail Updated", "password": "newpass"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Gmail Updated"
        assert data["password"] == "newpass"

    def test_delete_password_entry(self, client, auth_headers):
        """Test deleting a password entry."""
        # Create an entry
        create_response = client.post(
            "/passwords",
            json={
                "title": "Gmail",
                "username": "user@gmail.com",
                "password": "pass123",
            },
            headers=auth_headers,
        )
        entry_id = create_response.json()["id"]

        # Delete the entry
        response = client.delete(f"/passwords/{entry_id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify it's deleted
        response = client.get(f"/passwords/{entry_id}", headers=auth_headers)
        assert response.status_code == 404

    def test_unauthorized_access(self, client):
        """Test accessing passwords without authentication."""
        response = client.get("/passwords")
        assert response.status_code == 401

    def test_access_other_user_entries(self, client):
        """Test that users can only access their own entries."""
        # Create first user and entry
        client.post(
            "/auth/register",
            json={"username": "user1", "password": "pass123"},
        )
        login1 = client.post(
            "/auth/login",
            json={"username": "user1", "password": "pass123"},
        )
        token1 = login1.json()["access_token"]

        create_response = client.post(
            "/passwords",
            json={
                "title": "Secret",
                "username": "user1",
                "password": "secret123",
            },
            headers={"Authorization": f"Bearer {token1}"},
        )
        entry_id = create_response.json()["id"]

        # Create second user
        client.post(
            "/auth/register",
            json={"username": "user2", "password": "pass456"},
        )
        login2 = client.post(
            "/auth/login",
            json={"username": "user2", "password": "pass456"},
        )
        token2 = login2.json()["access_token"]

        # Try to access first user's entry with second user's token
        response = client.get(
            f"/passwords/{entry_id}",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert response.status_code == 404


class TestRootEndpoints:
    """Tests for root and health endpoints."""

    def test_root(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "app" in data
        assert "endpoints" in data

    def test_health(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

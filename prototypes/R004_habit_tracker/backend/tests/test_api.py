# =============================================================================
# R004 Habit Tracker - API Tests
# =============================================================================
# Tests for Habit Tracker API endpoints
# =============================================================================

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def test_habit(client):
    """Create a test habit and return its ID."""
    response = client.post(
        "/api/v1/habits",
        json={
            "name": "Exercise",
            "description": "Daily workout",
            "frequency": "daily",
            "target_count": 1,
        },
    )
    return response.json()


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_root(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["app"] == "Habit Tracker"
        assert data["status"] == "running"

    def test_health(self, client):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestHabitEndpoints:
    """Tests for habit CRUD endpoints."""

    def test_create_habit(self, client):
        """Test creating a new habit."""
        response = client.post(
            "/api/v1/habits",
            json={
                "name": "Read Book",
                "description": "Read for 30 minutes",
                "frequency": "daily",
                "target_count": 1,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Read Book"
        assert data["frequency"] == "daily"
        assert data["streak_count"] == 0
        assert data["total_completions"] == 0
        assert "id" in data
        assert "created_at" in data

    def test_create_habit_minimal(self, client):
        """Test creating a habit with minimal data."""
        response = client.post(
            "/api/v1/habits",
            json={"name": "Meditate"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Meditate"
        assert data["frequency"] == "daily"  # Default
        assert data["target_count"] == 1  # Default

    def test_list_habits_empty(self, client):
        """Test listing habits when empty."""
        response = client.get("/api/v1/habits")
        assert response.status_code == 200
        data = response.json()
        assert data["habits"] == []
        assert data["total"] == 0

    def test_list_habits(self, client):
        """Test listing habits."""
        # Create multiple habits
        client.post("/api/v1/habits", json={"name": "Habit 1"})
        client.post("/api/v1/habits", json={"name": "Habit 2"})

        response = client.get("/api/v1/habits")
        assert response.status_code == 200
        data = response.json()
        assert len(data["habits"]) == 2
        assert data["total"] == 2

    def test_get_habit(self, client, test_habit):
        """Test getting a specific habit."""
        habit_id = test_habit["id"]
        response = client.get(f"/api/v1/habits/{habit_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == habit_id
        assert data["name"] == "Exercise"
        assert "completions" in data
        assert "streak_data" in data

    def test_get_habit_not_found(self, client):
        """Test getting a non-existent habit."""
        response = client.get("/api/v1/habits/99999")
        assert response.status_code == 404

    def test_delete_habit(self, client, test_habit):
        """Test deleting a habit."""
        habit_id = test_habit["id"]
        response = client.delete(f"/api/v1/habits/{habit_id}")
        assert response.status_code == 204

        # Verify it's deleted
        response = client.get(f"/api/v1/habits/{habit_id}")
        assert response.status_code == 404

    def test_delete_habit_not_found(self, client):
        """Test deleting a non-existent habit."""
        response = client.delete("/api/v1/habits/99999")
        assert response.status_code == 404


class TestCompletionEndpoints:
    """Tests for habit completion endpoints."""

    def test_record_completion(self, client, test_habit):
        """Test recording a habit completion."""
        habit_id = test_habit["id"]
        response = client.post(
            f"/api/v1/habits/{habit_id}/completions",
            json={
                "notes": "Great session!",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["habit_id"] == habit_id
        assert data["notes"] == "Great session!"
        assert "id" in data
        assert "completed_at" in data

    def test_record_completion_with_custom_time(self, client, test_habit):
        """Test recording a completion with custom time."""
        habit_id = test_habit["id"]
        custom_time = (datetime.now(UTC) - timedelta(hours=2)).isoformat()
        response = client.post(
            f"/api/v1/habits/{habit_id}/completions",
            json={
                "completed_at": custom_time,
            },
        )
        assert response.status_code == 201

    def test_record_completion_invalid_habit(self, client):
        """Test recording a completion for non-existent habit."""
        response = client.post(
            "/api/v1/habits/99999/completions",
            json={},
        )
        assert response.status_code == 404

    def test_get_completions(self, client, test_habit):
        """Test getting completions for a habit."""
        habit_id = test_habit["id"]

        # Record some completions
        client.post(f"/api/v1/habits/{habit_id}/completions", json={})
        client.post(f"/api/v1/habits/{habit_id}/completions", json={})

        response = client.get(f"/api/v1/habits/{habit_id}/completions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_completions_invalid_habit(self, client):
        """Test getting completions for non-existent habit."""
        response = client.get("/api/v1/habits/99999/completions")
        assert response.status_code == 404


class TestStreakEndpoints:
    """Tests for streak tracking endpoints."""

    def test_get_streak_new_habit(self, client, test_habit):
        """Test streak data for a new habit (no completions)."""
        habit_id = test_habit["id"]
        response = client.get(f"/api/v1/habits/{habit_id}/streak")
        assert response.status_code == 200
        data = response.json()
        assert data["current_streak"] == 0
        assert data["longest_streak"] == 0
        assert data["last_completion_date"] is None

    def test_get_streak_with_completions(self, client, test_habit):
        """Test streak data after recording completions."""
        habit_id = test_habit["id"]

        # Record a completion
        client.post(f"/api/v1/habits/{habit_id}/completions", json={})

        response = client.get(f"/api/v1/habits/{habit_id}/streak")
        assert response.status_code == 200
        data = response.json()
        assert data["current_streak"] >= 1
        assert data["last_completion_date"] is not None

    def test_get_streak_invalid_habit(self, client):
        """Test getting streak for non-existent habit."""
        response = client.get("/api/v1/habits/99999/streak")
        assert response.status_code == 404


class TestTimeSeriesEndpoints:
    """Tests for time-series aggregation endpoints."""

    def test_get_timeseries_default(self, client, test_habit):
        """Test getting time-series data with default parameters."""
        habit_id = test_habit["id"]
        response = client.get(f"/api/v1/habits/{habit_id}/timeseries")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 30  # Default 30 days
        # Each entry should have date and count
        assert all("date" in entry and "count" in entry for entry in data)

    def test_get_timeseries_custom_days(self, client, test_habit):
        """Test getting time-series data with custom day count."""
        habit_id = test_habit["id"]
        response = client.get(f"/api/v1/habits/{habit_id}/timeseries?days=7")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 7

    def test_get_timeseries_with_completions(self, client, test_habit):
        """Test time-series data reflects completions."""
        habit_id = test_habit["id"]

        # Record a completion today
        client.post(f"/api/v1/habits/{habit_id}/completions", json={})

        response = client.get(f"/api/v1/habits/{habit_id}/timeseries?days=7")
        assert response.status_code == 200
        data = response.json()

        # Today's entry should have count > 0
        today = data[-1]  # Last entry is today
        assert today["count"] >= 1

    def test_get_timeseries_invalid_habit(self, client):
        """Test getting time-series for non-existent habit."""
        response = client.get("/api/v1/habits/99999/timeseries")
        assert response.status_code == 404

    def test_get_timeseries_invalid_days(self, client, test_habit):
        """Test time-series with invalid day parameter."""
        habit_id = test_habit["id"]
        response = client.get(f"/api/v1/habits/{habit_id}/timeseries?days=500")
        assert response.status_code == 422  # Validation error

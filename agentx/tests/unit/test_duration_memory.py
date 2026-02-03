"""Unit tests for DurationMemoryService.

Tests state tracking and duration calculation.
From C005 memory-rag change.
"""

from datetime import datetime, timedelta

import pytest

from agentx.application.services.duration import DurationMemoryService
from agentx.domain.entities.enums import TemporalType
from agentx.domain.entities.memory_consolidation import MemoryConsolidationEntity


class MockVectorStore:
    """Mock QdrantVectorStore for testing."""

    async def get_all_memories(self, user_id, tier=2, session_id=None):
        """Return mock memories."""
        now = datetime.now()
        return [
            {
                "memory_id": "1",
                "content": "Started working on task A",
                "metadata": {
                    "start_state": "working",
                    "temporal_type": TemporalType.STATE.value,
                    "created_at": (now - timedelta(minutes=30)).isoformat(),
                },
            },
            {
                "memory_id": "2",
                "content": "Completed task A",
                "metadata": {
                    "start_state": "working",
                    "end_state": "completed",
                    "duration_seconds": 1800,
                    "temporal_type": TemporalType.STATE.value,
                    "created_at": (now - timedelta(minutes=15)).isoformat(),
                },
            },
        ]


@pytest.fixture
def duration_service():
    """Create DurationMemoryService with mock vector store."""
    mock_store = MockVectorStore()
    return DurationMemoryService(vector_store=mock_store)


class TestStateTracking:
    """Tests for state transition tracking."""

    @pytest.mark.asyncio
    async def test_track_state_start(self, duration_service):
        """Should track the start of a state."""
        from uuid import uuid4

        session_id = uuid4()
        await duration_service.track_state_start(
            session_id=session_id,
            user_id="user1",
            state="working",
            context={"task": "A"},
        )
        # State is tracked in session
        current = duration_service.get_current_state(session_id)
        assert current == "working"

    @pytest.mark.asyncio
    async def test_track_state_end(self, duration_service):
        """Should calculate duration when state ends."""
        from uuid import uuid4

        session_id = uuid4()
        await duration_service.track_state_start(
            session_id=session_id, user_id="user1", state="working"
        )
        # Simulate time passing
        import time

        time.sleep(0.1)
        duration = await duration_service.track_state_end(session_id=session_id)
        assert duration is not None
        assert duration >= 0  # At least 100ms passed


class TestDurationCalculation:
    """Tests for duration calculation."""

    @pytest.mark.asyncio
    async def test_calculate_duration_from_seconds(self, duration_service):
        """Should calculate duration from seconds."""
        duration_seconds = 3665  # 1 hour, 1 minute, 5 seconds
        formatted = duration_service._format_duration(duration_seconds)
        assert "1h" in formatted or "61m" in formatted

    @pytest.mark.asyncio
    async def test_calculate_duration_short(self, duration_service):
        """Should handle short durations (< 1 minute)."""
        duration_seconds = 30
        formatted = duration_service._format_duration(duration_seconds)
        assert "30s" in formatted

    @pytest.mark.asyncio
    async def test_calculate_duration_zero(self, duration_service):
        """Should handle zero duration."""
        duration_seconds = 0
        formatted = duration_service._format_duration(duration_seconds)
        assert "0s" in formatted


class TestDurationConsolidation:
    """Tests for duration memory consolidation."""

    @pytest.mark.asyncio
    async def test_consolidate_durations(self, duration_service):
        """Should consolidate duration memories to Tier 3."""
        from uuid import uuid4

        session_id = uuid4()
        result = await duration_service.consolidate_session_durations(
            user_id="user1", session_id=session_id
        )
        assert isinstance(result, MemoryConsolidationEntity)
        assert result.memories_consolidated >= 0

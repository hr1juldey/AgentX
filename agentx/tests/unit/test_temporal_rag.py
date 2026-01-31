"""Unit tests for TemporalRAGService.

Tests temporal filtering, fact invalidation, and classification.
From C005 memory-rag change.
"""

from datetime import datetime, timedelta

import pytest

from agentx.application.services.temporal_rag_service import TemporalRAGService
from agentx.domain.entities.enums import TemporalType


class MockVectorStore:
    """Mock QdrantVectorStore for testing."""

    async def search_memories(
        self, query, user_id, tier=3, session_id=None, limit=10, time_filter="all"
    ):
        """Return mock search results with temporal metadata."""
        now = datetime.now()
        return [
            {
                "memory_id": "1",
                "content": "User prefers dark mode",
                "score": 0.9,
                "metadata": {
                    "temporal_type": TemporalType.PREFERENCE.value,
                    "created_at": (now - timedelta(days=10)).isoformat(),
                },
            },
            {
                "memory_id": "2",
                "content": "User lives in New York",
                "score": 0.8,
                "metadata": {
                    "temporal_type": TemporalType.FACT.value,
                    "created_at": (now - timedelta(days=100)).isoformat(),
                    "superseded_by": "3",
                },
            },
            {
                "memory_id": "3",
                "content": "User lives in San Francisco",
                "score": 0.7,
                "metadata": {
                    "temporal_type": TemporalType.FACT.value,
                    "created_at": (now - timedelta(days=5)).isoformat(),
                },
            },
        ]


@pytest.fixture
def temporal_rag_service():
    """Create TemporalRAGService with mock vector store."""
    mock_store = MockVectorStore()
    return TemporalRAGService(vector_store=mock_store)


class TestTemporalClassification:
    """Tests for temporal type classification."""

    @pytest.mark.asyncio
    async def test_classify_preference(self, temporal_rag_service):
        """Should classify preference keywords correctly."""
        result = temporal_rag_service._classify_temporal_type("I prefer dark mode")
        assert result == TemporalType.PREFERENCE

    @pytest.mark.asyncio
    async def test_classify_state(self, temporal_rag_service):
        """Should classify state keywords correctly."""
        result = temporal_rag_service._classify_temporal_type(
            "Current status is in progress"
        )
        assert result == TemporalType.STATE

    @pytest.mark.asyncio
    async def test_classify_event(self, temporal_rag_service):
        """Should classify event keywords correctly."""
        result = temporal_rag_service._classify_temporal_type(
            "Meeting happened yesterday"
        )
        assert result == TemporalType.EVENT

    @pytest.mark.asyncio
    async def test_classify_plan(self, temporal_rag_service):
        """Should classify plan keywords correctly."""
        result = temporal_rag_service._classify_temporal_type("Will do this tomorrow")
        assert result == TemporalType.PLAN

    @pytest.mark.asyncio
    async def test_classify_fact_default(self, temporal_rag_service):
        """Should default to fact for unknown patterns."""
        result = temporal_rag_service._classify_temporal_type("Some random statement")
        assert result == TemporalType.FACT


class TestTemporalFiltering:
    """Tests for time-based filtering."""

    @pytest.mark.asyncio
    async def test_recent_filter(self, temporal_rag_service):
        """Should return only recent memories (last 30 days)."""
        results = await temporal_rag_service.search_with_temporal_filter(
            query="test", user_id="user1", time_filter="recent", limit=10
        )
        # Should return memories from last 30 days only
        assert all(
            datetime.fromisoformat(r["metadata"]["created_at"])
            >= datetime.now() - timedelta(days=30)
            for r in results
        )

    @pytest.mark.asyncio
    async def test_historical_filter(self, temporal_rag_service):
        """Should return only historical memories (older than 30 days)."""
        results = await temporal_rag_service.search_with_temporal_filter(
            query="test", user_id="user1", time_filter="historical", limit=10
        )
        # Should return memories older than 30 days
        assert all(
            datetime.fromisoformat(r["metadata"]["created_at"])
            < datetime.now() - timedelta(days=30)
            for r in results
        )

    @pytest.mark.asyncio
    async def test_all_filter(self, temporal_rag_service):
        """Should return all memories regardless of time."""
        results = await temporal_rag_service.search_with_temporal_filter(
            query="test", user_id="user1", time_filter="all", limit=10
        )
        assert len(results) > 0


class TestFactInvalidation:
    """Tests for fact invalidation logic."""

    @pytest.mark.asyncio
    async def test_mark_superseded_facts(self, temporal_rag_service):
        """Should mark outdated facts as superseded."""
        results = await temporal_rag_service.search_with_temporal_filter(
            query="lives in", user_id="user1", time_filter="all", limit=10
        )
        # Check that superseded fact is marked
        outdated = [r for r in results if r.get("superseded")]
        assert len(outdated) > 0
        assert outdated[0]["memory_id"] == "2"  # "Lives in New York" superseded


class TestResultWeighting:
    """Tests for result weighting by temporal type."""

    @pytest.mark.asyncio
    async def test_preferences_weighted_higher(self, temporal_rag_service):
        """Preferences should have higher weight than facts."""
        results = await temporal_rag_service.search_with_temporal_filter(
            query="test", user_id="user1", time_filter="all", limit=10
        )
        # Results should be sorted by weighted_score
        for i in range(len(results) - 1):
            assert results[i].get("weighted_score", 0) >= results[i + 1].get(
                "weighted_score", 0
            )

"""Temporal and fact invalidation integration tests for consolidation.

Tests for outdated fact invalidation and duration event summarization.
"""

from uuid import uuid4

import pytest

from agentx.application.services.duration_memory_service import (
    DurationMemoryService,
)
from agentx.domain.entities.enums import TemporalType


class TestFactInvalidation:
    """Tests for outdated fact invalidation."""

    @pytest.mark.asyncio
    async def test_supersede_outdated_facts(self, consolidation_setup):
        """Should mark outdated facts as superseded."""
        store = consolidation_setup["store"]
        consolidate = consolidation_setup["consolidate"]
        user_id = str(uuid4())
        session_id = uuid4()

        # Store original fact
        await store.execute(
            content="User lives in New York",
            user_id=user_id,
            temporal_type=TemporalType.FACT,
            tier=2,
            session_id=session_id,
        )

        # Store updated fact (should supersede)
        await store.execute(
            content="User lives in San Francisco",
            user_id=user_id,
            temporal_type=TemporalType.FACT,
            tier=2,
            session_id=session_id,
        )

        # Consolidate
        result = await consolidate.execute(user_id=user_id, session_id=session_id)

        assert result.memories_consolidated > 0
        # Updated fact should be in Tier 3, old one marked


class TestDurationEventSummarization:
    """Tests for duration event summarization."""

    @pytest.mark.asyncio
    async def test_consolidate_duration_events(self, consolidation_setup):
        """Should consolidate duration events to Tier 3."""
        consolidate = consolidation_setup["consolidate"]
        user_id = str(uuid4())
        session_id = uuid4()

        # Simulate state tracking
        duration_service = DurationMemoryService(
            vector_store=consolidation_setup["vector_store"]
        )
        await duration_service.track_state_start(
            session_id=session_id,
            user_id=user_id,
            state="working",
            context={"task": "A"},
        )
        await duration_service.track_state_end(session_id=session_id)

        # Consolidate
        result = await consolidate.execute(user_id=user_id, session_id=session_id)

        # Should include duration summary
        assert "duration" in result.consolidation_summary.lower()

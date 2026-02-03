"""Tier Resolver Module for RAG Conflict Resolution.

Implements the 4-tier conflict resolution strategy:
1. Temporal Priority - Newest wins same topic
2. Confidence Score - Highest >= 0.7 wins
3. Source Authority - academic > report > general > social
4. LLM Fallback - DSPy synthesis (handled by main service)
"""

from datetime import timedelta

from agentx.core.config import get_settings
from agentx.domain.entities.memory_record import MemoryRecord, SourceType

settings = get_settings()


class TierResolver:
    """Resolves conflicts using a 4-tier strategy.

    Tiers are tried in order:
    1. Temporal Priority (newest same-topic wins)
    2. Confidence Score (highest >= 0.7 wins)
    3. Source Authority (academic > report > general > social)
    4. LLM Fallback (handled by caller - requires DSPy)
    """

    # Source authority ranking (higher = more authoritative)
    SOURCE_AUTHORITY_RANK: dict[SourceType, int] = {
        SourceType.ACADEMIC: 4,
        SourceType.REPORT: 3,
        SourceType.GENERAL: 2,
        SourceType.SOCIAL: 1,
        SourceType.UNKNOWN: 0,
    }

    def tier1_temporal_priority(
        self, memories: list[MemoryRecord], temporal_window_days: int
    ) -> MemoryRecord | None:
        """Tier 1: Temporal Priority - newest wins if same topic within window.

        Args:
            memories: List of conflicting memories
            temporal_window_days: Days for "same topic" detection

        Returns:
            Newest memory if within temporal window, None otherwise
        """
        if not memories:
            return None

        # Sort by creation date (newest first)
        sorted_by_date = sorted(memories, key=lambda m: m.created_at, reverse=True)

        newest = sorted_by_date[0]
        cutoff_date = newest.created_at - timedelta(days=temporal_window_days)

        # Check if all memories are within temporal window of newest
        all_within_window = all(m.created_at >= cutoff_date for m in memories)

        if all_within_window:
            return newest

        return None

    def tier2_confidence_score(
        self, memories: list[MemoryRecord]
    ) -> MemoryRecord | None:
        """Tier 2: Confidence Score - highest score >= 0.7 wins.

        Args:
            memories: List of conflicting memories

        Returns:
            Memory with highest confidence if >= 0.7, None otherwise
        """
        if not memories:
            return None

        # Find highest confidence score
        best_memory = max(memories, key=lambda m: m.confidence_score)

        if best_memory.confidence_score >= settings.memory.high_quality_threshold:
            return best_memory

        return None

    def tier3_source_authority(
        self, memories: list[MemoryRecord]
    ) -> MemoryRecord | None:
        """Tier 3: Source Authority - academic > report > general > social.

        Args:
            memories: List of conflicting memories

        Returns:
            Memory with highest source authority, None if all equal
        """
        if not memories:
            return None

        # Sort by source authority rank (highest first)
        sorted_by_authority = sorted(
            memories,
            key=lambda m: self.SOURCE_AUTHORITY_RANK.get(m.source_type, 0),
            reverse=True,
        )

        best = sorted_by_authority[0]
        best_rank = self.SOURCE_AUTHORITY_RANK.get(best.source_type, 0)

        # Check if there's a clear winner (not all same rank)
        if all(
            self.SOURCE_AUTHORITY_RANK.get(m.source_type, 0) == best_rank
            for m in memories
        ):
            return None  # All same rank, cannot decide

        return best


__all__ = ["TierResolver"]

"""RAG Conflict Resolution Service (Main Orchestrator).

Implements a 4-tier strategy for resolving conflicts between
multiple retrieved memories with potentially contradictory information.

Delegates to:
- ConflictDetector for conflict detection
- TierResolver for tiers 1-3
- LLMFallbackSynthesizer for tier 4 (LLM fallback)
"""

from agentx.application.services.rag_conflict.conflict_detector import (
    ConflictDetector,
)
from agentx.application.services.rag_conflict.llm_fallback_synthesizer import (
    LLMFallbackSynthesizer,
)
from agentx.application.services.rag_conflict.models import ConflictResolutionResult
from agentx.application.services.rag_conflict.tier_resolver import TierResolver
from agentx.domain.entities.memory_record import MemoryRecord


class RAGConflictResolver:
    """Service for resolving conflicts between multiple retrieved memories.

    Uses a 4-tier strategy to intelligently resolve contradictions:
    1. Temporal Priority (newest same-topic wins)
    2. Confidence Score (highest >= 0.7 wins)
    3. Source Authority (academic > report > general > social)
    4. LLM Fallback (DSPy synthesis)
    """

    def __init__(self) -> None:
        """Initialize the conflict resolution service."""
        self.detector = ConflictDetector()
        self.tier_resolver = TierResolver()
        self.llm_synthesizer = LLMFallbackSynthesizer()

    async def resolve_conflicts(
        self,
        memories: list[MemoryRecord],
        query: str = "",
        temporal_window_days: int = 30,
    ) -> ConflictResolutionResult:
        """Resolve conflicts between multiple memories using 4-tier strategy.

        Args:
            memories: List of potentially conflicting memories
            query: Original query for context (optional)
            temporal_window_days: Days for "same topic" detection (default: 30)

        Returns:
            ConflictResolutionResult with resolved memory and metadata
        """
        if not memories:
            return ConflictResolutionResult(
                resolved_memory=None,
                conflicts_detected=0,
                conflicts_resolved=0,
                llm_fallback_used=False,
                resolution_tier="none",
                reasoning="No memories provided",
            )

        if len(memories) == 1:
            return ConflictResolutionResult(
                resolved_memory=memories[0],
                conflicts_detected=0,
                conflicts_resolved=0,
                llm_fallback_used=False,
                resolution_tier="single",
                reasoning="Only one memory, no conflicts",
            )

        # Detect conflicts by comparing outputs
        conflicts = self.detector.detect_conflicts(memories)

        if not conflicts:
            # No conflicts detected, return highest quality memory
            best_memory = max(memories, key=lambda m: m.quality_score)
            return ConflictResolutionResult(
                resolved_memory=best_memory,
                conflicts_detected=0,
                conflicts_resolved=0,
                llm_fallback_used=False,
                resolution_tier="no_conflict",
                reasoning="No conflicts detected, using highest quality memory",
            )

        # Try Tier 1: Temporal Priority
        tier1_result = self.tier_resolver.tier1_temporal_priority(
            memories, temporal_window_days
        )
        if tier1_result:
            return ConflictResolutionResult(
                resolved_memory=tier1_result,
                conflicts_detected=len(conflicts),
                conflicts_resolved=len(conflicts),
                llm_fallback_used=False,
                resolution_tier="tier1_temporal",
                reasoning="Newest memory within temporal window wins",
            )

        # Try Tier 2: Confidence Score
        tier2_result = self.tier_resolver.tier2_confidence_score(memories)
        if tier2_result:
            return ConflictResolutionResult(
                resolved_memory=tier2_result,
                conflicts_detected=len(conflicts),
                conflicts_resolved=len(conflicts),
                llm_fallback_used=False,
                resolution_tier="tier2_confidence",
                reasoning="Highest confidence score (>= 0.7) wins",
            )

        # Try Tier 3: Source Authority
        tier3_result = self.tier_resolver.tier3_source_authority(memories)
        if tier3_result:
            return ConflictResolutionResult(
                resolved_memory=tier3_result,
                conflicts_detected=len(conflicts),
                conflicts_resolved=len(conflicts),
                llm_fallback_used=False,
                resolution_tier="tier3_authority",
                reasoning="Highest source authority wins",
            )

        # Tier 4: LLM Fallback (DSPy synthesis)
        return await self.llm_synthesizer.synthesize(memories, query, conflicts)


__all__ = [
    "RAGConflictResolver",
    "ConflictResolutionResult",
]

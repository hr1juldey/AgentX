"""RAG Conflict Resolution Service.

Implements a 4-tier strategy for resolving conflicts between
multiple retrieved memories with potentially contradictory information.

Tiers:
1. Temporal Priority - Newest wins same topic (30 days)
2. Confidence Score - Highest >= 0.7 wins
3. Source Authority - academic > report > general > social
4. LLM Fallback - DSPy synthesis when all else fails
"""

import json
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

import dspy

from agentx.agent.dspy_signatures.synthesis_signatures import (
    MultiSourceSynthesisSignature,
)
from agentx.domain.entities.memory_record import MemoryRecord, SourceType


@dataclass
class ConflictResolutionResult:
    """Result of conflict resolution process."""

    resolved_memory: Optional[MemoryRecord] = None
    conflicts_detected: int = 0
    conflicts_resolved: int = 0
    llm_fallback_used: bool = False
    resolution_tier: str = "none"
    reasoning: str = ""


class RAGConflictResolutionService:
    """Service for resolving conflicts between multiple retrieved memories.

    Uses a 4-tier strategy to intelligently resolve contradictions:
    1. Temporal Priority (newest same-topic wins)
    2. Confidence Score (highest >= 0.7 wins)
    3. Source Authority (academic > report > general > social)
    4. LLM Fallback (DSPy synthesis)
    """

    # Source authority ranking (higher = more authoritative)
    SOURCE_AUTHORITY_RANK: dict[SourceType, int] = {
        SourceType.ACADEMIC: 4,
        SourceType.REPORT: 3,
        SourceType.GENERAL: 2,
        SourceType.SOCIAL: 1,
        SourceType.UNKNOWN: 0,
    }

    def __init__(self) -> None:
        """Initialize the conflict resolution service."""
        self.synthesizer = dspy.ChainOfThought(MultiSourceSynthesisSignature)

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
        conflicts = self._detect_conflicts(memories)

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
        tier1_result = self._tier1_temporal_priority(memories, temporal_window_days)
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
        tier2_result = self._tier2_confidence_score(memories)
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
        tier3_result = self._tier3_source_authority(memories)
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
        return await self._tier4_llm_fallback(memories, query, conflicts)

    def _detect_conflicts(
        self, memories: list[MemoryRecord]
    ) -> list[tuple[MemoryRecord, MemoryRecord]]:
        """Detect conflicts between memories by comparing outputs.

        Simple heuristic: different outputs about similar data_input = potential conflict.
        """
        conflicts: list[tuple[MemoryRecord, MemoryRecord]] = []

        for i, mem1 in enumerate(memories):
            for mem2 in memories[i + 1 :]:
                # Check if memories are about similar topics
                if self._similar_topics(mem1, mem2):
                    # Check if outputs differ significantly
                    if self._outputs_differ(mem1.output_produced, mem2.output_produced):
                        conflicts.append((mem1, mem2))

        return conflicts

    def _similar_topics(self, mem1: MemoryRecord, mem2: MemoryRecord) -> bool:
        """Check if two memories are about similar topics.

        Simple heuristic: similar data_input or instruction_input.
        """
        # Check for exact matches in input fields
        if (
            mem1.data_input.strip().lower() == mem2.data_input.strip().lower()
            or mem1.instruction_input.strip().lower()
            == mem2.instruction_input.strip().lower()
        ):
            return True

        # Simple word overlap heuristic (can be enhanced with embeddings)
        words1 = set(mem1.data_input.lower().split())
        words2 = set(mem2.data_input.lower().split())
        overlap = len(words1 & words2) / max(len(words1), len(words2), 1)
        return overlap > 0.3

    def _outputs_differ(self, output1: str, output2: str) -> bool:
        """Check if two outputs differ significantly."""
        # Simple heuristic: outputs are not identical
        return output1.strip().lower() != output2.strip().lower()

    def _tier1_temporal_priority(
        self, memories: list[MemoryRecord], temporal_window_days: int
    ) -> Optional[MemoryRecord]:
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

    def _tier2_confidence_score(
        self, memories: list[MemoryRecord]
    ) -> Optional[MemoryRecord]:
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

        if best_memory.confidence_score >= 0.7:
            return best_memory

        return None

    def _tier3_source_authority(
        self, memories: list[MemoryRecord]
    ) -> Optional[MemoryRecord]:
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

    async def _tier4_llm_fallback(
        self,
        memories: list[MemoryRecord],
        query: str,
        conflicts: list[tuple[MemoryRecord, MemoryRecord]],
    ) -> ConflictResolutionResult:
        """Tier 4: LLM Fallback - use DSPy to synthesize resolution.

        Args:
            memories: List of conflicting memories
            query: Original query for context
            conflicts: List of detected conflict pairs

        Returns:
            ConflictResolutionResult with LLM-generated resolution
        """
        # Format sources for DSPy
        sources_list = [
            {
                "content": m.output_produced,
                "reasoning": m.reasoning_done,
                "source_type": m.source_type.value,
                "confidence": m.confidence_score,
                "quality": m.quality_score,
            }
            for m in memories
        ]

        sources_json = json.dumps(sources_list, indent=2)

        # Run DSPy synthesis (ChainOfThought is not async, returns Prediction)
        query_text = query or "Resolve conflicts between these information sources"
        result = self.synthesizer(query=query_text, sources=sources_json)

        # Create a synthetic memory record from LLM output
        resolved_memory = MemoryRecord(
            user_id=memories[0].user_id,
            session_id=memories[0].session_id,
            memory_type=memories[0].memory_type,
            data_input=memories[0].data_input,
            instruction_input=memories[0].instruction_input,
            reasoning_done=f"LLM conflict resolution: {result.reasoning}",  # type: ignore[attr-defined]
            output_produced=result.unified_answer,  # type: ignore[attr-defined]
            quality_score=0.8,  # Default quality for LLM-resolved
            source_type=SourceType.UNKNOWN,
            confidence_score=0.7,  # Default confidence for LLM-resolved
        )

        return ConflictResolutionResult(
            resolved_memory=resolved_memory,
            conflicts_detected=len(conflicts),
            conflicts_resolved=len(conflicts),
            llm_fallback_used=True,
            resolution_tier="tier4_llm_fallback",
            reasoning=f"LLM synthesis: {result.reasoning}",  # type: ignore[attr-defined]
        )


__all__ = [
    "RAGConflictResolutionService",
    "ConflictResolutionResult",
]

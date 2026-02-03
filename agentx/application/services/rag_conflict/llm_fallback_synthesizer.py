"""LLM Fallback Synthesizer for RAG Conflict Resolution.

Handles Tier 4 conflict resolution using DSPy to synthesize
a unified answer from conflicting information sources.
"""

import json

import dspy

from agentx.agent.dspy_signatures.synthesis_signatures import (
    MultiSourceSynthesisSignature,
)
from agentx.core.config import get_settings
from agentx.domain.entities.memory_record import MemoryRecord, SourceType
from agentx.application.services.rag_conflict.models import ConflictResolutionResult

settings = get_settings()


class LLMFallbackSynthesizer:
    """Synthesizes conflicting memories using DSPy.

    Used as Tier 4 fallback when lower tiers cannot resolve conflicts.
    Creates a unified answer using ChainOfThought reasoning.
    """

    def __init__(self) -> None:
        """Initialize the LLM fallback synthesizer."""
        self.synthesizer = dspy.ChainOfThought(MultiSourceSynthesisSignature)

    async def synthesize(
        self,
        memories: list[MemoryRecord],
        query: str,
        conflicts: list[tuple[MemoryRecord, MemoryRecord]],
    ) -> ConflictResolutionResult:
        """Synthesize a resolution using DSPy.

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
            quality_score=settings.memory.default_quality_score,
            source_type=SourceType.UNKNOWN,
            confidence_score=settings.memory.default_confidence,
        )

        return ConflictResolutionResult(
            resolved_memory=resolved_memory,
            conflicts_detected=len(conflicts),
            conflicts_resolved=len(conflicts),
            llm_fallback_used=True,
            resolution_tier="tier4_llm_fallback",
            reasoning=f"LLM synthesis: {result.reasoning}",  # type: ignore[attr-defined]
        )


__all__ = ["LLMFallbackSynthesizer"]

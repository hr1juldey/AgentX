"""Service for synthesizing multiple research sources.

Combines multiple assessed research sources into unified answers
with consensus detection and conflict identification.
"""

import json

import dspy

from agentx.agent.dspy_signatures.synthesis_signatures import (
    MultiSourceSynthesisSignature,
)


class SynthesisService:
    """Service for synthesizing multiple research sources.

    Combines multiple sources into a unified answer, identifying
    consensus points and conflicts between sources.
    """

    def __init__(self) -> None:
        """Initialize the synthesis service."""
        self.synthesizer = dspy.ChainOfThought(MultiSourceSynthesisSignature)

    async def synthesize(self, query: str, assessed_sources: list[dict]) -> dict:
        """Synthesize multiple sources into unified answer.

        Args:
            query: User's original question
            assessed_sources: List of assessed sources with content and scores

        Returns:
            dict: Contains unified_answer, consensus_points, conflicts, confidence
        """
        if not assessed_sources:
            return {
                "unified_answer": "No sources available to synthesize.",
                "consensus_points": "",
                "conflicts": "",
                "confidence_level": "low",
                "reasoning": "No sources provided.",
            }

        # Format sources for DSPy
        sources_list = []
        for source in assessed_sources:
            source_entry = {
                "content": source.get("content", ""),
                "relevance": source.get("relevance_score", 0.5),
                "quality": source.get("quality_score", 0.5),
            }
            sources_list.append(source_entry)

        sources_json = json.dumps(sources_list, indent=2)

        # Run synthesis through DSPy ChainOfThought
        result = self.synthesizer(query=query, sources=sources_json)

        return {
            "unified_answer": result.unified_answer,  # type: ignore[attr-defined]
            "consensus_points": result.consensus_points,  # type: ignore[attr-defined]
            "conflicts": result.conflicts,  # type: ignore[attr-defined]
            "confidence_level": result.confidence_level,  # type: ignore[attr-defined]
            "reasoning": result.reasoning,  # type: ignore[attr-defined]
        }


__all__ = ["SynthesisService"]

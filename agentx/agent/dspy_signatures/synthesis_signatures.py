"""Synthesis signatures for multi-source research integration.

Provides DSPy signatures for synthesizing multiple research sources
into unified answers with consensus and conflict detection.
"""

import dspy


class MultiSourceSynthesisSignature(dspy.Signature):
    """Signature for synthesizing multiple research sources.

    Combines multiple assessed research sources into a unified answer.
    Identifies consensus points and conflicts between sources.

    Class-based signature for gemma3:4b compatibility (explicit fields).
    """

    query = dspy.InputField(
        desc="User's original question or request that needs answering"
    )
    sources = dspy.InputField(
        desc="JSON string of assessed research sources with content, relevance, and quality scores",
    )
    unified_answer = dspy.OutputField(
        desc="One coherent, comprehensive answer that synthesizes all relevant information from the sources"
    )
    consensus_points = dspy.OutputField(
        desc="Key points that most or all sources agree upon (comma-separated list)"
    )
    conflicts = dspy.OutputField(
        desc="Conflicting information found between sources (describe the contradiction)"
    )
    confidence_level = dspy.OutputField(
        desc="Overall confidence in the unified answer: 'high', 'medium', or 'low'"
    )
    reasoning = dspy.OutputField(
        desc="Explanation of how different sources were combined and weighted"
    )


__all__ = ["MultiSourceSynthesisSignature"]

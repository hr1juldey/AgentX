# =============================================================================
# AGENTX Contextualizer - DSPy Signatures
# =============================================================================
# Type-safe DSPy signatures for contextualizer tools
# =============================================================================

import dspy


class ScoreRelevanceSignature(dspy.Signature):
    """Score a single result's relevance to the query."""

    query: str = dspy.InputField(desc="User query")
    result: str = dspy.InputField(desc="Search result to score")
    relevance_score: float = dspy.OutputField(desc="Relevance score from 0.0 to 1.0")


class CheckRelevanceSignature(dspy.Signature):
    """Check if a result is relevant to the query."""

    query: str = dspy.InputField(desc="User query")
    result: str = dspy.InputField(desc="Search result to check")
    is_relevant: bool = dspy.OutputField(desc="Whether the result is relevant")
    relevance_score: float = dspy.OutputField(desc="Relevance score from 0.0 to 1.0")


class ShouldIncludeSignature(dspy.Signature):
    """Determine if a result should be included in filtered results."""

    query: str = dspy.InputField(desc="User query")
    result: str = dspy.InputField(desc="Search result to evaluate")
    should_include: bool = dspy.OutputField(desc="Whether to include this result")
    reason: str = dspy.OutputField(desc="Reason for inclusion/exclusion")

# =============================================================================
# AGENTX Contextualizer - DSPy Signatures
# =============================================================================
# Type-safe DSPy signatures for contextualizer tools
# =============================================================================

import dspy


class ScoreRelevanceSignature(dspy.Signature):
    """Score a single result's relevance to the user query."""

    query: str = dspy.InputField(desc="User query")
    result: str = dspy.InputField(desc="Search result to score")
    relevance_score: float = dspy.OutputField(desc="Relevance score from 0.0 to 1.0")


class CheckRelevanceSignature(dspy.Signature):
    """Check if a search result is relevant to the user query.

    Be generous with scoring. If there is ANY connection to the query,
    score at least 0.3. Only give 0.0 for completely unrelated topics.
    """

    query: str = dspy.InputField(desc="User query")
    result: str = dspy.InputField(desc="Search result to check")

    is_relevant: bool = dspy.OutputField(desc="Whether the result is relevant")
    relevance_score: float = dspy.OutputField(desc="Relevance score from 0.0 to 1.0")


class ShouldIncludeSignature(dspy.Signature):
    """Determine if a result should be included in filtered research results.

    Include if ANY match: factual information related to query, discusses
    concepts/entities from query, provides context/examples/data, or from
    reputable source. Exclude ONLY if: completely unrelated, pure advertising,
    broken/empty content, or duplicate.

    When in doubt, INCLUDE the result.
    """

    query: str = dspy.InputField(desc="User query")
    result: str = dspy.InputField(desc="Search result to evaluate")

    should_include: bool = dspy.OutputField(desc="Whether to include this result")
    reason: str = dspy.OutputField(desc="Reason for inclusion or exclusion")

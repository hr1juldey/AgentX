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
    """Check if a result is relevant to the query.

    RELEVANCE SCORING:
    - 1.0: Directly addresses the query with specific information
    - 0.7-0.9: Strongly related topic with useful information
    - 0.4-0.6: Somewhat related, tangential or background context
    - 0.1-0.3: Weakly related, only minimal connection
    - 0.0: Completely unrelated

    BE GENEROUS with scoring. If there is ANY connection to the query,
    score it at least 0.3. Only give 0.0 for completely unrelated topics.
    """

    query: str = dspy.InputField(desc="User query")
    result: str = dspy.InputField(desc="Search result to check")
    is_relevant: bool = dspy.OutputField(desc="Whether the result is relevant")
    relevance_score: float = dspy.OutputField(desc="Relevance score from 0.0 to 1.0")


class ShouldIncludeSignature(dspy.Signature):
    """Determine if a result should be included in filtered results.

    INCLUSION CRITERIA (include if ANY match):
    1. Contains ANY factual information related to the query topic
    2. Discusses concepts, entities, or themes mentioned in the query
    3. Provides historical context, examples, or case studies
    4. Contains statistics, data, or measurements
    5. Offers analysis, opinions, or perspectives
    6. Is from a reputable source (news, academic, government, official)

    EXCLUSION CRITERIA (exclude ONLY if):
    1. Completely unrelated topic (different domain/subject)
    2. Pure advertising without informational content
    3. Broken or empty content
    4. Duplicate of another result

    WHEN IN DOUBT, INCLUDE the result. Be inclusive, not exclusive.
    """

    query: str = dspy.InputField(desc="User query")
    result: str = dspy.InputField(desc="Search result to evaluate")
    should_include: bool = dspy.OutputField(desc="Whether to include this result")
    reason: str = dspy.OutputField(desc="Reason for inclusion/exclusion")

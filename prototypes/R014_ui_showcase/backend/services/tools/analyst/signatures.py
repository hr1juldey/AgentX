# =============================================================================
# AGENTX Analyst - DSPy Signatures
# =============================================================================
# Type-safe DSPy signatures for analyst tools
# =============================================================================

import dspy


class ExtractInitialInsights(dspy.Signature):
    """Extract key insights from a text chunk.

    Return 2-3 insights, one per line starting with '- '.
    """

    text_chunk: str = dspy.InputField(desc="Text to analyze (500 chars)")
    insights: str = dspy.OutputField(
        desc="Key insights from text, one per line starting with '- '"
    )


class RefineInsights(dspy.Signature):
    """Refine insights using context from previous passes.

    Focus on different angles or deeper analysis beyond existing insights.
    """

    text_chunk: str = dspy.InputField(desc="Text to analyze")
    existing_insights: str = dspy.InputField(
        desc="Previously found insights (comma-separated)"
    )

    new_insights: str = dspy.OutputField(
        desc="2-3 additional insights NOT in existing list, one per line starting with '- '"
    )


class AssessCompletenessSignature(dspy.Signature):
    """Assess if research data is complete for answering the user query."""

    query: str = dspy.InputField(desc="User query to evaluate")
    data: str = dspy.InputField(desc="Research data to assess")

    completeness_score: float = dspy.OutputField(
        desc="Completeness score from 0.0 to 1.0"
    )
    missing_elements: str = dspy.OutputField(desc="Description of missing information")


class AssessRelevanceSignature(dspy.Signature):
    """Assess if research data is relevant to the user query."""

    query: str = dspy.InputField(desc="User query")
    data: str = dspy.InputField(desc="Research data to evaluate")

    relevance_score: float = dspy.OutputField(desc="Relevance score from 0.0 to 1.0")
    relevance_explanation: str = dspy.OutputField(
        desc="Explanation of relevance assessment"
    )


class DecideResearchSignature(dspy.Signature):
    """Decide if more research is needed based on current data quality."""

    completeness_score: float = dspy.InputField(desc="Current completeness score")
    relevance_score: float = dspy.InputField(desc="Current relevance score")

    needs_more_research: bool = dspy.OutputField(desc="Whether more research is needed")
    reason: str = dspy.OutputField(desc="Reason for the decision")

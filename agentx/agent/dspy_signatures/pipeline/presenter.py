"""DSPy signatures for Presenter agent.

Ported from R014: services/pipeline/presenter.py

Implements signatures for presenting findings and quality checking.
"""

import dspy


class PresentFindings(dspy.Signature):
    """Present findings in polished, user-friendly format.

    Transforms raw findings into:
    - Clear executive summary
    - Well-structured key points
    - Proper citations and references
    - Actionable insights
    """

    raw_findings: str = dspy.InputField(
        desc="Raw research findings to present",
        prefix="Findings: ",
    )
    query: str = dspy.InputField(
        desc="User's original question",
        prefix="Query: ",
    )
    presentation: str = dspy.OutputField(
        desc="""Polished presentation in Markdown format with:
        - Executive summary (2-3 sentences)
        - Key findings (bullet points)
        - Supporting details
        - Citations and references
        - Confidence level"""
    )


class QualityCheck(dspy.Signature):
    """Perform quality check on presentation.

    Validates:
    - Clarity and readability
    - Completeness of information
    - Proper attribution of sources
    - Absence of contradictions
    """

    presentation: str = dspy.InputField(
        desc="Presentation to quality check",
        prefix="Presentation: ",
    )
    query: str = dspy.InputField(
        desc="Original user query for relevance check",
        prefix="Query: ",
    )
    quality_score: float = dspy.OutputField(
        desc="Overall quality score (0.0 to 1.0)",
        prefix="Score: ",
    )
    issues: str = dspy.OutputField(
        desc="Any quality issues found (empty if none)",
        prefix="Issues: ",
    )
    approved: bool = dspy.OutputField(
        desc="Whether presentation passes quality check",
        prefix="Approved: ",
    )

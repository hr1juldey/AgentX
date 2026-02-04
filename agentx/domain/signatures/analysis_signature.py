"""DSPy signatures for query analysis tasks."""

import dspy


class AnalysisSignature(dspy.Signature):
    """Signature for query analysis tasks.

    Analyzes query and context to extract goals and confidence.
    """

    query: str = dspy.InputField(desc="The user query to analyze")
    context: str = dspy.InputField(desc="Additional context for analysis")

    goals: list[str] = dspy.OutputField(desc="Extracted goals from the query")
    confidence: float = dspy.OutputField(desc="Confidence score (0.0 to 1.0)")

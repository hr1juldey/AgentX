"""DSPy signatures for search and research tasks."""

import dspy


class SearchSignature(dspy.Signature):
    """Signature for search and research tasks.

    Searches available tools and cites sources.
    """

    query: str = dspy.InputField(desc="The search query")
    context: str = dspy.InputField(desc="Additional context")

    answer: str = dspy.OutputField(desc="The search answer")
    reasoning: str = dspy.OutputField(desc="Search reasoning process")
    citations: list[str] = dspy.OutputField(desc="Source citations")

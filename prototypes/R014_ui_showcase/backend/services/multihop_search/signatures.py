# =============================================================================
# AGENTX Multi-Hop Search DSPy Signatures
# =============================================================================
# DSPy signatures for multi-hop search with runtime reflection
# =============================================================================

from __future__ import annotations

import dspy
from dspy.signatures import Signature


class GenerateSearchQuery(Signature):
    """Generate a search query based on current context.

    The first hop should use the original question directly.
    Subsequent hops should refine the query based on what we've learned.
    """

    question: str = dspy.InputField(desc="Original user question")
    context: str = dspy.InputField(desc="Accumulated context from previous hops")
    hop_number: int = dspy.InputField(desc="Current hop number")
    total_hops: int = dspy.InputField(desc="Total number of hops")

    search_query: str = dspy.OutputField(desc="Optimized search query for this hop")
    reasoning: str = dspy.OutputField(desc="Reasoning behind this query")


class AnswerWithSources(Signature):
    """Answer questions using provided documents with citations.

    IMPORTANT: Include inline citations like [1], [2] when referencing documents.
    """

    question: str = dspy.InputField(desc="Question to answer")
    context: str = dspy.InputField(desc="Accumulated context from previous hops")

    answer: str = dspy.OutputField(
        desc="Comprehensive answer with inline citations [1], [2], etc."
    )
    sources_summary: str = dspy.OutputField(desc="Brief summary of sources used")


class CheckCompleteness(Signature):
    """Check if we have enough information to answer the question.

    This is a runtime reflection checkpoint to decide if we should continue searching.
    """

    question: str = dspy.InputField(desc="Original question")
    current_answer: str = dspy.InputField(desc="Current best answer from all hops")
    documents_summary: str = dspy.InputField(desc="Brief summary of documents found")

    is_sufficient: bool = dspy.OutputField(
        desc="True if we can answer the question well"
    )
    confidence: float = dspy.OutputField(desc="Confidence score 0.0 to 1.0")
    gap_description: str = dspy.OutputField(
        desc="Brief description of what's missing (if not sufficient)"
    )


class GenerateNextQuery(Signature):
    """Generate the next search query based on what's missing.

    Strategy options:
    - REFINE_TOPIC: Dig deeper into the same aspect
    - DISCOVER_NEW: Explore a different angle
    - VALIDATE_EXPAND: Verify and extend findings
    """

    question: str = dspy.InputField(desc="Original question")
    gap_description: str = dspy.InputField(desc="What information is still missing")
    previous_queries: list[str] = dspy.InputField(desc="Search queries already tried")

    next_query: str = dspy.OutputField(desc="Proposed search query for next hop")
    strategy: str = dspy.OutputField(
        desc="Strategy: REFINE_TOPIC (go deeper), DISCOVER_NEW (new angle), VALIDATE_EXPAND (verify)"
    )


class SynthesizeFinalAnswer(Signature):
    """Synthesize final answer from all hop results."""

    question: str = dspy.InputField(desc="Original question")
    all_hop_answers: list[str] = dspy.InputField(desc="Answers from each hop")
    all_context: list[str] = dspy.InputField(desc="Context from each hop")

    final_answer: str = dspy.OutputField(desc="Synthesized final answer")
    summary: str = dspy.OutputField(desc="Brief summary of findings")
    confidence: str = dspy.OutputField(desc="Confidence level: low, medium, or high")

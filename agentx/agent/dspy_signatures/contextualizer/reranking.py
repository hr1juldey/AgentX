"""DSPy signatures for Contextualizer agent.

Ported from R014: services/tools/contextualizer/reranking.py

Implements 3 signatures for context reranking and injection:
- ReorderContext: Reorder context by relevance
- FilterContext: Filter irrelevant context
- InjectContext: Inject context into findings
"""

import dspy


class ReorderContext(dspy.Signature):
    """Reorder context chunks by relevance to query.

    Ranks context segments from most to least relevant.
    Uses semantic similarity and query matching.
    """

    query: str = dspy.InputField(
        desc="User's original question",
        prefix="Query: ",
    )
    context_chunks: str = dspy.InputField(
        desc="Context chunks to reorder (JSON array of objects with text and source)",
        prefix="Context: ",
    )
    reordered_context: str = dspy.OutputField(
        desc="Reordered context chunks from most to least relevant, as JSON array"
    )


class FilterContext(dspy.Signature):
    """Filter out irrelevant or redundant context.

    Removes context chunks that:
    - Don't address the query
    - Are duplicates or near-duplicates
    - Are low quality or unreliable
    """

    query: str = dspy.InputField(
        desc="User's original question for relevance filtering",
        prefix="Query: ",
    )
    context_chunks: str = dspy.InputField(
        desc="Context chunks to filter (JSON array)",
        prefix="Context: ",
    )
    filtered_context: str = dspy.OutputField(
        desc="""Filtered context chunks with only relevant, non-redundant entries.
        Return as JSON array with reason for each kept entry."""
    )
    removed_count: int = dspy.OutputField(
        desc="Number of chunks removed",
        prefix="Removed: ",
    )


class InjectContext(dspy.Signature):
    """Inject relevant context into research findings.

    Enriches research findings with relevant context from:
    - Previous research results
    - User preferences and history
    - Domain knowledge
    """

    findings: str = dspy.InputField(
        desc="Original research findings to enrich",
        prefix="Findings: ",
    )
    context: str = dspy.InputField(
        desc="Additional context to inject",
        prefix="Context: ",
    )
    query: str = dspy.InputField(
        desc="Original query for relevance",
        prefix="Query: ",
    )
    enriched_findings: str = dspy.OutputField(
        desc="""Enriched findings with context naturally integrated.
        Format as Markdown with:
        - Original findings enhanced
        - Context seamlessly woven in
        - Clear citations for all sources"""
    )


class AssessContextQuality(dspy.Signature):
    """Assess the quality and relevance of context chunks.

    Evaluates context on:
    - Relevance to query
    - Information density
    - Source credibility
    - Freshness (for time-sensitive queries)
    """

    context_chunk: str = dspy.InputField(
        desc="Single context chunk to assess",
        prefix="Context: ",
    )
    query: str = dspy.InputField(
        desc="User's original query for relevance assessment",
        prefix="Query: ",
    )
    quality_score: float = dspy.OutputField(
        desc="Quality score from 0.0 (poor) to 1.0 (excellent)",
        prefix="Score: ",
    )
    relevance_score: float = dspy.OutputField(
        desc="Relevance score from 0.0 (irrelevant) to 1.0 (highly relevant)",
        prefix="Relevance: ",
    )
    should_keep: bool = dspy.OutputField(
        desc="Whether this chunk should be kept in the final context",
        prefix="Keep: ",
    )

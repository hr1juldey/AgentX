"""DSPy signatures for Analyst agent.

Ported from R014: services/tools/analyst/signatures.py, query_analyzer.py

These signatures define the input/output contracts for DSPy modules used
in the Analyst agent's dual-pass pipeline.
"""

import dspy


class AnalyzeQueryContext(dspy.Signature):
    """Analyze the context and domain of the user query.

    Detects query type, subject domain, and urgency level for routing.
    """

    query: str = dspy.InputField(desc="User's question or request")

    query_type: str = dspy.OutputField(
        desc="Type of query: question, task, comparison, analysis, or other"
    )
    domain: str = dspy.OutputField(
        desc="Subject area: economics, technology, science, general, etc."
    )
    urgency: str = dspy.OutputField(
        desc="Urgency level: immediate, routine, or background"
    )


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


class DetectGoal(dspy.Signature):
    """Detect the primary goal of the user query."""

    query: str = dspy.InputField(desc="User's question or request")
    insights: str = dspy.InputField(
        desc="Context from query analysis (optional)", default=""
    )

    goal: str = dspy.OutputField(
        desc="Primary goal: information_retrieval, data_analysis, comparison, or action"
    )


class DetectScope(dspy.Signature):
    """Detect the scope of the query."""

    query: str = dspy.InputField(desc="User's question or request")

    scope: str = dspy.OutputField(
        desc="Scope: broad (comprehensive overview), specific (targeted answer), or comparison (between items)"
    )


class DetectDepth(dspy.Signature):
    """Detect the required depth of analysis."""

    query: str = dspy.InputField(desc="User's question or request")
    goal: str = dspy.InputField(desc="Detected goal from analysis")

    depth: str = dspy.OutputField(
        desc="Required depth: shallow (quick answer), deep (detailed analysis), or comprehensive (multi-source)"
    )


class ExtractSearchTerms(dspy.Signature):
    """Extract specific search terms with temporal and domain qualifiers.

    For queries about historical events, include:
    - Specific event names (not generic terms)
    - Year ranges or time periods
    - Domain-specific keywords (GDP, sanctions, reconstruction, etc.)
    - Authoritative source types (reports, studies, analysis)

    Examples:
    - "Economic Impact of Major Wars Since 2000"
      → ["iraq war economic impact 2003-2011", "afghanistan war cost analysis",
         "ukraine war gdp decline 2022", "syrian civil war economic damage"]
    """

    query: str = dspy.InputField(desc="User's original question")
    domain: str = dspy.InputField(desc="Subject area (economics, technology, etc.)")
    insights: str = dspy.InputField(desc="Context from query analysis")

    search_terms: str = dspy.OutputField(
        desc="3-5 specific search phrases with temporal/domain qualifiers, comma-separated. "
        "Include specific names, years, and domain keywords. "
        "Example: 'iraq war economic impact 2003-2011, afghanistan war cost analysis'"
    )


class AssessDataQuality(dspy.Signature):
    """Assess the quality and completeness of research data (Pass 2).

    Used in the second pass of the Analyst agent to judge if more research is needed.
    """

    query: str = dspy.InputField(desc="Original user query")
    data: str = dspy.InputField(desc="Research data to assess")

    completeness_score: float = dspy.OutputField(
        desc="Completeness score from 0.0 (incomplete) to 1.0 (complete)"
    )
    relevance_score: float = dspy.OutputField(
        desc="Relevance score from 0.0 (irrelevant) to 1.0 (highly relevant)"
    )
    missing_elements: str = dspy.OutputField(
        desc="Description of missing information, if any"
    )
    needs_more_research: bool = dspy.OutputField(desc="Whether more research is needed")

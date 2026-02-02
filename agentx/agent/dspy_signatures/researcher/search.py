"""DSPy signatures for Researcher agent.

Ported from R014: services/tools/researcher/search.py

Implements 3 signatures for search execution and data structuring:
- ExecuteSearch: Search query execution
- StructureData: Raw search result structuring
- BeautifyFindings: Findings beautification for presentation
"""

import dspy


class ExecuteSearch(dspy.Signature):
    """Execute a web search using extracted search terms.

    Takes search terms from the analyst and executes the search.
    Returns structured search results with URLs and snippets.
    """

    search_terms: str = dspy.InputField(
        desc="Comma-separated search terms (2-5 word phrases)"
    )
    domain: str = dspy.InputField(
        desc="Subject domain for domain-specific search optimization",
        prefix="Domain: ",
    )
    num_results: int = dspy.InputField(
        desc="Number of results to retrieve (typically 5-10)",
        prefix="Max results: ",
    )
    search_results: str = dspy.OutputField(
        desc="Structured search results with title, URL, snippet for each result"
    )


class StructureData(dspy.Signature):
    """Structure raw search results into organized data.

    Extracts key information from raw search results:
    - Titles and snippets
    - URLs and sources
    - Publication dates
    - Key facts and data points
    """

    raw_results: str = dspy.InputField(
        desc="Raw search results from search engine",
        prefix="Raw results: ",
    )
    query_context: str = dspy.InputField(
        desc="Original query context for relevance filtering",
        prefix="Query context: ",
    )
    structured_data: str = dspy.OutputField(
        desc="""Structured data with:
        - source_title: Title of source
        - source_url: Direct URL
        - published_date: Date if available (YYYY-MM-DD)
        - snippet: Relevant excerpt
        - key_facts: List of key facts found

        Format as JSON-like structure with one entry per source."""
    )


class BeautifyFindings(dspy.Signature):
    """Beautify research findings for presentation.

    Transforms structured data into readable, well-formatted findings
    suitable for presentation to the user.
    """

    structured_data: str = dspy.InputField(
        desc="Structured research data from data structurer",
        prefix="Structured data: ",
    )
    original_query: str = dspy.InputField(
        desc="Original user query for context",
        prefix="Original query: ",
    )
    beautified_findings: str = dspy.OutputField(
        desc="""Well-formatted findings with:
        - Executive summary (2-3 sentences)
        - Key findings (bullet points)
        - Source citations with URLs
        - Confidence level (high/medium/low)

        Format in Markdown for readability."""
    )


class ExtractSearchQuery(dspy.Signature):
    """Extract optimized search queries from search terms.

    For queries about historical events with temporal qualifiers:
    - Include specific event names (not generic terms)
    - Add year ranges or time periods
    - Include domain-specific keywords (GDP, sanctions, reconstruction, etc.)
    - Format for search engine optimization
    """

    search_terms: str = dspy.InputField(
        desc="Search terms from analyst agent",
        prefix="Search terms: ",
    )
    domain: str = dspy.InputField(
        desc="Subject domain for domain-specific terms",
        prefix="Domain: ",
    )
    original_query: str = dspy.InputField(
        desc="Original user query for context",
        prefix="Original query: ",
    )
    optimized_queries: str = dspy.OutputField(
        desc="""3-5 optimized search queries, one per line.
        Each query should be 2-5 words with temporal/domain qualifiers.
        Format: query_1, query_2, query_3, ... (comma-separated)"""
    )


class AssessRelevance(dspy.Signature):
    """Assess the relevance of a source to the user query.

    Used in citation building to score and rank sources by relevance.
    """

    query: str = dspy.InputField(desc="Original user query for context")
    source: str = dspy.InputField(
        desc="Source text (title + snippet) to assess relevance"
    )

    relevance_score: float = dspy.OutputField(
        desc="Relevance score from 0.0 (not relevant) to 1.0 (highly relevant)"
    )

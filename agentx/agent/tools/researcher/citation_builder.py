"""Citation Builder Module for Researcher agent.

Ported from R014: services/tools/researcher/citation_builder.py

Builds properly formatted citations from structured search results.
Includes relevance scoring and source credibility assessment.

Fraud #9 fix: Returns dspy.Prediction instead of dict.
"""

import dspy

from agentx.agent.dspy_signatures.researcher import AssessRelevance
from agentx.agent.tools.common.dspy_helpers import safe_extract
from agentx.agent.tools.common.type_utils import _to_float


class CitationBuilderModule(dspy.Module):
    """Builds properly formatted citations from structured data.

    Takes structured search results and creates:
    - Properly formatted citations (APA/MLA style)
    - Relevance scores for each source
    - Source credibility assessment
    - Direct URLs for verification

    Fraud #9 fix: Returns dspy.Prediction instead of dict.
    """

    def __init__(self) -> None:
        """Initialize the citation builder."""
        super().__init__()
        self.assessor = dspy.Predict(AssessRelevance)

    def forward(self, structured_data: list[dict], query: str) -> dspy.Prediction:
        """Build citations from structured data.

        Args:
            structured_data: List of structured source entries
            query: Original user query for relevance scoring

        Returns:
            dspy.Prediction with 'citations' (list of dict) and 'top_sources' (list)
        """
        citations = []

        for entry in structured_data:
            # Extract source information
            source_title = entry.get("source_title", "Unknown Title")
            source_url = entry.get("source_url", "")
            published_date = entry.get("published_date", "n.d.")
            snippet = entry.get("snippet", "")

            # Assess relevance
            relevance = self._assess_relevance(query, source_title, snippet)

            # Build citation
            citation = {
                "title": source_title,
                "url": source_url,
                "date": published_date,
                "snippet": snippet,
                "relevance_score": relevance,
                "credibility": self._assess_credibility(entry),
            }

            citations.append(citation)

        # Sort by relevance
        citations.sort(key=lambda x: x["relevance_score"], reverse=True)

        # Extract top sources
        top_sources = [c["title"] for c in citations[:3] if c["relevance_score"] > 0.5]

        return dspy.Prediction(
            citations=citations,
            top_sources=top_sources,
        )

    def _assess_relevance(self, query: str, title: str, snippet: str) -> float:
        """Assess relevance of source to query.

        Args:
            query: Original user query
            title: Source title
            snippet: Source snippet/abstract

        Returns:
            float: Relevance score from 0.0 to 1.0
        """
        # Build context string
        source_text = f"{title}. {snippet}"

        # Run DSPy assessment
        result = self.assessor(query=query, source=source_text)

        # Parse relevance score
        score_str = safe_extract(result, "relevance_score", "0.5")
        return _to_float(score_str, default=0.5)

    def _assess_credibility(self, entry: dict) -> str:
        """Assess source credibility based on domain and metadata.

        Args:
            entry: Structured source entry

        Returns:
            str: Credibility level (high/medium/low)
        """
        url = entry.get("source_url", "")

        # High credibility domains
        high_domains = [
            ".edu",
            ".gov",
            "wikipedia.org",
            "scholar.google.com",
            "nature.com",
            "science.org",
            "ieee.org",
            "acm.org",
        ]

        # Check for high credibility
        for domain in high_domains:
            if domain in url:
                return "high"

        # Check for news sources (medium credibility)
        medium_domains = [
            ".com",
            ".org",
            ".net",
            "news.",
            "reuters",
            "apnews",
            "bbc",
        ]

        for domain in medium_domains:
            if domain in url:
                return "medium"

        # Default to low
        return "low"

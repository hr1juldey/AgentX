"""Findings Beautifier Module for Researcher agent.

Ported from R014: services/tools/researcher/findings_beautifier.py

Beautifies research findings into readable Markdown format.
Transforms structured data into user-friendly presentation.
"""

import dspy

from agentx.agent.dspy_signatures.researcher.search import BeautifyFindings
from agentx.agent.tools.common.dspy_helpers import safe_extract


class FindingsBeautifierModule(dspy.Module):
    """Beautifies research findings for presentation.

    Takes structured data and citations, transforms into:
    - Executive summary (2-3 sentences)
    - Key findings (bullet points)
    - Source citations with URLs
    - Confidence level assessment
    """

    def __init__(self) -> None:
        """Initialize the findings beautifier."""
        super().__init__()
        self.beautifier = dspy.ChainOfThought(BeautifyFindings)

    def forward(
        self, structured_data: list[dict], citations: list[dict], query: str
    ) -> dict:
        """Beautify findings into readable format.

        Args:
            structured_data: List of structured source entries
            citations: List of citation dicts with relevance scores
            query: Original user query

        Returns:
            dict with 'beautified_findings' (str) and 'confidence' (str)
        """
        # Build structured data string
        data_str = self._format_structured_data(structured_data, citations)

        # Run beautifier
        result = self.beautifier(structured_data=data_str, original_query=query)

        # Extract beautified findings
        findings = safe_extract(result, "beautified_findings", "")

        # Assess confidence based on citation quality
        confidence = self._assess_confidence(citations)

        return {
            "beautified_findings": findings,
            "confidence": confidence,
        }

    def _format_structured_data(
        self, structured_data: list[dict], citations: list[dict]
    ) -> str:
        """Format structured data and citations into string.

        Args:
            structured_data: List of structured entries
            citations: List of citation dicts

        Returns:
            str: Formatted data string
        """
        lines: list[str] = []
        for i, (entry, cit) in enumerate(zip(structured_data, citations), 1):
            lines.append(f"Source {i}:")
            lines.append(f"  Title: {entry.get('source_title', 'Unknown')}")
            lines.append(f"  URL: {cit.get('url', 'N/A')}")
            lines.append(f"  Relevance: {cit.get('relevance_score', 0.0):.2f}")
            lines.append(f"  Snippet: {entry.get('snippet', 'N/A')[:200]}...")
            lines.append("")

        return "\n".join(lines)

    def _assess_confidence(self, citations: list[dict]) -> str:
        """Assess overall confidence in findings.

        Args:
            citations: List of citation dicts with relevance scores

        Returns:
            str: Confidence level (high/medium/low)
        """
        if not citations:
            return "low"

        # Calculate average relevance
        avg_relevance = sum(c.get("relevance_score", 0.0) for c in citations) / len(
            citations
        )

        # Count high credibility sources
        high_cred = sum(1 for c in citations if c.get("credibility") == "high")

        # Assess confidence
        if avg_relevance > 0.7 and high_cred >= 2:
            return "high"
        elif avg_relevance > 0.5 and high_cred >= 1:
            return "medium"
        else:
            return "low"

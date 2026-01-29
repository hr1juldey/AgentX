"""Search Term Extractor Module for Analyst agent.

Ported from R014: services/tools/analyst/search_terms.py

Extracts short search phrases for traditional search engines (SearXNG).
Uses few-shot learning with multiple iterations for diverse term generation.
"""

import dspy

from agentx.agent.dspy_signatures.analyst import ExtractSearchTerms
from agentx.agent.tools.common.dspy_helpers import safe_extract


class SearchTermExtractorModule(dspy.Module):
    """Extracts short search terms for SearXNG from natural language queries.

    Runs extraction multiple times to get diverse search terms, then
    combines and deduplicates for comprehensive search coverage.

    Uses few-shot learning pattern for robust extraction.
    """

    def __init__(self, num_iterations: int = 3) -> None:
        """Initialize the search term extractor.

        Args:
            num_iterations: Number of extraction iterations for diversity
        """
        super().__init__()
        self.extractor = dspy.ChainOfThought(ExtractSearchTerms)
        self.num_iterations = num_iterations

    def forward(self, query: str, insights: list, domain: str = "general") -> dict:
        """Extract search terms from user query with multiple iterations.

        Args:
            query: User's question or request
            insights: Context from query analysis
            domain: Subject area for domain-specific terms

        Returns:
            dict with 'search_terms' (list) and 'domain' (str)
        """
        all_terms = set()

        for _ in range(self.num_iterations):
            result = self.extractor(
                query=query,
                domain=domain,
                insights=str(insights),
            )

            raw_terms = safe_extract(result, "search_terms", "")

            if "," in raw_terms:
                terms = [t.strip() for t in raw_terms.split(",")]
            else:
                terms = [t.strip() for t in raw_terms.split("\n") if t.strip()]

            for t in terms:
                t_clean = t.lower().strip()
                # Filter for 2-5 word phrases (good for search engines)
                if 2 <= len(t_clean.split()) <= 5:
                    all_terms.add(t_clean)

        valid_terms = list(all_terms)

        # Fallback: use first 5 words if no terms extracted
        if not valid_terms:
            words = query.split()[:5]
            valid_terms = [" ".join(words).lower()]

        return {"search_terms": valid_terms, "domain": domain}

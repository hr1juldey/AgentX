# =============================================================================
# AGENTX Analyst - Search Term Extractor Module
# =============================================================================
# Extracts short search phrases for traditional search engines (SearXNG)
# =============================================================================

import dspy


class ExtractSearchTerms(dspy.Signature):
    """Extract short search phrases for traditional search engines like SearXNG.

    Traditional search engines work best with 2-4 word keyword phrases rather
    than full natural language sentences.

    Examples:
        Query: "Explain labor force migration and remittance economics"
        Terms: "labor force migration, remittance economics, workforce data"
    """

    query: str = dspy.InputField(desc="User's original question")
    domain: str = dspy.InputField(desc="Subject area (economics, technology, etc.)")
    insights: str = dspy.InputField(desc="Context from query analysis")

    search_terms: str = dspy.OutputField(
        desc="3-5 short search phrases (2-4 words each), comma-separated. "
        "Example: 'labor force migration, remittance economics, workforce data'"
    )


class SearchTermExtractorModule(dspy.Module):
    """Extracts short search terms for SearXNG from natural language queries.

    Runs extraction multiple times to get diverse search terms, then
    combines and deduplicates for comprehensive search coverage.
    """

    def __init__(self, num_iterations: int = 3):
        super().__init__()
        self.extractor = dspy.ChainOfThought(ExtractSearchTerms)
        self.num_iterations = num_iterations

    def forward(self, query: str, insights: list, domain: str = "general") -> dict:
        """Extract search terms from user query with multiple iterations."""
        all_terms = set()

        for i in range(self.num_iterations):
            result = self.extractor(
                query=query,
                domain=domain,
                insights=str(insights),
            )

            raw_terms = result.search_terms if hasattr(result, "search_terms") else ""

            if "," in raw_terms:
                terms = [t.strip() for t in raw_terms.split(",")]
            else:
                terms = [t.strip() for t in raw_terms.split("\n") if t.strip()]

            for t in terms:
                t_clean = t.lower().strip()
                if 2 <= len(t_clean.split()) <= 5:
                    all_terms.add(t_clean)

        valid_terms = list(all_terms)

        if not valid_terms:
            words = query.split()[:5]
            valid_terms = [" ".join(words).lower()]

        return {"search_terms": valid_terms, "domain": domain}

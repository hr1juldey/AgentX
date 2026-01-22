# =============================================================================
# AGENTX Researcher - Citation Builder Module
# =============================================================================
# Builds citations from search results
# =============================================================================

import dspy


class CitationBuilderModule(dspy.Module):
    """Builds citations from search results.

    Has 2 signatures:
    - ExtractCitations: Extract citations from raw data
    - FormatCitations: Format citations properly
    """

    def __init__(self):
        super().__init__()
        self.extract_citations = dspy.Predict("raw_data -> citations")
        self.format_citations = dspy.Predict("citations -> formatted_citations")

    def forward(self, raw_data: list) -> list:
        """Build citations from raw data."""
        citations_result = self.extract_citations(raw_data=str(raw_data))

        if hasattr(citations_result, "citations"):
            formatted = self.format_citations(citations=citations_result.citations)
            return (
                formatted.formatted_citations
                if hasattr(formatted, "formatted_citations")
                else []
            )

        return []

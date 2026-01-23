# =============================================================================
# AGENTX Researcher Data Processing Pipeline
# =============================================================================
# Executes beautifier, structurer, and citation builder
# =============================================================================


def process_research_data(
    beautifier,
    structurer,
    citer,
    raw_data: list,
    query_display: str,
) -> tuple:
    """Process raw search data through beautifier, structurer, citation builder.

    Args:
        beautifier: BeautifierModule instance
        structurer: DataStructurerModule instance
        citer: CitationBuilderModule instance
        raw_data: Filtered search results
        query_display: Query string for display

    Returns:
        Tuple of (beautiful_data, structured_data, citations)
    """
    # Beautify raw data
    beautiful_data_raw = beautifier(
        raw_data=raw_data,
        query=query_display,
    )
    beautiful_data = beautiful_data_raw if hasattr(beautiful_data_raw, "get") else {}

    # Structure the beautiful data
    structured_data_raw = structurer(beautiful_data=beautiful_data)
    structured_data = structured_data_raw if hasattr(structured_data_raw, "get") else {}

    # Build citations
    citations_raw = citer(raw_data=raw_data)
    citations = citations_raw if hasattr(citations_raw, "get") else []

    return beautiful_data, structured_data, citations

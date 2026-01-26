# =============================================================================
# AGENTX Researcher Data Processing Pipeline
# =============================================================================
# Executes beautifier, structurer, citation builder, and number extractor
# =============================================================================

from typing import Any, cast

from services.tools.researcher.number_extractor import NumberExtractorModule


def process_research_data(
    beautifier,
    structurer,
    citer,
    raw_data: list,
    query_display: str,
) -> tuple:
    """Process raw search data through beautifier, structurer, citation builder.

    Now includes number extraction for chart/table data.

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
    beautiful_data_raw = beautifier(raw_data=raw_data, query=query_display)
    beautiful_data = beautiful_data_raw if hasattr(beautiful_data_raw, "get") else {}

    # Extract structured numbers from raw documents
    number_extractor = NumberExtractorModule()
    number_data = cast(dict[str, Any], number_extractor(raw_data=raw_data))
    extracted_numbers = number_data.get("extracted_numbers", [])

    # Add extracted numbers to beautiful_data
    beautiful_data["extracted_numbers"] = extracted_numbers

    # Structure the beautiful data
    structured_data_raw = structurer(beautiful_data=beautiful_data)
    structured_data = structured_data_raw if hasattr(structured_data_raw, "get") else {}

    # Build citations with structured report as writing parameter
    structured_report = structured_data.get("structured_report", "")
    citations_raw = citer(raw_data=raw_data, writing=structured_report)
    citations = citations_raw if hasattr(citations_raw, "get") else []

    return beautiful_data, structured_data, citations

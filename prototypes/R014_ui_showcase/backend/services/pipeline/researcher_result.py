# =============================================================================
# AGENTX Researcher Result Construction
# =============================================================================
# Builds the final researcher output dictionary
# =============================================================================

from services.pipeline.researcher_helpers import (
    determine_data_type,
    generate_summary_report,
)


def build_researcher_result(
    raw_data: list,
    beautiful_data: dict,
    structured_data: dict,
    citations: list,
    analysis: dict,
    url_list: list = [],
) -> dict:
    """Build the final researcher result dictionary.

    Args:
        raw_data: Filtered search results
        beautiful_data: Processed beautiful data from beautifier
        structured_data: Structured data from structurer
        citations: Citation list
        analysis: Original analysis from ANALYST agent

    Returns:
        Complete researcher result dictionary
    """
    domain = analysis.get("domain", "general")
    query_for_log = analysis.get("query") or analysis.get("goal") or ""
    search_terms = analysis.get("search_terms", [])

    return {
        "raw_data": raw_data,
        "documents": raw_data,  # Alias for orchestration compatibility
        "beautiful_data": {
            "key_facts": beautiful_data.get("key_facts", [])
            if hasattr(beautiful_data, "get")
            else [],
            "trends": beautiful_data.get("trends", [])
            if hasattr(beautiful_data, "get")
            else [],
            "comparisons": beautiful_data.get("comparisons", [])
            if hasattr(beautiful_data, "get")
            else [],
            "extracted_numbers": beautiful_data.get("extracted_numbers", [])
            if hasattr(beautiful_data, "get")
            else [],
        },
        "structured_data": structured_data,
        "citations": citations,
        "structured_report": generate_summary_report(
            beautiful_data if isinstance(beautiful_data, dict) else {},
            citations if isinstance(citations, list) else [],
            domain,
        ),
        "data_type": determine_data_type(
            analysis, beautiful_data if isinstance(beautiful_data, dict) else {}
        ),
        "query": query_for_log,
        "search_terms": search_terms,
        "url_list": url_list,
    }

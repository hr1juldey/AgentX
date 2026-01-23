# =============================================================================
# AGENTX RESEARCHER - Helper Methods
# =============================================================================
# Summary report and data type determination utilities
# =============================================================================


def generate_summary_report(
    beautiful_data: dict,
    citations: list,
    domain: str,
) -> str:
    """Generate a summary report from research.

    Args:
        beautiful_data: Beautified research data
        citations: Citation list
        domain: Domain/subject area

    Returns:
        Summary report string
    """
    parts = []

    key_facts = (
        beautiful_data.get("key_facts", []) if hasattr(beautiful_data, "get") else []
    )
    trends = beautiful_data.get("trends", []) if hasattr(beautiful_data, "get") else []

    if key_facts:
        parts.append("Key findings: " + ", ".join(key_facts[:3]))

    if trends:
        parts.append("Trends: " + ", ".join(trends[:3]))

    return " | ".join(parts) if parts else f"Research completed for {domain}"


def determine_data_type(analysis: dict, beautiful_data: dict) -> str:
    """Determine the type of data for widget selection.

    Args:
        analysis: Analysis result from ANALYST agent
        beautiful_data: Beautified research data

    Returns:
        Data type string
    """
    query = analysis.get("query", "").lower()
    domain = analysis.get("domain", "").lower()

    if "price" in query or "stock" in query or "finance" in domain:
        return "numerical_time_series"
    if "image" in query or "photo" in query:
        return "visual_image"
    if "comparison" in query:
        return "comparative"

    return "general"

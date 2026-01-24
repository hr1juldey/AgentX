# =============================================================================
# AGENTX DATA CONTEXTUALIZER Utilities
# =============================================================================
# Helper functions for data contextualization
# =============================================================================


def extract_top_facts(contextualized_data: list) -> list:
    """Extract top facts from contextualized data.

    Args:
        contextualized_data: List of contextualized data items

    Returns:
        List of top facts as strings
    """
    if not contextualized_data:
        return []

    facts = []
    for item in contextualized_data[:5]:
        if isinstance(item, dict):
            if "title" in item:
                facts.append(item["title"])
            elif "text" in item:
                text = item.get("text", "")
                facts.append(text[:100] + "..." if len(text) > 100 else text)
        else:
            facts.append(str(item)[:100])

    return facts

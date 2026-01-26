# =============================================================================
# AGENTX Researcher - Link Parser
# =============================================================================
# Helper functions for parsing link extraction results
# =============================================================================

"""Helper functions for parsing link extraction results.

Provides utilities for parsing DSPy link extraction output.
"""


def parse_relevant_links(relevant_urls: str, original_links: list[dict]) -> list[dict]:
    """Parse relevant URLs from DSPy output and match with original links.

    Args:
        relevant_urls: String output from DSPy with URLs and reasons
        original_links: Original list of link dicts with 'url' and 'text' keys

    Returns:
        List of relevant link dicts with 'reason' field added (max 3)
    """
    relevant_links = []

    for line in relevant_urls.split("\n"):
        line = line.strip()
        if not line or line.upper() == "NONE":
            continue

        # Parse "URL | reason" format
        if "|" in line:
            url_part = line.split("|")[0].strip()
            reason = line.split("|", 1)[1].strip() if "|" in line else ""

            # Find matching link from original list
            for link in original_links:
                if link["url"] == url_part:
                    relevant_links.append(
                        {
                            "url": link["url"],
                            "text": link.get("text", ""),
                            "reason": reason,
                        }
                    )
                    break

    return relevant_links[:3]  # Limit to 3 links per page

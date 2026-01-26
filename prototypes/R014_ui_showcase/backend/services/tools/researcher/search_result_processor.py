# =============================================================================
# AGENTX Researcher - Search Result Processor
# =============================================================================
# Extracts and formats search results for OpenGraph rendering
# =============================================================================


def extract_url_list(results: list[dict], image_search: bool) -> list[dict]:
    """Extract URLs from search results for OpenGraph rendering.

    Args:
        results: Raw search results from SearXNG
        image_search: Whether this is an image search

    Returns:
        List of URL dicts with url, title, snippet, source, engine
    """
    url_list = []
    for result in results:
        # For image search, extract img_src (the actual image URL)
        # For general/news, extract the page URL
        if image_search:
            url = result.get("img_src", "")
        else:
            url = result.get("url", "")

        if url and url.startswith("http"):
            url_list.append(
                {
                    "url": url,
                    "title": result.get("title", ""),
                    "snippet": result.get("content", "")[:200],
                    "source": result.get("source", ""),
                    "engine": result.get("engine", ""),
                }
            )

    return url_list

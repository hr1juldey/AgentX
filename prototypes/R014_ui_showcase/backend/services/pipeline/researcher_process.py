# =============================================================================
# AGENTX Researcher Data Processing Pipeline
# =============================================================================
# Executes beautifier, structurer, citation builder, and number extractor
# =============================================================================

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, cast

from services.tools.researcher.number_extractor import NumberExtractorModule
from services.tools.researcher.web_fetcher import fetch_multiple_pages

logger = logging.getLogger(__name__)


def enrich_raw_data_with_content(raw_data: list, max_fetch: int = 10) -> list:
    """Fetch full content for top documents to improve number extraction.

    Args:
        raw_data: List of search result dicts with 'url' field
        max_fetch: Maximum number of pages to fetch (to limit latency)

    Returns:
        Enriched raw_data with 'full_content' field added
    """
    if not raw_data:
        return raw_data

    # Extract URLs from top documents
    urls_to_fetch = [doc.get("url") for doc in raw_data[:max_fetch] if doc.get("url")]

    if not urls_to_fetch:
        return raw_data

    try:
        # Run async fetch in sync context
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create new thread for async operation
            with ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run, fetch_multiple_pages(urls_to_fetch)
                )
                fetched_pages = future.result()
        else:
            fetched_pages = asyncio.run(fetch_multiple_pages(urls_to_fetch))

        # Create URL -> content mapping
        url_to_content = {}
        for page in fetched_pages:
            if page and "markdown_content" in page:
                url_to_content[page["url"]] = page["markdown_content"]

        # Add full_content to raw_data
        enriched = []
        for doc in raw_data:
            url = doc.get("url")
            if url and url in url_to_content:
                # Add full_content while preserving original content
                doc_with_full = doc.copy()
                doc_with_full["full_content"] = url_to_content[url]
                enriched.append(doc_with_full)
            else:
                enriched.append(doc)

        logger.info(
            f"[CONTENT_FETCH] Enriched {len(url_to_content)}/{len(urls_to_fetch)} documents"
        )
        return enriched

    except Exception as e:
        logger.warning(f"[CONTENT_FETCH] Failed to fetch content: {e}")
        return raw_data


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
    # First, enrich with full content for better number extraction
    enriched_raw_data = enrich_raw_data_with_content(raw_data, max_fetch=10)

    number_extractor = NumberExtractorModule()
    number_data = cast(
        dict[str, Any],
        number_extractor(raw_data=enriched_raw_data, query=query_display),
    )
    extracted_numbers = number_data.get("extracted_numbers", [])

    # Add extracted numbers to beautiful_data
    beautiful_data["extracted_numbers"] = extracted_numbers

    # Structure the beautiful data
    structured_data_raw = structurer(beautiful_data=beautiful_data)
    structured_data = structured_data_raw if hasattr(structured_data_raw, "get") else {}

    # Build citations with structured report as writing parameter
    structured_report = structured_data.get("structured_report", "")
    citations_raw = citer(raw_data=raw_data, writing=structured_report)
    citations = citations_raw if isinstance(citations_raw, list) else []

    return beautiful_data, structured_data, citations

# =============================================================================
# AGENTX Research Tools
# =============================================================================
# DSPy modules for the RESEARCHER agent (Beautiful Data)
# =============================================================================

import asyncio
from typing import Optional

import dspy
import httpx


class SearXNGSearchModule(dspy.Module):
    """Searches SearXNG for live web data.

    Has 3 signatures:
    - SearchGeneral: General web search
    - SearchImages: Image search
    - SearchNews: News search
    """

    def __init__(self, searxng_url: str = "http://192.168.1.4:8080"):
        super().__init__()
        self.searxng_url = searxng_url
        self.search_general = dspy.Predict("query -> search_results")
        self.client = httpx.AsyncClient(timeout=30.0)

    async def _search_searxng(
        self,
        query: str,
        categories: Optional[list[str]] = None,
        engines: Optional[list[str]] = None,
    ) -> list[dict]:
        """Execute SearXNG search."""
        params = {
            "q": query,
            "format": "json",
        }

        if categories:
            params["categories"] = ",".join(categories)
        if engines:
            params["engines"] = ",".join(engines)

        try:
            response = await self.client.get(
                f"{self.searxng_url}/search",
                params=params,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            print(f"SearXNG search error: {e}")
            return []

    def forward(self, query: str, search_type: str = "general") -> dict:
        """Execute search based on type.

        Args:
            query: Search query
            search_type: Type of search (general, images, news)

        Returns:
            Search results with URL list for OpenGraph rendering
        """
        # Determine categories based on search_type
        categories = None
        if search_type == "news":
            categories = ["news"]

        # Run async search in sync context
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create new loop in thread
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    self._search_searxng(query, categories),
                )
                results = future.result()
        else:
            results = asyncio.run(self._search_searxng(query, categories))

        # Extract URLs for OpenGraph rendering (not images!)
        url_list = []
        for result in results:
            url = result.get("url", "")
            if url and url.startswith("http"):
                url_list.append({
                    "url": url,
                    "title": result.get("title", ""),
                    "snippet": result.get("content", "")[:200],
                    "source": result.get("source", ""),
                    "engine": result.get("engine", ""),
                })

        return {
            "raw_data": results,
            "query": query,
            "search_type": search_type,
            "url_list": url_list,  # URLs for OpenGraph rendering
        }


class BeautifierModule(dspy.Module):
    """Beautifies raw search data for presentation.

    Has 3 signatures:
    - ExtractKeyFacts: Extract key facts from results
    - IdentifyTrends: Identify trends in data
    - CreateComparisons: Create comparisons between entities
    """

    def __init__(self):
        super().__init__()
        self.extract_facts = dspy.Predict("raw_data -> key_facts")
        self.identify_trends = dspy.Predict("raw_data -> trends")
        self.create_comparisons = dspy.Predict("raw_data, query -> comparisons")

    def forward(self, raw_data: list, query: str) -> dict:
        """Beautify raw search data."""
        facts_result = self.extract_facts(raw_data=str(raw_data[:5]))
        trends_result = self.identify_trends(raw_data=str(raw_data[:5]))
        comparisons_result = self.create_comparisons(
            raw_data=str(raw_data[:5]), query=query
        )

        return {
            "key_facts": [facts_result.key_facts]
            if hasattr(facts_result, "key_facts")
            else [],
            "trends": [trends_result.trends]
            if hasattr(trends_result, "trends")
            else [],
            "comparisons": [comparisons_result.comparisons]
            if hasattr(comparisons_result, "comparisons")
            else [],
        }


class DataStructurerModule(dspy.Module):
    """Structures data for better organization.

    Has 2 signatures:
    - OrganizeByTopic: Organize results by topic
    - CreateHierarchy: Create hierarchical structure
    """

    def __init__(self):
        super().__init__()
        self.organize_topic = dspy.Predict("beautiful_data -> organized_data")
        self.create_hierarchy = dspy.Predict("organized_data -> hierarchy")

    def forward(self, beautiful_data: dict) -> dict:
        """Structure the beautiful data."""
        organized_result = self.organize_topic(beautiful_data=str(beautiful_data))
        hierarchy_result = self.create_hierarchy(organized_data=str(organized_result))

        return {
            "structured_data": organized_result.organized_data,  # type: ignore[attr-defined]
            "hierarchy": hierarchy_result.hierarchy,  # type: ignore[attr-defined]
        }


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

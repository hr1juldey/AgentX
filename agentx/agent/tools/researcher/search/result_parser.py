"""Result parsing utilities for search results.

Extracts and formats search results from SearXNG responses.
"""

from typing import Any


class SearchResultParser:
    """Parser for SearXNG search results."""

    def extract_results(self, data: dict, num_results: int) -> list[dict]:
        """Extract and format search results.

        Args:
            data: Raw SearXNG response JSON
            num_results: Maximum number of results to return

        Returns:
            list of dict with title, url, snippet, published_date
        """
        results = []

        # Extract results from SearXNG response
        raw_results = data.get("results", [])

        for item in raw_results[:num_results]:
            result = {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("content", ""),
                "published_date": self._parse_date(item),
                "engine": item.get("engine", "unknown"),
                "score": item.get("score", 0.0),
            }
            results.append(result)

        return results

    def _parse_date(self, item: dict) -> str:
        """Parse publication date from SearXNG result.

        Args:
            item: SearXNG result item

        Returns:
            str: Date in YYYY-MM-DD format, or 'n.d.' if not found
        """
        # Try to extract date from publication date field
        pub_date = item.get("publishedDate", "")
        if pub_date:
            return pub_date

        # Try to extract from metadata
        metadata = item.get("metadata", {})
        if "date" in metadata:
            return metadata["date"]

        # Default to no date
        return "n.d."

    def format_search_response(self, search_data: dict[str, Any]) -> dict[str, Any]:
        """Format search response with extracted results.

        Args:
            search_data: Raw search response from SearXNG client

        Returns:
            dict with 'results' (list) and 'query' (str)
        """
        raw_data = search_data.get("raw_data", {})
        num_results = search_data.get("num_results_requested", 10)

        # Check for errors
        if "error" in search_data:
            return {
                "results": [],
                "query": search_data.get("query", ""),
                "error": search_data["error"],
            }

        # Extract results
        results = self.extract_results(raw_data, num_results)

        return {
            "results": results,
            "query": search_data.get("query", ""),
            "total_results": len(results),
        }

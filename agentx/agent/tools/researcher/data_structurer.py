"""Data Structurer Module for Researcher agent.

Ported from R014: services/tools/researcher/data_structurer.py

Structures raw search results into organized, queryable data format.
Uses explicit signatures with named fields for robust extraction.
"""

import dspy

from agentx.agent.dspy_signatures.researcher.search import StructureData
from agentx.agent.tools.common.dspy_helpers import safe_extract


class DataStructurerModule(dspy.Module):
    """Structures raw search results into organized data.

    Takes raw search results from SearXNG and structures them into:
    - Source titles and URLs
    - Publication dates
    - Key snippets and facts
    - Relevance scores

    Uses explicit DSPy signatures with named fields for type safety.
    """

    def __init__(self) -> None:
        """Initialize the data structurer."""
        super().__init__()
        self.structurer = dspy.ChainOfThought(StructureData)

    def forward(self, raw_results: str, query_context: str) -> dict:
        """Structure raw search results into organized data.

        Args:
            raw_results: Raw search results from search engine (JSON or text)
            query_context: Original query context for relevance filtering

        Returns:
            dict with 'structured_data' (list of dict) and 'sources_count' (int)
        """
        # Run the data structuring
        result = self.structurer(raw_results=raw_results, query_context=query_context)

        # Extract the structured data string
        structured_str = safe_extract(result, "structured_data", "")

        # Parse the structured data into a list of dicts
        structured_list = self._parse_structured_data(structured_str)

        return {
            "structured_data": structured_list,
            "sources_count": len(structured_list),
        }

    def _parse_structured_data(self, structured_str: str) -> list[dict]:
        """Parse structured data string into list of dicts.

        Args:
            structured_str: String output from DSPy structurer

        Returns:
            list of dict with source_title, source_url, published_date, snippet, key_facts
        """
        if not structured_str:
            return []

        # Try to parse as JSON first
        import json

        try:
            data = json.loads(structured_str)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
        except json.JSONDecodeError:
            pass

        # Fallback: Parse line-by-line format
        # Expected format per entry:
        # source_title: <title>
        # source_url: <url>
        # published_date: <date>
        # snippet: <text>
        # key_facts: <facts>
        entries = []
        current_entry: dict[str, str | list[str]] = {}
        key_fact_buffer: list[str] = []

        for line in structured_str.split("\n"):
            line = line.strip()
            if not line:
                # Empty line marks end of entry
                if current_entry:
                    if key_fact_buffer:
                        current_entry["key_facts"] = key_fact_buffer
                    entries.append(current_entry)
                    current_entry = {}
                    key_fact_buffer = []
                continue

            # Parse key-value pairs
            if ": " in line:
                key, value = line.split(": ", 1)
                key = key.strip().lower()
                value = value.strip()

                if key == "source_title":
                    current_entry["source_title"] = value
                elif key == "source_url":
                    current_entry["source_url"] = value
                elif key == "published_date":
                    current_entry["published_date"] = value
                elif key == "snippet":
                    current_entry["snippet"] = value
                elif key == "key_facts":
                    key_fact_buffer.append(value)

        # Don't forget the last entry
        if current_entry:
            if key_fact_buffer:
                current_entry["key_facts"] = key_fact_buffer
            entries.append(current_entry)

        return entries

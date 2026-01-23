# =============================================================================
# AGENTX Researcher - Data Processor Modules
# =============================================================================
# Beautifies and structures data for presentation
# =============================================================================

import dspy
from typing import List


class BeautifierModule(dspy.Module):
    """Beautifies raw search data for presentation."""

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


class StructureDataChunk(dspy.Signature):
    """Structure a chunk of data into organized sections."""

    data_chunk: str = dspy.InputField(desc="Data to structure (max 500 chars)")
    key_facts: str = dspy.OutputField(desc="Key facts from data, numbered 1-5")
    trends: str = dspy.OutputField(desc="Trends from data, numbered 1-3")
    comparisons: str = dspy.OutputField(desc="Comparisons from data, numbered 1-2")


class DataStructurerModule(dspy.Module):
    """Structures data using ChainOfThought + chunking."""

    MAX_CHUNK_SIZE = 500

    def __init__(self):
        super().__init__()
        self.structurer = dspy.ChainOfThought(StructureDataChunk)

    def forward(self, beautiful_data: dict) -> dict:
        """Structure data by processing chunks and combining."""
        data_str = self._format_data(beautiful_data)

        if len(data_str) <= self.MAX_CHUNK_SIZE:
            return self._structure_single(data_str)

        return self._structure_chunked(data_str)

    def _structure_single(self, data_str: str) -> dict:
        """Fast path for small data."""
        result = self.structurer(data_chunk=data_str)

        return {
            "structured_data": {
                "key_facts": self._parse_numbered(result.key_facts),
                "trends": self._parse_numbered(result.trends),
                "comparisons": self._parse_numbered(result.comparisons),
            }
        }

    def _structure_chunked(self, data_str: str) -> dict:
        """Process data in chunks and combine."""
        sections = data_str.split("\n\n")
        chunks = []
        current_chunk = []
        current_size = 0

        for section in sections:
            if current_size + len(section) > self.MAX_CHUNK_SIZE:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [section]
                current_size = len(section)
            else:
                current_chunk.append(section)
                current_size += len(section)

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        all_facts = []
        all_trends = []
        all_comparisons = []

        for chunk in chunks:
            result = self.structurer(data_chunk=chunk)
            all_facts.extend(self._parse_numbered(result.key_facts))
            all_trends.extend(self._parse_numbered(result.trends))
            all_comparisons.extend(self._parse_numbered(result.comparisons))

        return {
            "structured_data": {
                "key_facts": all_facts[:5],
                "trends": all_trends[:3],
                "comparisons": all_comparisons[:2],
            }
        }

    def _parse_numbered(self, text: str) -> List[str]:
        """Parse numbered list into array."""
        items = []
        for line in text.split("\n"):
            line = line.strip()
            if any(line.startswith(f"{i}.") for i in range(1, 10)):
                items.append(line)
        return items

    def _format_data(self, data: dict) -> str:
        """Format dict to string."""
        parts = []
        if "key_facts" in data:
            parts.append("Key Facts:\n" + "\n".join(data["key_facts"]))
        if "trends" in data:
            parts.append("\nTrends:\n" + "\n".join(data["trends"]))
        return "\n\n".join(parts)

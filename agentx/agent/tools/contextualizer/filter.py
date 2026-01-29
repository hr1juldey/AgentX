"""Context Filter Module for Contextualizer agent.

Ported from R014: services/tools/contextualizer/filter.py

Filters out irrelevant, redundant, or low-quality context chunks.
"""

import dspy

from agentx.agent.dspy_signatures.contextualizer.reranking import FilterContext
from agentx.agent.tools.common.dspy_helpers import safe_extract
from agentx.agent.tools.common.type_utils import _to_float


def _to_int(value: str | float | bool | None, default: int = 0) -> int:
    """Convert value to int safely.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        int: Converted integer value
    """
    try:
        return int(float(_to_float(value, default=default)))  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return default


class ContextFilterModule(dspy.Module):
    """Filters context chunks to keep only relevant content.

    Removes:
    - Irrelevant chunks (don't address query)
    - Duplicates and near-duplicates
    - Low quality or unreliable sources
    - Redundant information
    """

    def __init__(self) -> None:
        """Initialize the context filter."""
        super().__init__()
        self.filter = dspy.Predict(FilterContext)

    def forward(self, query: str, context_chunks: list[dict]) -> dict:
        """Filter context chunks to keep only relevant ones.

        Args:
            query: User's original question
            context_chunks: List of context dicts

        Returns:
            dict with 'filtered_context' (list) and 'stats' (dict)
        """
        if not context_chunks:
            return {
                "filtered_context": [],
                "stats": {
                    "total": 0,
                    "kept": 0,
                    "removed": 0,
                    "removal_reasons": [],
                },
            }

        # Build context string for DSPy
        context_str = self._format_context(context_chunks)

        # Run filter
        result = self.filter(query=query, context_chunks=context_str)

        # Parse filtered context
        filtered_str = safe_extract(result, "filtered_context", "")
        filtered_context = self._parse_filtered_context(filtered_str)

        # Get removal count
        removed_count = _to_int(safe_extract(result, "removed_count", 0), default=0)

        # Calculate stats
        total_count = len(context_chunks)
        kept_count = len(filtered_context)

        return {
            "filtered_context": filtered_context,
            "stats": {
                "total": total_count,
                "kept": kept_count,
                "removed": removed_count,
                "removal_rate": removed_count / total_count if total_count > 0 else 0.0,
            },
        }

    def _format_context(self, context_chunks: list[dict]) -> str:
        """Format context chunks as string for DSPy.

        Args:
            context_chunks: List of context dicts

        Returns:
            str: Formatted context string
        """
        lines: list[str] = []
        for i, chunk in enumerate(context_chunks, 1):
            text = chunk.get("text", "")
            source = chunk.get("source", "Unknown")
            lines.append(f"Chunk {i} (from {source}):")
            lines.append(f"  {text[:500]}...")  # Limit length
            lines.append("")

        return "\n".join(lines)

    def _parse_filtered_context(self, filtered_str: str) -> list[dict]:
        """Parse filtered context string back to list of dicts.

        Args:
            filtered_str: String output from DSPy filter

        Returns:
            list of dict with text and source
        """
        if not filtered_str:
            return []

        # Try to parse as JSON
        import json

        try:
            data = json.loads(filtered_str)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

        # Fallback: Parse line-by-line
        chunks = []
        current_chunk: dict[str, str] = {}

        for line in filtered_str.split("\n"):
            line = line.strip()
            if not line:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = {}
                continue

            # Parse key-value pairs
            if ": " in line:
                key, value = line.split(": ", 1)
                key = key.strip().lower()

                if key in ("text", "content"):
                    current_chunk["text"] = value
                elif key in ("source", "url"):
                    current_chunk["source"] = value

        # Don't forget last chunk
        if current_chunk:
            chunks.append(current_chunk)

        return chunks

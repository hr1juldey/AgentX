"""Context filtering logic and utilities.

Helper functions for context filtering and parsing.
"""

import json


def to_int(value: str | float | bool | None, default: int = 0) -> int:
    """Convert value to int safely.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        int: Converted integer value
    """
    from agentx.agent.tools.common.type_utils import _to_float

    try:
        return int(float(_to_float(value, default=default)))  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return default


def format_context(context_chunks: list[dict]) -> str:
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


def parse_filtered_context(filtered_str: str) -> list[dict]:
    """Parse filtered context string back to list of dicts.

    Args:
        filtered_str: String output from DSPy filter

    Returns:
        list of dict with text and source
    """
    if not filtered_str:
        return []

    # Try to parse as JSON
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

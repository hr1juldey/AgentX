# =============================================================================
# AGENTX Number Extractor Utilities
# =============================================================================
# Utility functions for LLM output processing
# =============================================================================


def strip_markdown_wrapper(text: str) -> str:
    """Strip markdown code block wrapper from LLM output.

    14B coder models wrap JSON in ``` blocks for readability.
    This strips the wrapper before JSON parsing.

    Args:
        text: Raw LLM output, possibly wrapped in ```

    Returns:
        Cleaned JSON string without markdown wrapper
    """
    if not text or not isinstance(text, str):
        return text

    text = text.strip()

    # Check for markdown code block wrapper
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove lines that are just ``` or ```json
        json_lines = [
            line for line in lines
            if not line.strip().startswith("```")
        ]
        return "\n".join(json_lines).strip()

    return text

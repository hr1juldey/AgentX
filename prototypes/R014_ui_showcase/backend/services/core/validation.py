# =============================================================================
# AGENTX Validation Infrastructure
# =============================================================================
# LLM response validation and parsing utilities
# =============================================================================

from typing import Any, Callable, List, Optional
import re


def validate_output(
    output: Any,
    validator: Callable[[Any], bool],
    on_invalid: Optional[Callable[[], Any]] = None,
) -> Any:
    """Validate LLM output and return fallback if invalid.

    Args:
        output: LLM output to validate
        validator: Function that returns True if output is valid
        on_invalid: Optional fallback function if validation fails

    Returns:
        Validated output or fallback
    """
    if validator(output):
        return output
    if on_invalid:
        return on_invalid()
    return None


def extract_list_from_text(text: str) -> List[str]:
    """Extract list items from LLM text output.

    Handles formats like:
    - "item1, item2, item3"
    - "- item1\\n- item2\\n- item3"
    - "1. item1\\n2. item2\\n3. item3"

    Args:
        text: Raw LLM output

    Returns:
        List of extracted items
    """
    if not text:
        return []

    # Try comma-separated first
    if "," in text and "\n" not in text:
        items = [item.strip() for item in text.split(",")]
        return [i for i in items if i]

    # Try bullet points
    bullet_items = re.findall(r"^[\-\*]\s+(.+)$", text, re.MULTILINE)
    if bullet_items:
        return [i.strip() for i in bullet_items]

    # Try numbered list
    numbered_items = re.findall(r"^\d+\.\s+(.+)$", text, re.MULTILINE)
    if numbered_items:
        return [i.strip() for i in numbered_items]

    # Fallback: split by newlines
    return [line.strip() for line in text.split("\n") if line.strip()]


def parse_numbered_list(text: str) -> List[str]:
    """Parse numbered list from LLM output.

    Handles formats like:
    - "1. First item\\n2. Second item"
    - "1) First item\\n2) Second item"

    Args:
        text: Raw LLM output

    Returns:
        List of items (without numbers)
    """
    if not text:
        return []

    items = []
    for line in text.split("\n"):
        line = line.strip()
        # Match "1." or "1)" format at start of line
        match = re.match(r"^\d+[\.\)]\s*(.+)$", line)
        if match:
            items.append(match.group(1))
        elif line and not line[0].isdigit():  # Non-numbered lines
            items.append(line)

    return items


def parse_float_score(score_str: str, default: float = 0.0) -> float:
    """Parse float score from LLM output with fallback.

    Handles formats like:
    - "0.75"
    - "The score is 0.75"
    - "75%"

    Args:
        score_str: String containing a score
        default: Default value if parsing fails

    Returns:
        Parsed float value or default
    """
    if not score_str:
        return default

    # Try direct float conversion
    try:
        return float(score_str.strip())
    except ValueError:
        pass

    # Try to extract a number using regex
    match = re.search(r"0?\.\d+|1\.0|0|1|\d+%", score_str)
    if match:
        try:
            value = float(match.group().rstrip("%"))
            # Handle percentages
            if "%" in match.group() and value > 1:
                return value / 100.0
            return value
        except ValueError:
            pass

    # Fallback: check for qualitative indicators
    lower = score_str.lower()
    if any(word in lower for word in ["high", "very", "strong", "excellent"]):
        return 0.8
    if any(word in lower for word in ["medium", "moderate", "good"]):
        return 0.5
    if any(word in lower for word in ["low", "weak", "poor"]):
        return 0.2

    return default

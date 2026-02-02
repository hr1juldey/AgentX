"""Temporal type classifier for memory.

Classifies memories into temporal types (FACT, PREFERENCE, STATE, EVENT, PLAN).
"""

from agentx.domain.entities.enums import TemporalType


def classify_temporal_type(content: str) -> TemporalType:
    """Classify memory by temporal type.

    Args:
        content: Memory content.

    Returns:
        TemporalType: Classified type.
    """
    content_lower = content.lower()

    # Preference patterns
    if any(
        word in content_lower
        for word in ["prefer", "like", "want", "choose", "favorite"]
    ):
        return TemporalType.PREFERENCE

    # State patterns
    if any(
        word in content_lower
        for word in ["status", "state", "condition", "current", "progress"]
    ):
        return TemporalType.STATE

    # Event patterns
    if any(
        word in content_lower
        for word in ["happened", "occurred", "meeting", "call", "discussed"]
    ):
        return TemporalType.EVENT

    # Plan patterns
    if any(
        word in content_lower
        for word in ["will", "plan", "schedule", "upcoming", "future", "tomorrow"]
    ):
        return TemporalType.PLAN

    # Default to fact
    return TemporalType.FACT

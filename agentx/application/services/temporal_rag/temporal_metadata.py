"""Temporal metadata enrichment for memory.

Adds temporal metadata to memories before storage.
"""

from datetime import datetime
from typing import Any

from agentx.domain.entities.enums import TemporalType
from agentx.application.services.temporal_rag.temporal_classifier import (
    classify_temporal_type,
)


def add_temporal_metadata(
    content: str, temporal_type: TemporalType | None = None
) -> dict[str, Any]:
    """Add temporal metadata to memory.

    Args:
        content: Memory content.
        temporal_type: Optional pre-classified type.

    Returns:
        dict: Temporal metadata.
    """
    now = datetime.now()

    if temporal_type is None:
        temporal_type = classify_temporal_type(content)

    return {
        "created_at": now,
        "modified_at": now,
        "valid_from": now,
        "valid_until": None,
        "temporal_type": temporal_type,
        "supersedes": [],
        "superseded_by": None,
    }

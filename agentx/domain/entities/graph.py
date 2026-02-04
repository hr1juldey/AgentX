"""Graph entity for LangGraph StateGraph specifications."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Graph:
    """Represents a LangGraph StateGraph specification.

    Attributes:
        id: Unique graph identifier
        spec: JSON graph specification
        metadata: Graph metadata (description, tags, etc.)
        score: Quality score from critic (0.0 to 1.0)
        created_at: Creation timestamp
        version: Graph version number
    """

    id: str
    spec: dict
    metadata: dict
    score: float
    created_at: datetime
    version: int

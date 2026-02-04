"""Execution entity for graph execution tracking."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Execution:
    """Represents a graph execution trace.

    Attributes:
        session: Session identifier
        trace: Execution trace (node visits, edges taken)
        result: Execution result
    """

    session: str
    trace: list[dict[str, Any]]
    result: dict[str, Any]

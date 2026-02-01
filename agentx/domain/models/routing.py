"""Domain models for routing decisions.

This module defines the models for state-driven routing decisions
including continuation decisions and research quality assessments.
"""

from enum import Enum

from pydantic import BaseModel, Field


class ContinuationAction(str, Enum):
    """Actions the evaluator can take."""

    CONTINUE_RESEARCH = "continue_research"
    FINALIZE = "finalize"
    ADD_TASKS = "add_tasks"


class ContinuationDecision(BaseModel):
    """Evaluator's decision on whether to continue research."""

    action: ContinuationAction = Field(
        description="continue_research, finalize, or add_tasks"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="LLM's confidence in current info (0.0-1.0)",
    )
    missing_information: list[str] = Field(
        default_factory=list,
        description="What's still needed",
    )
    reasoning: str = Field(description="Why this action")


class ResearchQuality(str, Enum):
    """Quality assessment of research findings."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RoutingPath(str, Enum):
    """Possible routing paths in the graph."""

    DIRECT_ANSWER = "direct_answer"
    CREATE_WORKERS = "create_workers"
    CONTINUE = "continue"
    FINALIZE = "finalize"
    ADD_TASKS = "add_tasks"

"""Domain models for query execution plans.

This module defines the ExecutionPlan and ResearchTask models for dynamic
worker creation based on query complexity.
"""

from enum import Enum

from pydantic import BaseModel, Field


class TaskType(str, Enum):
    """Types of research tasks."""

    SEARCH = "search"
    SUMMARIZE = "summarize"
    COMPARE = "compare"
    ANALYZE = "analyze"
    SYNTHESIZE = "synthesize"


class ResearchTask(BaseModel):
    """A single research task in the execution plan."""

    task_id: str = Field(description="Unique task identifier")
    task_type: TaskType = Field(description="Type of task")
    description: str = Field(description="What this task does")
    query: str = Field(description="Search query or prompt")

    # Dependency management
    dependencies: list[str] = Field(
        default_factory=list,
        description="Task IDs that must complete first",
    )

    # State tracking
    cached: bool = Field(
        default=False,
        description="True if result is in Store cache",
    )
    priority: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Task priority (1=lowest, 10=highest)",
    )

    # Outcome
    result: str | None = Field(
        default=None,
        description="Task result after execution",
    )


class ExecutionPlan(BaseModel):
    """Execution plan for query processing."""

    query: str = Field(description="Original user query")
    needs_research: bool = Field(description="Whether research is needed")

    research_tasks: list[ResearchTask] = Field(
        default_factory=list,
        description="List of research tasks (0-N)",
    )

    estimated_duration: int | None = Field(
        default=None,
        description="Estimated seconds to complete",
    )

    reasoning: str = Field(
        default="",
        description="Why this plan was chosen",
    )

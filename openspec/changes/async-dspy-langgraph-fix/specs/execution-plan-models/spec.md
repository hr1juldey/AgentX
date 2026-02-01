# Spec: Execution Plan Models

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Draft

---

## 1. Purpose

Define the Pydantic models for execution plans and research tasks.

**Success Criteria**:
- ExecutionPlan model with research tasks list
- ResearchTask model with dependencies
- TaskType enum for task categorization
- All models compatible with LangGraph state

---

## 2. Scope

### In Scope

- ExecutionPlan Pydantic model
- ResearchTask Pydantic model
- TaskType enum
- Task priority and caching fields

### Out of Scope

- Query planner logic (covered by query-planner spec)
- Task execution (covered by send-api-workers spec)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-EPM-001 | ExecutionPlan MUST have research_tasks list | Must |
| FR-EPM-002 | ResearchTask MUST have dependencies list | Must |
| FR-EPM-003 | ResearchTask MUST have cached flag | Must |
| FR-EPM-004 | TaskType enum MUST define all task types | Must |

---

## 4. Data Model

```python
# domain/models/query_plan.py
from pydantic import BaseModel, Field
from typing import List
from enum import Enum

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
    dependencies: List[str] = Field(
        default_factory=list,
        description="Task IDs that must complete first"
    )

    # State tracking
    cached: bool = Field(
        default=False,
        description="True if result is in Store cache"
    )
    priority: int = Field(
        default=5,
        ge=1, le=10,
        description="Task priority (1=lowest, 10=highest)"
    )

    # Outcome
    result: str | None = Field(
        default=None,
        description="Task result after execution"
    )

class ExecutionPlan(BaseModel):
    """Execution plan for query processing."""

    query: str = Field(description="Original user query")
    needs_research: bool = Field(description="Whether research is needed")

    research_tasks: List[ResearchTask] = Field(
        default_factory=list,
        description="List of research tasks (0-N)"
    )

    estimated_duration: int | None = Field(
        default=None,
        description="Estimated seconds to complete"
    )

    reasoning: str = Field(
        default="",
        description="Why this plan was chosen"
    )
```

---

## 5. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-EPM-001 | Task IDs unique | Validation in __init__ |
| BR-EPM-002 | No circular dependencies | Validation in __init__ |
| BR-EPM-003 | Priority 1-10 | Pydantic constraint |

---

## 6. Acceptance Criteria

- [ ] ExecutionPlan model created
- [ ] ResearchTask model created
- [ ] TaskType enum with all values
- [ ] Pyrefly type checking passes
- [ ] Models compatible with LangGraph State

---

## 7. Usage Example

```python
# Create execution plan
plan = ExecutionPlan(
    query="Compare iPhone vs Pixel",
    needs_research=True,
    research_tasks=[
        ResearchTask(
            task_id="search_iphone",
            task_type=TaskType.SEARCH,
            description="Search for iPhone reviews",
            query="iPhone 15 reviews 2024",
            priority=8,
        ),
        ResearchTask(
            task_id="search_pixel",
            task_type=TaskType.SEARCH,
            description="Search for Pixel reviews",
            query="Pixel 8 reviews 2024",
            priority=8,
        ),
        ResearchTask(
            task_id="compare",
            task_type=TaskType.COMPARE,
            description="Compare the phones",
            query="Compare iPhone 15 vs Pixel 8",
            dependencies=["search_iphone", "search_pixel"],
            priority=9,
        ),
    ],
    reasoning="Comparison requires research on both phones first",
)
```

---

**Next**: See `query-planner/spec.md` for planner module implementation.

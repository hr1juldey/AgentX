# Spec: Dynamic State-Driven Routing with Send API

**Domain**: agent-runtime
**Generated**: 2026-02-01
**Status**: Draft

---

## 1. Purpose

Define the dynamic routing system where the LLM uses accumulated state to decide execution paths via Send API. Workers are created DYNAMICALLY based on the execution plan, not pre-defined static nodes.

**Problem Statement**: R014 uses fragile text parsing (`"needs more research: true"`) for routing decisions and has a fixed 8-node pipeline regardless of query complexity.

**Success Criteria**:
- Zero tasks → direct answer (no workers created)
- Cached tasks → skipped (memory_id used directly)
- Parallel independent tasks → executed concurrently via Send
- Staged dependent tasks → executed in dependency order

---

## 2. Scope

### In Scope

- Send API for dynamic worker creation based on ExecutionPlan
- State-driven routing decisions (not static conditionals)
- Dependency resolution for staged execution
- Evaluator-optimizer for "continue research" decisions
- Mem0 memory integration for cached results

### Out of Scope

- Query planning (see query-complexity-assessment spec)
- STT preprocessing (see stt-preprocessing spec)
- Widget selection (see adaptive-widget-selection spec)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-DR-001 | Workers created dynamically via Send API | Must | LangGraph pattern |
| FR-DR-002 | Cached tasks skipped (memory_id used) | Must | Mem0 integration |
| FR-DR-003 | Independent tasks executed in parallel | Must | Send API |
| FR-DR-004 | Dependent tasks executed in order | Must | Dependency resolution |
| FR-DR-005 | Evaluator uses structured output (not text parsing) | Must | R014 fix |
| FR-DR-006 | State accumulated during execution for decisions | Must | State-driven |
| FR-DR-007 | Max iteration limit enforced (safety) | Should | Prevent loops |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority | Target Metric |
|----|-------------|----------|---------------|
| NFR-DR-001 | Routing decision latency | Must | < 100ms |
| NFR-DR-002 | No fragile string parsing | Must | Structured output only |
| NFR-DR-003 | State immutability | Should | Functional updates |
| NFR-DR-004 | Backwards compatible | Must | Works with existing state |

---

## 4. Data Model

### 4.1 LangGraph State Schema

```python
# agent/state/graph_state.py
from typing import Annotated, TypedDict, Optional
from langgraph.graph import add_messages

class AgentState(TypedDict):
    """Shared state for dynamic routing with Send API."""

    # Input
    messages: Annotated[list, add_messages]  # Conversation history
    query: str  # Original user query
    input_path: InputPath  # TEXT or STT

    # Execution plan
    execution_plan: ExecutionPlan  # From QueryPlannerModule
    current_iteration: int  # Current research iteration

    # Accumulated research (for state-driven decisions)
    research_findings: list[str]  # Accumulated findings
    research_sources: list[str]  # Source URLs/references
    task_results: dict[str, str]  # {task_id: result} including cached

    # State for decisions
    research_quality: Optional[ResearchQuality]  # Latest quality assessment
    accumulated_confidence: float  # Cumulative confidence (0.0-1.0)

    # Memory integration
    memory_hits: int  # Number of cached results used
    new_results_to_store: list[tuple[str, str]]  # [(task_id, result)] for Mem0

    # Output
    final_response: Optional[str]

    # Execution tracking
    visited_tasks: list[str]  # Tasks executed (to detect cycles)
    execution_path: list[str]  # Nodes visited (for debugging)
```

### 4.2 Routing Decision Struct

```python
# domain/models/routing.py
from pydantic import BaseModel, Field
from enum import Enum
from typing import Literal

class ContinuationDecision(BaseModel):
    """LLM-structured output for whether to continue researching."""
    action: Literal["continue_research", "finalize", "add_tasks"] = Field(
        description="What to do next based on accumulated state"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence in current information (0.0-1.0)"
    )
    missing_information: list[str] = Field(
        default_factory=list,
        description="What information is still needed"
    )
    additional_tasks: list[ResearchTask] = Field(
        default_factory=list,
        description="New tasks to add (if action='add_tasks')"
    )
    reasoning: str = Field(
        description="Why this action was chosen based on accumulated state"
    )

class ResearchQuality(BaseModel):
    """Quality assessment of accumulated research."""
    score: float = Field(
        ge=0.0, le=1.0,
        description="Quality score (0.0-1.0)"
    )
    sufficient: bool = Field(
        description="Whether findings are sufficient to answer"
    )
    gaps: list[str] = Field(
        default_factory=list,
        description="Information gaps remaining"
    )
    confidence_boost: float = Field(
        default=0.0,
        description="How much this boosts accumulated confidence"
    )
```

---

## 5. Architecture

### 5.1 Send API Worker Creation

```python
# agent/nodes/routing.py
from langgraph.types import Send
from typing import Literal

def route_by_plan(state: AgentState) -> Literal["direct_answer", "create_workers"]:
    """Route based on execution plan.

    Zero tasks → direct answer
    Cached tasks → load from memory
    New tasks → create workers via Send API
    """
    plan = state["execution_plan"]

    # Filter out cached tasks (they're already loaded)
    uncached_tasks = [t for t in plan.research_tasks if not t.cached]

    if len(uncached_tasks) == 0:
        return "direct_answer"
    else:
        return "create_workers"

def assign_workers(state: AgentState) -> list[Send]:
    """Create dynamic workers via Send API based on execution plan.

    This replaces R014's fixed pipeline with dynamic worker creation.
    """
    plan = state["execution_plan"]

    # Find ready tasks: dependencies satisfied, not yet visited
    visited = set(state.get("visited_tasks", []))
    ready_tasks = [
        t for t in plan.research_tasks
        if not t.cached  # Skip cached (already in state)
        and all(dep in visited for dep in t.dependencies)
        and t.task_id not in visited
    ]

    # Create Send for each ready task
    return [Send("research_worker", {"task": t}) for t in ready_tasks]

def should_continue_research(state: AgentState) -> Literal["continue", "finalize", "add_tasks"]:
    """Evaluator-optimizer: decide whether to continue based on accumulated state.

    This uses structured output (NOT string parsing like R014).
    """
    decision = state["continuation_decision"]
    iteration = state.get("current_iteration", 0)
    max_iterations = 5  # Safety limit

    # Check max iterations
    if iteration >= max_iterations:
        return "finalize"

    # Check LLM's structured decision
    if decision.action == "continue_research":
        return "continue"
    elif decision.action == "add_tasks":
        return "add_tasks"
    else:
        return "finalize"
```

### 5.2 Worker Node Pattern

```python
# agent/nodes/research_worker.py
from agentx.agent.tools.researcher.search_executor import SearchExecutorModule

async def research_worker_node(state: WorkerState) -> dict:
    """Execute a single research task.

    This node is created dynamically via Send API.
    """
    task: ResearchTask = state["task"]

    # Execute task based on type
    if task.task_type == TaskType.SEARCH:
        module = SearchExecutorModule()
        result = await module.aforward(query=task.query)
    elif task.task_type == TaskType.CONTEXTUALIZE:
        module = ContextualizerModule()
        result = await module.aforward(query=task.query, context=state["research_findings"])
    # ... other task types

    # Store result for Mem0
    return {
        "task_results": {task.task_id: result.text},
        "new_results_to_store": [(task.task_id, result.text)],
        "visited_tasks": [task.task_id],
    }
```

### 5.3 Graph Structure

```python
# agent/graph/dynamic_agent_graph.py
from langgraph.graph import StateGraph, END, START

# Build dynamic workflow
builder = StateGraph(AgentState)

# Add nodes
builder.add_node("query_planner", query_planner_node)
builder.add_node("direct_answer", direct_answer_node)
builder.add_node("research_worker", research_worker_node)
builder.add_node("evaluator", evaluator_node)
builder.add_node("synthesizer", synthesizer_node)

# Add edges
builder.add_edge(START, "query_planner")

# Conditional route based on plan
builder.add_conditional_edges(
    "query_planner",
    route_by_plan,
    {
        "direct_answer": "direct_answer",
        "create_workers": "assign_workers",  # Special node for Send API
    }
)

# Send API creates workers dynamically
builder.add_conditional_edges(
    "assign_workers",
    assign_workers,  # Returns list[Send]
    ["research_worker"]
)

# After workers complete, evaluate
builder.add_edge("research_worker", "evaluator")

# Evaluator decides: continue, finalize, or add tasks
builder.add_conditional_edges(
    "evaluator",
    should_continue_research,
    {
        "continue": "assign_workers",  # More tasks from original plan
        "add_tasks": "assign_workers",  # Add new tasks dynamically
        "finalize": "synthesizer",
    }
)

builder.add_edge("synthesizer", END)
builder.add_edge("direct_answer", END)

# Compile
dynamic_agent = builder.compile()
```

---

## 6. Business Rules

| Rule | Description | Enforcement | Source |
|------|-------------|-------------|--------|
| BR-DR-001 | Zero tasks → skip workers, direct answer | `route_by_plan()` | Performance |
| BR-DR-002 | Cached tasks → load from Mem0, skip execution | Worker checks `task.cached` | Cache hit |
| BR-DR-003 | Dependencies must be satisfied before execution | `assign_workers()` filter | Correctness |
| BR-DR-004 | Max 5 research iterations (safety) | `should_continue_research()` check | Safety |
| BR-DR-005 | Decisions use structured output only | `ContinuationDecision` model | R014 fix |
| BR-DR-006 | State accumulated across iterations | Reducers on state | State-driven |
| BR-DR-007 | Task results stored in Mem0 after execution | Worker nodes call `mem0.add()` | Future cache |

---

## 7. Acceptance Criteria

- [ ] Workers created dynamically via Send API (not fixed nodes)
- [ ] Cached tasks skipped with memory_id lookup
- [ ] Independent tasks executed in parallel
- [ ] Dependent tasks wait for dependencies
- [ ] Evaluator uses structured output (no text parsing)
- [ ] Max 5 iterations enforced
- [ ] Task results stored in Mem0
- [ ] Ruff and pyrefly checks pass

---

## 8. Test Scenarios

### 8.1 Simple Query (Zero Tasks)

| Query | Plan | Expected Execution |
|-------|------|-------------------|
| "What's 2+2?" | 0 tasks | direct_answer node, no workers |

### 8.2 Cached Query (Memory Hit)

| Query | Memory State | Expected Execution |
|-------|-------------|-------------------|
| "Compare iPhone 15 vs Pixel 8" (repeated) | Previous result in Mem0 | Tasks marked cached=True, workers skipped |

### 8.3 Parallel Independent Tasks

| Query | Plan | Expected Execution |
|-------|------|-------------------|
| "Compare iPhone 15 vs Pixel 8" | 2 independent tasks | 2 workers created, execute concurrently |

### 8.4 Staged Dependent Tasks

| Query | Plan | Expected Execution |
|-------|------|-------------------|
| "Analyze AI adoption in healthcare vs finance" | 3 tasks with dependencies | Task 1,2 parallel → Task 3 waits → executes |

### 8.5 Dynamic Task Addition

| Query | Scenario | Expected Behavior |
|-------|----------|-------------------|
| Complex query | After 2 iterations, quality still low | Evaluator adds new tasks to plan |

---

## 9. References

- **LangGraph Send API**: `tests/langgraph_workflows_agents.md` (lines 663-768)
- **LangGraph Orchestrator-Worker**: Same section - Dynamic worker pattern
- **LangGraph Evaluator-optimizer**: `tests/langgraph_workflows_agents.md` (lines 770-912)
- **R014 Analysis**: This spec fixes R014's "needs more research: true" parsing bug
- **DSPy Async**: `/home/riju279/Downloads/dspy-main/dspy-main/docs/docs/tutorials/async/index.md`
- **Mem0AI**: `docs/research/02_dspy_mem0_integration.md`

---

**Next**: See `stt-preprocessing/spec.md` for STT input handling.

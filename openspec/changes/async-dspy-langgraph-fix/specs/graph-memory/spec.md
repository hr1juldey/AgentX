# Spec: Graph Memory (Procedural Routing with Checkpointers)

**Domain**: agent-runtime
**Generated**: 2026-02-01
**Status**: Draft

---

## 1. Purpose

Define the graph memory system using LangGraph Checkpointers for procedural routing. This is "procedural memory" - the graph learns efficient execution paths based on past executions within a thread.

**Problem Statement**: R014 runs a fixed pipeline and forgets why it searched, leading to arbitrary widget dumps. Graph memory enables state-driven routing where the LLM evaluates accumulated state to decide "what do I know vs what do I need."

**Success Criteria**:
- Graph maintains conversation state across iterations
- Evaluator uses accumulated state to decide whether to continue researching
- Routing decisions are based on state (not fragile string parsing)
- Time-travel debugging: inspect and replay past graph states

---

## 2. Scope

### In Scope

- LangGraph Checkpointers for state persistence (InMemorySaver, PostgresSaver)
- State reducers for accumulation across iterations
- Evaluator-optimizer pattern for "continue or finalize" decisions
- Time-travel debugging (get_state_history, update_state)
- State-driven routing (not static conditionals)

### Out of Scope

- Agent memory (Store) - see episodic-memory spec for cached research
- STT preprocessing - see stt-preprocessing spec
- Transient UX patterns - see transient-ux spec

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-GM-001 | Graph state persisted across iterations | Must | Continuity |
| FR-GM-002 | Accumulate research findings in state | Must | State-driven |
| FR-GM-003 | Evaluator uses structured output (not text parsing) | Must | R014 fix |
| FR-GM-004 | Max iteration limit enforced (safety) | Must | Prevent loops |
| FR-GM-005 | Time-travel: inspect past states | Should | Debugging |
| FR-GM-006 | State updated with reducers (functional) | Should | Immutability |
| FR-GM-007 | thread_id for per-user isolation | Must | Multi-tenancy |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority | Target Metric |
|----|-------------|----------|---------------|
| NFR-GM-001 | State persistence latency | Must | < 50ms |
| NFR-GM-002 | Checkpoint size | Should | < 10 KB per checkpoint |
| NFR-GM-003 | Max checkpoints per thread | Should | 100-500 |
| NFR-GM-004 | Retention period | Should | 24-72 hours |

---

## 4. Data Model

### 4.1 Graph State Schema

```python
# agent/state/graph_state.py
from typing import Annotated, TypedDict, Optional
from langgraph.graph.message import add_messages
from operator import add

class AgentState(TypedDict):
    """Shared state for dynamic routing with graph memory."""

    # Input
    messages: Annotated[list, add_messages]  # Conversation history (with reducer)
    query: str  # Original user query
    input_path: InputPath  # TEXT or STT
    user_id: str  # User identifier (for isolation)
    session_id: str  # Session identifier

    # Execution plan
    execution_plan: ExecutionPlan  # From QueryPlannerModule
    current_iteration: int  # Current research iteration

    # Accumulated research (state for decisions)
    research_findings: Annotated[list[str], add]  # Accumulated findings
    research_sources: Annotated[list[str], add]  # Source URLs/references
    task_results: dict[str, str]  # {task_id: result}

    # State for evaluator decisions
    research_quality: Optional[ResearchQuality]  # Latest quality assessment
    accumulated_confidence: float  # Cumulative confidence (0.0-1.0)
    information_gaps: Annotated[list[str], add]  # Remaining gaps

    # Execution tracking
    visited_tasks: list[str]  # Tasks executed (to detect cycles)
    execution_path: Annotated[list[str], add]  # Nodes visited (for debugging)

    # Output
    final_response: Optional[str]

class ResearchQuality(BaseModel):
    """Quality assessment of accumulated research (structured output)."""
    score: float = Field(ge=0.0, le=1.0, description="Quality score (0.0-1.0)")
    sufficient: bool = Field(description="Whether findings are sufficient to answer")
    gaps: list[str] = Field(default_factory=list, description="Information gaps remaining")
    confidence_boost: float = Field(default=0.0, description="How much this boosts confidence")
    reasoning: str = Field(description="Why this quality assessment was made")

class ContinuationDecision(BaseModel):
    """LLM-structured output for whether to continue researching."""
    action: Literal["continue_research", "finalize", "add_tasks"] = Field(
        description="What to do next based on accumulated state"
    )
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in current information")
    missing_information: list[str] = Field(default_factory=list, description="What's still needed")
    additional_tasks: list[ResearchTask] = Field(default_factory=list, description="New tasks if action='add_tasks'")
    reasoning: str = Field(description="Why this action was chosen")
```

### 4.2 Checkpointer Configuration

```python
# infrastructure/memory/checkpointer_config.py
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.redis import RedisSaver
from langgraph.store.base import BaseStore

# Graph memory (Checkpointers) - for procedural routing
def get_checkpointer():
    """Get checkpointer for graph memory (short-term, per-thread state)."""
    # Use PostgresSaver for production, MemorySaver for testing
    DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"
    return PostgresSaver.from_conn_string(DB_URI)

# Agent memory (Store) - for cached research (long-term, cross-thread)
def get_store():
    """Get Store for agent memory (long-term, cross-thread semantic search)."""
    DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"
    from langgraph.store.postgres import PostgresStore
    return PostgresStore.from_conn_string(DB_URI)

# Compile graph with both memory types
graph = builder.compile(
    checkpointer=get_checkpointer(),  # Graph memory (procedural)
    store=get_store(),  # Agent memory (episodic)
)
```

---

## 5. Architecture

### 5.1 Evaluator-Optimizer Pattern

```python
# agent/nodes/evaluator.py
import dspy
from dspy import InputField, OutputField, Signature

class EvaluateProgressSignature(dspy.Signature):
    """Decide whether to continue researching based on accumulated state."""
    original_query = InputField(desc="The user's original query")
    accumulated_findings = InputField(desc="All research findings gathered so far")
    information_gaps = InputField(desc="Remaining information gaps")
    accumulated_confidence = InputField(desc="Current confidence level (0.0-1.0)")
    current_iteration = InputField(desc="Current iteration number")

    # Structured output (NOT text parsing)
    action = OutputField(desc="continue_research, finalize, or add_tasks")
    confidence = OutputField(desc="0.0 to 1.0 confidence in current information")
    missing_information = OutputField(desc="What information is still needed")
    reasoning = OutputField(desc="Why this action was chosen")

class EvaluatorNode:
    """Evaluate progress and decide next action."""

    def __init__(self):
        self.evaluate = dspy.Predict(EvaluateProgressSignature)

    def __call__(self, state: AgentState) -> dict:
        """Evaluate accumulated state and decide next action."""

        # Get accumulated state
        findings = "\n".join(state.get("research_findings", []))
        gaps = state.get("information_gaps", [])
        confidence = state.get("accumulated_confidence", 0.0)
        iteration = state.get("current_iteration", 0)

        # LLM evaluates progress (structured output!)
        result = self.evaluate(
            original_query=state["query"],
            accumulated_findings=findings,
            information_gaps=str(gaps),
            accumulated_confidence=str(confidence),
            current_iteration=str(iteration),
        )

        # Parse structured output
        decision = ContinuationDecision(
            action=result.action,
            confidence=float(result.confidence),
            missing_information=json.loads(result.missing_information) if result.missing_information else [],
            reasoning=result.reasoning,
        )

        # Update accumulated confidence
        new_confidence = max(confidence, decision.confidence)

        return {
            "continuation_decision": decision,
            "accumulated_confidence": new_confidence,
            "execution_path": ["evaluator"],
        }

def should_continue_research(state: AgentState) -> str:
    """Route based on evaluator's structured decision (NOT text parsing)."""
    decision = state.get("continuation_decision")
    iteration = state.get("current_iteration", 0)
    max_iterations = 5

    # Safety limit
    if iteration >= max_iterations:
        return "finalize"

    # Structured decision routing
    if decision.action == "continue_research":
        return "continue"
    elif decision.action == "add_tasks":
        return "add_tasks"
    else:
        return "finalize"
```

### 5.2 Graph Structure with Checkpointers

```python
# agent/graph/dynamic_agent_graph.py
from langgraph.graph import StateGraph, START, END
from infrastructure.memory.checkpointer_config import get_checkpointer, get_store

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
        "create_workers": "assign_workers",
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
    should_continue_research,  # Routing function
    {
        "continue": "assign_workers",
        "add_tasks": "assign_workers",
        "finalize": "synthesizer",
    }
)

builder.add_edge("synthesizer", END)
builder.add_edge("direct_answer", END)

# Compile with checkpointers (graph memory) and store (agent memory)
dynamic_agent = builder.compile(
    checkpointer=get_checkpointer(),  # Procedural memory (short-term)
    store=get_store(),  # Episodic memory (long-term)
)
```

### 5.3 Time-Travel Debugging

```python
# application/debugging/time_travel.py
from langgraph.checkpoint import BaseCheckpointSaver

def inspect_graph_state(thread_id: str, checkpoint_id: str = None):
    """Inspect past graph states for debugging."""

    checkpointer = get_checkpointer()

    # Get state history for this thread
    config = {"configurable": {"thread_id": thread_id}}

    # Get specific checkpoint
    if checkpoint_id:
        state = checkpointer.get(config, checkpoint_id)
        print(f"Checkpoint {checkpoint_id}:")
        print(f"  Query: {state.values.get('query')}")
        print(f"  Iteration: {state.values.get('current_iteration')}")
        print(f"  Findings: {len(state.values.get('research_findings', []))}")
        return state

    # List all checkpoints
    for checkpoint in checkpointer.list(config):
        print(f"Checkpoint: {checkpoint.id}")
        print(f"  Timestamp: {checkpoint.ts}")
        print(f"  Step: {checkpoint.step}")
        print(f"  Next: {checkpoint.next}")

def replay_from_checkpoint(thread_id: str, checkpoint_id: str):
    """Replay graph execution from a specific checkpoint."""

    config = {
        "configurable": {
            "thread_id": thread_id,
            "checkpoint_id": checkpoint_id,
        }
    }

    # Continue execution from checkpoint
    result = dynamic_agent.invoke(
        {"query": "Continue from here"},
        config=config,
    )

    return result

def modify_and_replay(thread_id: str, checkpoint_id: str, modifications: dict):
    """Modify a checkpoint and replay (for testing alternative paths)."""

    checkpointer = get_checkpointer()
    config = {"configurable": {"thread_id": thread_id}}

    # Get original checkpoint
    original = checkpointer.get_tuple(config, checkpoint_id)

    # Apply modifications
    modified_state = {**original.channel_values, **modifications}

    # Create new checkpoint with modifications
    checkpointer.put(
        config,
        modified_state,
        original.metadata,
        original.config,
    )

    # Replay from modified checkpoint
    return replay_from_checkpoint(thread_id, checkpoint_id)
```

---

## 6. Business Rules

| Rule | Description | Enforcement | Source |
|------|-------------|-------------|--------|
| BR-GM-001 | State accumulated with reducers (functional updates) | Annotated[list, add] | Immutability |
| BR-GM-002 | Evaluator uses structured output only | ContinuationDecision model | R014 fix |
| BR-GM-003 | Max 5 iterations enforced | Routing function checks | Safety |
| BR-GM-004 | thread_id isolates conversations | Configurable thread_id | Multi-tenancy |
| BR-GM-005 | State persisted after each node | Checkpointer auto-saves | Continuity |
| BR-GM-006 | Routing based on accumulated state | Evaluator reads state | State-driven |
| BR-GM-007 | Time-travel via get_state_history | Checkpointer API | Debugging |

---

## 7. Acceptance Criteria

- [ ] Graph state persisted across iterations
- [ ] Research findings accumulated with reducers
- [ ] Evaluator uses structured output (no text parsing)
- [ ] Max 5 iterations enforced
- [ ] thread_id isolates user conversations
- [ ] Time-travel: can inspect past states
- [ ] Can replay from checkpoint
- [ ] Can modify and replay (alternative paths)
- [ ] Routing decisions based on accumulated state
- [ ] Ruff and pyrefly checks pass

---

## 8. Test Scenarios

### 8.1 State Accumulation

| Iteration | research_findings | accumulated_confidence |
|-----------|-------------------|------------------------|
| 0 | [] | 0.0 |
| 1 | ["Finding 1"] | 0.3 |
| 2 | ["Finding 1", "Finding 2"] | 0.6 |
| 3 | ["Finding 1", "Finding 2", "Finding 3"] | 0.85 |

### 8.2 Evaluator Decision

| Accumulated Confidence | Gaps Remaining | Expected Action |
|------------------------|----------------|-----------------|
| 0.9 | [] | finalize |
| 0.4 | ["key info missing"] | continue_research |
| 0.6 | ["minor detail"] | finalize (good enough) |

### 8.3 Time-Travel

| Operation | Expected Result |
|-----------|-----------------|
| get_state_history(thread_id) | List all checkpoints |
| get(thread_id, checkpoint_id) | Specific state snapshot |
| replay_from_checkpoint | Continue from that point |
| modify_and_replay | Test alternative decisions |

---

## 9. Biological Inspiration: Procedural Memory

Graph memory is inspired by biological **procedural memory**:

| Biological | Graph Memory |
|------------|--------------|
| Corticostriatal circuits (habit) | Checkpointers (routing patterns) |
| Chunking (grouping actions) | State accumulation (findings → decisions) |
| Model-free RL (stimulus-response) | Evaluator routing (state → action) |
| Skill learning with practice | Graph improves with more executions |

**Key insight**: The graph "learns" efficient paths by:
1. Accumulating state (experience)
2. Evaluating progress (dopamine-like quality signals)
3. Routing decisions based on state (habitual responses)

Unlike agent memory (episodic facts), graph memory is **procedural** - it's about **how to navigate** the problem, not **what was found**.

---

## 10. References

- **LangGraph Checkpointers**: `tests/langgraph_memory.md` (lines 841-1116)
- **Time Travel**: `tests/langgraph_memory.md` (lines 1116-1380)
- **Evaluator-Optimizer**: `tests/langgraph_workflows_agents.md` (lines 770-912)
- **Biological Procedural Memory**: tavily_research on corticostriatal circuits, chunking, RL
- **R014 Analysis**: This spec fixes R014's "forgot why it searched" problem

---

## 11. Memory Types Clarification

**TWO TYPES OF MEMORY** (don't confuse them):

| Type | Purpose | Implementation | Duration | Analogy |
|------|---------|----------------|----------|---------|
| **Graph Memory** | Procedural routing, how to navigate | Checkpointers (PostgresSaver) | Per-thread | "Muscle memory" |
| **Agent Memory** | Cached research, what was found | Store (PostgresStore) | Cross-thread | "Work experience" |

**This spec** defines Graph Memory (Checkpointers).
**See `episodic-memory/spec.md`** for Agent Memory (Store).

---

**Next**: See `stt-preprocessing/spec.md` for STT input handling.

# Design Artifact: async-dspy-langgraph-fix

**Generated**: 2026-02-01
**Change**: async-dspy-langgraph-fix
**Schema**: spec-factory v1.0.0

---

## 1. Architecture Overview

### 1.1 System Vision: Dynamic State-Driven Graph Assembly

The system is NOT a fixed pipeline. It's a **dynamically assembled execution graph** where:

1. **LLM generates execution plan** based on query complexity
2. **Send API creates workers dynamically** based on plan (no fixed nodes)
3. **State drives routing decisions** - "what do I know vs what do I need?"
4. **Two memory types** work together:
   - **Graph Memory (Checkpointers)**: Procedural routing, "how to navigate"
   - **Agent Memory (Store)**: Cached research, "what was found"

### 1.2 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Dynamic Query-Driven Agent                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────┐     ┌──────────────┐     ┌─────────────────────┐   │
│   │ User Input  │────▶│ Query Planner │────▶│  Execution Plan      │   │
│   │ (TEXT/STT)  │     │  (LLM)        │     │  (0 to N tasks)       │   │
│   └─────────────┘     └──────────────┘     └──────────┬──────────┘   │
│                                                     │                │
│                         ┌─────────────────────────┴────────┐   │
│                         ▼                                  │   │
│              ┌───────────────────────┐                   │   │
│              │  Agent Memory Check   │                   │   │
│              │  (Store: Search cached│                   │   │
│              │   research results)  │                   │   │
│              └───────────┬───────────┘                   │   │
│                          │ cached tasks?                  │   │
│              ┌───────────▼────────────┐                  │   │
│              │ Route by Plan           │                  │   │
│              │ 0 tasks → Direct Answer  │                  │   │
│              │ N tasks → Send Workers   │                  │   │
│              └───────────┬────────────┘                  │   │
│                          │                               │   │
│         ┌────────────────┼────────────────┐                │   │
│         ▼                ▼                ▼                │   │
│   ┌──────────┐    ┌───────────┐    ┌──────────┐           │   │
│   │  Direct  │    │  Send API │    │ Research │           │   │
│   │  Answer  │    │  Dynamic  │    │  Workers │           │   │
│   │  Node    │    │  Workers  │    │ (0 to N) │           │   │
│   └──────────┘    └─────┬─────┘    └─────┬─────┘           │   │
│                       │                 │                   │   │
│                       │                 └──────┬──────┐       │   │
│                       │                        │          │       │   │
│                       │                        ▼          │       │   │
│                       │              ┌──────────────────┐   │   │
│                       │              │ Graph Memory     │   │   │
│                       │              │ (Checkpointers)  │   │   │
│                       │              │ - Accumulate     │   │   │
│                       │              │ - State-driven   │   │   │
│                       │              │   routing        │   │   │
│                       │              └────────┬─────────┘   │   │
│                       │                       │             │   │
│                       │              ┌────────▼─────────┐   │   │
│                       │              │  Evaluator       │   │   │
│                       │              │  (LLM: "Enough?") │   │   │
│                       │              └────────┬─────────┘   │   │
│                       │                       │             │   │
│                       │        ┌──────────────┴──────┐  │   │
│                       │        ▼                     ▼  │   │
│                       │   ┌──────────┐      ┌──────────┐│   │
│                       │   │Continue  │      │Finalize  ││   │
│                       │   │Research  │      │Response  ││   │
│                       │   └────┬─────┘      └────┬─────┘│   │
│                       │        │                   │     │   │
│                       └────────┼───────────────────┘     │   │
│                                ▼                       │   │
│                       ┌───────────────────┐             │   │
│                       │ Transient UX       │             │   │
│                       │ - Streaming         │             │   │
│                       │ - Skeleton screens  │             │   │
│                       │ - Progress events   │             │   │
│                       └───────────────────┘             │   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Clean Architecture Layer Structure

```
agentx/
├── core/                          # Configuration
│   ├── config.py                  # DSPy + memory settings
│   └── dependencies.py            # Store + checkpointer singletons
│
├── domain/                        # Business logic (no external deps)
│   ├── models/                    # Pydantic models
│   │   ├── query_plan.py          # ExecutionPlan, ResearchTask
│   │   ├── graph_state.py         # AgentState, reducers
│   │   ├── routing.py              # ContinuationDecision, ResearchQuality
│   │   └── episodic_memory.py     # EpisodicMemory, TemporalMetadata
│   └── services/                  # Domain service protocols
│       ├── query_planner.py       # IQueryPlanner
│       └── memory_manager.py      # IMemoryManager
│
├── application/                   # Use cases
│   └── use_cases/
│       ├── plan_query.py          # GenerateExecutionPlan
│       ├── evaluate_progress.py   # ShouldContinueResearch
│       └── manage_memory.py       # Consolidate/forget memories
│
├── infrastructure/                # External concerns
│   ├── memory/
│   │   ├── langgraph_store_adapter.py  # EpisodicMemoryStore
│   │   └── checkpointer_config.py     # get_checkpointer()
│   └── external/
│       └── ollama.py               # LLM backend
│
└── agent/                         # LangGraph graph
    ├── graph/
    │   └── dynamic_agent_graph.py  # StateGraph compilation
    ├── nodes/                     # Graph nodes
    │   ├── query_planner.py        # GenerateExecutionPlan
    │   ├── stt_preprocessor.py     # Preprocess STT input
    │   ├── route_by_plan.py        # Conditional routing
    │   ├── assign_workers.py       # Send API worker creation
    │   ├── research_worker.py      # Execute research task
    │   ├── evaluator.py            # ShouldContinueResearch
    │   ├── synthesizer.py          # Generate final response
    │   └── direct_answer.py         # Skip research for simple queries
    └── tools/                     # DSPy modules
        ├── planner/                # QueryPlannerModule
        ├── evaluator/              # EvaluateProgressModule
        └── researcher/             # SearchExecutorModule (etc.)
```

---

## 2. State-Driven Decision Making

### 2.1 The Core Insight

**R014's Problem**: "Searches more if quality is low, then forgets why it searched"

**Solution**: The graph maintains **accumulated state** and the LLM evaluates "what do I know vs what do I need" at each iteration.

### 2.2 State Accumulation Pattern

```python
# agent/state/graph_state.py
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from operator import add

class AgentState(TypedDict):
    """Shared state for state-driven routing."""

    # Input
    messages: Annotated[list, add_messages]
    query: str
    input_path: InputPath  # TEXT or STT
    preprocessed_query: Optional[str]  # After STT preprocessing
    user_id: str
    session_id: str

    # Execution plan
    execution_plan: ExecutionPlan
    current_iteration: int

    # ACCUMULATED STATE (for state-driven decisions)
    research_findings: Annotated[list[str], add]  # ← Accumulates!
    research_sources: Annotated[list[str], add]  # ← Accumulates!
    task_results: dict[str, str]  # {task_id: result}
    information_gaps: Annotated[list[str], add]  # ← Accumulates!

    # State for evaluator decisions
    accumulated_confidence: float  # ← Increases with each finding
    research_quality: Optional[ResearchQuality]  # LLM's assessment

    # Execution tracking
    visited_tasks: list[str]  # Tasks executed
    execution_path: Annotated[list[str], add]  # Nodes visited

    # Output
    final_response: Optional[str]
```

### 2.3 Evaluator-Optimizer Pattern

```python
# agent/nodes/evaluator.py
import dspy
from dspy import InputField, OutputField, Signature

class EvaluateProgressSignature(dspy.Signature):
    """LLM evaluates: "Do I have enough to answer?" (STRUCTURED OUTPUT!)"""
    original_query = InputField(desc="User's original query")
    accumulated_findings = InputField(desc="All research gathered so far")
    accumulated_confidence = InputField(desc="Current confidence (0.0-1.0)")
    information_gaps = InputField(desc="What's still missing")
    current_iteration = InputField(desc="Iteration number")

    # Structured output (NOT text parsing!)
    action = OutputField(desc="continue_research, finalize, or add_tasks")
    confidence = OutputField(desc="LLM's confidence in current info (0.0-1.0)")
    missing_information = OutputField(desc="What's still needed")
    reasoning = OutputField(desc="Why this action")

class EvaluatorNode:
    def __call__(self, state: AgentState) -> dict:
        """Evaluate accumulated state - LLM decides next action."""

        findings = "\n".join(state.get("research_findings", []))
        gaps = state.get("information_gaps", [])
        confidence = state.get("accumulated_confidence", 0.0)
        iteration = state.get("current_iteration", 0)

        # LLM evaluates progress (STRUCTURED OUTPUT!)
        result = self.evaluate(
            original_query=state["query"],
            accumulated_findings=findings,
            accumulated_confidence=str(confidence),
            information_gaps=str(gaps),
            current_iteration=str(iteration),
        )

        # Parse structured output into decision
        decision = ContinuationDecision(
            action=result.action,  # "continue_research", "finalize", or "add_tasks"
            confidence=float(result.confidence),
            missing_information=json.loads(result.missing_information),
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
    """Route based on evaluator's STRUCTURED decision (no text parsing!)."""
    decision = state.get("continuation_decision")
    iteration = state.get("current_iteration", 0)
    max_iterations = 5

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

---

## 3. Dynamic Worker Creation with Send API

### 3.1 Send API Pattern

```python
# agent/nodes/routing.py
from langgraph.types import Send

def route_by_plan(state: AgentState) -> str:
    """Route based on execution plan.

    Key insight: Zero tasks → direct answer (no Send API needed).
    """

    plan = state["execution_plan"]

    # Filter out cached tasks (already loaded from Store)
    uncached_tasks = [t for t in plan.research_tasks if not t.cached]

    if len(uncached_tasks) == 0:
        return "direct_answer"
    else:
        return "create_workers"

def assign_workers(state: AgentState) -> list[Send]:
    """Create DYNAMIC workers via Send API based on execution plan.

    This is NOT a fixed pipeline. Workers are created DYNAMICALLY based on:
    - Plan's task list
    - Dependencies (respect task.dependencies)
    - Already-visited tasks (avoid cycles)
    """

    plan = state["execution_plan"]
    visited = set(state.get("visited_tasks", []))

    # Find ready tasks: deps satisfied, not visited, not cached
    ready_tasks = [
        t for t in plan.research_tasks
        if not t.cached
        and all(dep in visited for dep in t.dependencies)
        and t.task_id not in visited
    ]

    # DYNAMIC worker creation - one Send per ready task
    return [Send("research_worker", {"task": t}) for t in ready_tasks]
```

### 3.2 Graph Structure

```python
# agent/graph/dynamic_agent_graph.py
from langgraph.graph import StateGraph, START, END

builder = StateGraph(AgentState)

# Add nodes
builder.add_node("query_planner", query_planner_node)
builder.add_node("direct_answer", direct_answer_node)
builder.add_node("research_worker", research_worker_node)
builder.add_node("evaluator", evaluator_node)
builder.add_node("synthesizer", synthesizer_node)

# Entry point: plan query
builder.add_edge(START, "query_planner")

# DYNAMIC routing based on plan
builder.add_conditional_edges(
    "query_planner",
    route_by_plan,
    {
        "direct_answer": "direct_answer",
        "create_workers": "assign_workers",
    }
)

# Send API creates DYNAMIC workers
builder.add_conditional_edges(
    "assign_workers",
    assign_workers,  # Returns list[Send]
    ["research_worker"]  # Dynamic target
)

# After worker completes, evaluate progress
builder.add_edge("research_worker", "evaluator")

# Evaluator decides: continue, add tasks, or finalize
builder.add_conditional_edges(
    "evaluator",
    should_continue_research,
    {
        "continue": "assign_workers",
        "add_tasks": "assign_workers",
        "finalize": "synthesizer",
    }
)

builder.add_edge("synthesizer", END)
builder.add_edge("direct_answer", END)

# Compile with BOTH memory types
dynamic_agent = builder.compile(
    checkpointer=get_checkpointer(),  # Graph memory (procedural)
    store=get_store(),  # Agent memory (episodic)
)
```

---

## 4. Two Memory Types

### 4.1 Memory Architecture

| Type | Purpose | Implementation | Analogy | Duration |
|------|---------|----------------|---------|----------|
| **Graph Memory** | Procedural routing, "how to navigate" | Checkpointers (PostgresSaver) | "Muscle memory" | Per-thread |
| **Agent Memory** | Cached research, "what was found" | Store (PostgresStore) | "Work experience" | Cross-thread |

### 4.2 Graph Memory (Checkpointers) - Procedural

```python
# infrastructure/memory/checkpointer_config.py
from langgraph.checkpoint.postgres import PostgresSaver

def get_checkpointer():
    """Get checkpointer for graph memory."""
    DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"
    return PostgresSaver.from_conn_string(DB_URI)

# Compile graph
graph = builder.compile(
    checkpointer=get_checkpointer(),  # ← Graph memory
)

# Time-travel: inspect past states
state = graph.get_state(config)
for checkpoint in graph.get_state_history(config):
    print(f"Step {checkpoint.step}: {checkpoint.values}")
```

### 4.3 Agent Memory (Store) - Episodic

```python
# infrastructure/memory/langgraph_store_adapter.py
from langgraph.store.postgres import PostgresStore

class EpisodicMemoryStore:
    """Agent memory: cached research results."""

    async def store_research_result(
        self,
        query: str,
        user_id: str,
        summary: str,
        result: str,
    ) -> str:
        """Store research result for future reuse."""

        memory_id = str(uuid.uuid4())
        query_hash = hashlib.sha256(query.lower().encode()).hexdigest()
        namespace = ("research", query_hash)

        # Create memory with C005 temporal metadata
        memory = EpisodicMemory(
            memory_id=memory_id,
            query=query,
            summary=summary,
            result=result,
            temporal=TemporalMetadata(
                created_at=datetime.now(),
                modified_at=datetime.now(),
                valid_from=datetime.now(),
                valid_until=None,  # Still valid
                temporal_type=TemporalType.RESEARCH,
                supersedes=[],
                superseded_by=None,
            ),
            outcome_quality=OutcomeQuality.HIGH,
        )

        await self.store.aput(namespace, memory_id, memory.model_dump())
        return memory_id

    async def search_research_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 5,
    ) -> list[EpisodicMemory]:
        """Search for relevant cached research."""

        query_hash = hashlib.sha256(query.lower().encode()).hexdigest()
        namespace = ("research", query_hash)

        items = await self.store.asearch(
            namespace,
            query=query,
            limit=limit,
        )

        return [EpisodicMemory(**item.value) for item in items]
```

---

## 5. Biological Inspiration: Procedural Memory

### 5.1 From Neuroscience Research

The graph memory design is inspired by biological **procedural memory**:

| Biological | Graph Memory |
|------------|--------------|
| **Corticostriatal circuits** (habit formation) | Checkpointers (routing patterns) |
| **Chunking** (grouping actions into subunits) | State accumulation (findings → decisions) |
| **Model-free RL** (stimulus-response) | Evaluator routing (state → action) |
| **Dopamine prediction errors** | ResearchQuality scores |
| **Skill learning with practice** | Graph improves with executions |

### 5.2 Two-Stage Learning

Biological systems use two-stage learning:

1. **Within-session**: Rapid improvement (acquisition phase)
2. **Offline consolidation**: Sleep-dependent stabilization (6-8 hours later)

Our graph mirrors this:

1. **Within-query**: State accumulates, evaluator decides when enough
2. **Across-queries**: Cached in Store, available for future queries

---

## 6. Transient UX for Long-Running Tasks

### 6.1 UX Problem

**User insight**: "Even if a task takes 15 minutes, humans won't wait and will leave."

**Solution**: Keep users engaged with transient UX patterns:
- Skeleton screens (appear within 300ms)
- Streaming responses (token-by-token)
- Progress events (every 1-2s)
- "Continue in background?" prompt (after 15s)

### 6.2 Streaming Response Flow

```python
# agent/nodes/synthesizer.py
from typing import AsyncGenerator

async def synthesizer_node(state: AgentState) -> AsyncGenerator[dict, None]:
    """Synthesize with streaming - keep users engaged."""

    findings = state.get("research_findings", [])
    query = state["query"]

    # Stream tokens to frontend
    for token in stream_response(query, findings):
        yield {
            "streaming_event": TokenEvent(token=token),
        }

    yield {
        "final_response": "".join(tokens),
    }
```

---

## 7. Technical Decisions

| Decision | Option Chosen | Alternatives | Rationale |
|----------|--------------|--------------|-----------|
| **State-driven routing** | LLM evaluates accumulated state | Static conditionals | "What do I know?" question |
| **Worker creation** | Send API (dynamic) | Fixed nodes | Scalable, flexible |
| **Memory separation** | Checkpointers + Store | Single memory type | Clear responsibilities |
| **Output format** | Structured (Pydantic) | Text parsing | R014 bug fixed |

---

## 8. Rollout Plan

1. **Phase 1**: Graph memory (Checkpointers) + evaluator
2. **Phase 2**: Agent memory (Store) + cache lookup
3. **Phase 3**: Send API dynamic workers
4. **Phase 4**: Transient UX streaming
5. **Phase 5**: STT preprocessing
6. **Phase 6**: Integration testing

---

## 9. References

- **LangGraph Send API**: `tests/langgraph_workflows_agents.md` (lines 663-768)
- **Evaluator-Optimizer**: `tests/langgraph_workflows_agents.md` (lines 770-912)
- **LangGraph Memory**: `tests/langgraph_memory.md`
- **C005 Memory Specs**: Temporal metadata, consolidation patterns
- **Biological Procedural Memory**: tavily_research on corticostriatal circuits
- **Transient UX Research**: tavily_research on long-running AI task UX

---

**Next**: See `validate.md` for validation against requirements.

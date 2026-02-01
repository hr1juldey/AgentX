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

```bash
┌─────────────────────────────────────────────────────────────────────────┐
│                    Dynamic Query-Driven Agent                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────┐     ┌──────────────┐     ┌─────────────────────┐      │
│   │ User Input  │────▶│ Query Planner │────▶│  Execution Plan    │      │
│   │ (TEXT/STT)  │     │  (LLM)        │     │  (0 to N tasks)    │      │
│   └─────────────┘     └──────────────┘     └──────────┬──────────┘      │
│                                                     │                   │
│                         ┌─────────────────────────┴────────┐            │
│                         ▼                                  │            │
│              ┌───────────────────────┐                     │            │
│              │  Agent Memory Check   │                     │            │
│              │  (Store: Search cached│                     │            │
│              │   research results)   │                     │            │
│              └───────────┬───────────┘                     │            │
│                          │ cached tasks?                   │            │
│              ┌───────────▼────────────┐                    │            │
│              │ Route by Plan          │                    │            │
│              │ 0 tasks → Direct Answer│                    │            │
│              │ N tasks → Send Workers │                    │            │
│              └───────────┬────────────┘                    │            │
│                          │                                 │            │
│         ┌────────────────┼────────────────┐                │            │
│         ▼                ▼                ▼                │            │
│   ┌──────────┐    ┌───────────┐    ┌──────────┐            │            │
│   │  Direct  │    │  Send API │    │ Research │            │            │
│   │  Answer  │    │  Dynamic  │    │  Workers │            │            │
│   │  Node    │    │  Workers  │    │ (0 to N) │            │            │
│   └──────────┘    └─────┬─────┘    └─────┬─────┘           │            │
│                       │                 │                  │            │
│                       │                 └──────┬──────┐    │            │
│                       │                        │      │    │            │
│                       │                        ▼      │    │            │
│                       │              ┌──────────────────┐   │           │
│                       │              │ Graph Memory     │   │           │
│                       │              │ (Checkpointers)  │   │           │
│                       │              │ - Accumulate     │   │           │
│                       │              │ - State-driven   │   │           │
│                       │              │   routing        │   │           │
│                       │              └────────┬─────────┘   │           │
│                       │                       │             │           │
│                       │              ┌────────▼─────────┐   │           │
│                       │              │  Evaluator       │   │           │
│                       │              │  (LLM: "Enough?")│   │           │
│                       │              └────────┬─────────┘   │           │
│                       │                       │             │           │
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

```bash
agentx/
├── core/                          # Configuration
│   ├── config.py                  # DSPy + memory settings
│   ├── memory_config.py           # ColBERT + Qdrant + Mem0 settings
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
│       ├── manage_memory.py       # Consolidate/forget memories
│       └── temporal_rag.py        # Time-aware RAG with 0.85 threshold
│
├── infrastructure/                # External concerns
│   ├── memory/
│   │   ├── langgraph_store_adapter.py  # EpisodicMemoryStore (agent memory)
│   │   ├── checkpointer_config.py     # get_checkpointer() (graph memory)
│   │   ├── qdrant_vector_store.py     # ColBERT multivector storage
│   │   └── mem0_adapter.py            # Mem0AI consolidation
│   └── external/
│       ├── ollama.py               # LLM backend
│       ├── searxng.py              # Web search integration
│       └── colbert_embedder.py     # ColBERTv2 late interaction
│
└── agent/                         # LangGraph graph
    ├── graph/
    │   └── dynamic_agent_graph.py  # StateGraph compilation
    ├── nodes/                     # LangGraph nodes (async wrappers)
    │   ├── query_planner.py        # GenerateExecutionPlan
    │   ├── stt_preprocessor.py     # Preprocess STT input
    │   ├── route_by_plan.py        # Conditional routing
    │   ├── assign_workers.py       # Send API worker creation
    │   ├── research_worker.py      # Execute research task
    │   ├── evaluator.py            # ShouldContinueResearch
    │   ├── synthesizer.py          # Generate final response
    │   └── direct_answer.py        # Skip research for simple queries
    ├── react_agents/               # 🔴 CRITICAL: ReAct orchestration layer
    │   ├── coordinator_agent.py    # Main: deploys sub-agents
    │   ├── research_agent.py       # Research domain (limited tools)
    │   ├── widget_agent.py         # Widget generation (limited tools)
    │   ├── synthesis_agent.py      # Response synthesis (limited tools)
    │   └── memory_agent.py         # Memory operations (limited tools)
    └── tools/                     # DSPy modules (atomic operations)
        ├── planner/                # QueryPlannerModule
        ├── evaluator/              # EvaluateProgressModule
        ├── researcher/             # SearchExecutorModule, SearXNGSearch
        ├── widgets/                # WidgetSelectorModule
        ├── synthesis/              # SynthesizerModule
        └── memory/                 # MemoryRetrievalModule, MemoryStoreModule
```

**Key Architecture Layers** (bottom to top):

1. **DSPy Tools** (`agent/tools/`): Atomic operations with class-based signatures
2. **ReAct Agents** (`agent/react_agents/`): Limited-tool orchestration with reasoning
3. **LangGraph Nodes** (`agent/nodes/`): Graph node wrappers (async/sync bridge)
4. **Dynamic Graph** (`agent/graph/`): State-driven routing with Send API

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

## 5. ReAct Agent Hierarchy: Main Deploys Sub-Agents

### 5.1 The Coordinator Pattern

**Problem**: A single ReAct agent with 20+ tools causes hallucination and poor performance.

**Solution**: Main Coordinator Agent deploys specialized sub-agents with limited tools (3-5 tools each).

```python
# agent/react_agents/coordinator_agent.py
import dspy
from dspy import InputField, OutputField, Signature

class CoordinatorSignature(dspy.Signature):
    """Coordinator decides which sub-agent to deploy."""
    query: str = InputField(desc="User's original query")
    conversation_history: str = InputField(desc="Previous messages")
    available_agents: str = InputField(desc="List of available sub-agents")

    # Structured output
    selected_agent: str = OutputField(desc="Which sub-agent to deploy (research/widget/synthesis/memory/direct)")
    reasoning: str = OutputField(desc="Why this agent")
    sub_task: str = OutputField(desc="Specific task for the sub-agent")

class CoordinatorAgent(dspy.Module):
    """Main coordinator that deploys specialized sub-agents.

    Each sub-agent has LIMITED tools (3-5 max) to prevent hallucination.
    """

    def __init__(self, research_agent, widget_agent, synthesis_agent, memory_agent):
        super().__init__()
        self.decide = dspy.Predict(CoordinatorSignature)

        # Sub-agents (each with limited tools)
        self.research_agent = research_agent      # 3 tools: search, scrape, cite
        self.widget_agent = widget_agent          # 3 tools: select_widgets, render_card, show_chart
        self.synthesis_agent = synthesis_agent    # 3 tools: summarize, format_text, check_quality
        self.memory_agent = memory_agent          # 3 tools: store_memory, search_memory, consolidate

    def forward(self, query: str, conversation_history: str) -> dspy.Prediction:
        """Decide which sub-agent handles this query."""
        decision = self.decide(
            query=query,
            conversation_history=conversation_history,
            available_agents="research, widget, synthesis, memory, direct",
        )

        # Route to appropriate sub-agent
        agent = decision.selected_agent.lower()
        if agent == "research":
            return self.research_agent(query=query)
        elif agent == "widget":
            return self.widget_agent(query=query)
        elif agent == "synthesis":
            return self.synthesis_agent(query=query)
        elif agent == "memory":
            return self.memory_agent(query=query)
        else:  # direct
            return dspy.Prediction(response=query)  # Simple direct answer
```

### 5.2 Research Sub-Agent (3 Tools Only)

```python
# agent/react_agents/research_agent.py
import dspy
from dspy import Tool

class ResearchAgent(dspy.Module):
    """Research specialist with ONLY 3 tools (prevents hallucination)."""

    def __init__(self, searxng_search, web_scraper, citation_builder):
        super().__init__()

        # 🔴 CRITICAL: Only 3 tools (prevents tool confusion)
        tools = [
            Tool(searxng_search, name="search_web"),
            Tool(web_scraper, name="scrape_page"),
            Tool(citation_builder, name="build_citation"),
        ]

        # ReAct with limited toolset
        self.react = dspy.ReAct(
            "query -> research_findings",
            tools=tools,
            max_iters=3,  # Limited iterations
        )

    def forward(self, query: str) -> dspy.Prediction:
        """Execute research with limited tools."""
        result = self.react(query=query)
        return dspy.Prediction(
            research_findings=result.research_findings,
            sources=result.sources,
        )
```

### 5.3 Widget Sub-Agent (3 Tools Only)

```python
# agent/react_agents/widget_agent.py
import dspy
from dspy import Tool

class WidgetAgent(dspy.Module):
    """Widget generation specialist with ONLY 3 tools."""

    def __init__(self, widget_selector, card_renderer, chart_renderer):
        super().__init__()

        # 🔴 CRITICAL: Only 3 tools (prevents arbitrary widget dump)
        tools = [
            Tool(widget_selector, name="select_widgets"),
            Tool(card_renderer, name="render_card"),
            Tool(chart_renderer, name="show_chart"),
        ]

        self.react = dspy.ReAct(
            "query -> widget_plan",
            tools=tools,
            max_iters=2,
        )

    def forward(self, query: str, accumulated_findings: list[str]) -> dspy.Prediction:
        """Generate adaptive widgets based on findings."""
        findings_text = "\n".join(accumulated_findings)
        result = self.react(query=query, accumulated_findings=findings_text)
        return dspy.Prediction(
            selected_widgets=result.selected_widgets,
            widget_count=len(result.selected_widgets),
        )
```

### 5.4 Hierarchy Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ReAct Agent Hierarchy                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  CoordinatorAgent (Main)                                         │   │
│   │    - Analyzes query complexity                                   │   │
│   │    - Deploys sub-agents                                          │   │
│   │    - Aggregates results                                          │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                          ↓ deploys based on query type                   │
│   ┌──────────┬──────────┬──────────┬──────────┬──────────┐             │
│   ▼          ▼          ▼          ▼          ▼          ▼             │
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐              │
│ │Research│ │Widget│ │Synthesis│ │Memory│ │Direct│ │Other │              │
│ │Agent  │ │Agent │ │Agent   │ │Agent │ │Answer│ │Agent │              │
│ │3 tools│ │3 tools│ │3 tools │ │3 tools│ │0 tools│ │3 tools│              │
│ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘              │
│    ↓        ↓        ↓        ↓        ↓        ↓                     │
│ DSPy Tools (atomic operations)                                          │
│    │        │        │        │                                         │
│ ┌────┴────┴────┴────┴────────────────────────────────────────┐        │
│ │  SearXNG, WebScraper, Citation, WidgetSelector, CardRenderer, │        │
│ │  Synthesizer, MemoryStore, MemorySearch, etc.                │        │
│ └───────────────────────────────────────────────────────────────┘        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.5 Tool Limit Enforcement

```python
# agent/react_agents/base_agent.py
from typing import List

MAX_TOOLS_PER_AGENT = 5  # 🔴 Hard limit to prevent hallucination

class BaseReActAgent(dspy.Module):
    """Base class with tool limit enforcement."""

    def __init__(self, tools: List[dspy.Tool], max_tools: int = MAX_TOOLS_PER_AGENT):
        if len(tools) > max_tools:
            raise ValueError(
                f"Too many tools: {len(tools)} > {max_tools}. "
                f"Split into multiple sub-agents to prevent hallucination."
            )
        super().__init__()
        self.react = dspy.ReAct(
            "query -> result",
            tools=tools,
            max_iters=3,
        )
```

---

## 6. Memory Implementation: Mem0 + Qdrant + LangGraph

### 6.1 Three-Memory System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      THREE-MEMORY SYSTEM                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Memory Type 1: LangGraph Graph Memory (Checkpointers)          │   │
│  │    Purpose: Procedural routing ("how to navigate")              │   │
│  │    Implementation: PostgresSaver                                │   │
│  │    Duration: Per-thread, time-travel enabled                    │   │
│  │    Stores: AgentState snapshots, execution path, routing history│   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ↕ (accessed by graph nodes)                │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Memory Type 2: Qdrant Vector Store (ColBERT Multivectors)      │   │
│  │    Purpose: Semantic search with late interaction              │   │
│  │    Implementation: QdrantClient + FastEmbed ColBERT            │   │
│  │    Duration: Persistent, cross-session                          │   │
│  │    Stores: Tier 2 (session), Tier 3 (persistent) memories      │   │
│  │    Collections: mem_{agent}_{user_id}[_session_{id}]          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ↕ (accessed by TemporalRAGService)        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Memory Type 3: Mem0AI (Advanced Consolidation)                │   │
│  │    Purpose: Memory summarization, duplicate detection          │   │
│  │    Implementation: Mem0 Memory (uses Qdrant as backend)        │   │
│  │    Duration: Long-term (30-90 days)                            │   │
│  │    Stores: Consolidated summaries, merged duplicates          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.2 ColBERTv2: Retriever and Embedder

```python
# infrastructure/external/colbert_embedder.py
from fastembed import LateInteractionTextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, MultiVectorConfig, MultiVectorComparator, Distance

class ColBERTEmbedder:
    """ColBERTv2 late interaction embedder for semantic search.

    Why ColBERT?
    - Token-level granularity (preserves fine-grained semantics)
    - Late interaction (efficient MaxSim operation)
    - Multivector output (each token → 128-dim vector)
    - State-of-the-art retrieval performance
    """

    MODEL_NAME = "colbert-ir/colbertv2.0"  # 128 dimensions per token
    VECTOR_SIZE = 128

    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        # Lazy-load ColBERT model
        self._embedder: LateInteractionTextEmbedding | None = None

        # Qdrant client for multivector storage
        self.client = QdrantClient(url=qdrant_url)

    @property
    def embedder(self) -> LateInteractionTextEmbedding:
        """Lazy-load ColBERT model (expensive, ~440MB)."""
        if self._embedder is None:
            self._embedder = LateInteractionTextEmbedding(
                model_name=self.MODEL_NAME,
            )
        return self._embedder

    def embed_text(self, text: str) -> list[list[float]]:
        """Embed text as multivectors (one vector per token).

        Returns:
            list[list[float]]: Multivector embedding (num_tokens × 128)
        """
        # embed() returns generator of multivectors
        embeddings = list(self.embedder.embed([text]))
        return embeddings[0]  # First (and only) text

    def query_embed(self, query: str) -> list[list[float]]:
        """Embed query for search (optimized for retrieval)."""
        # query_embed() is optimized for search queries
        embeddings = list(self.embedder.query_embed([query]))
        return embeddings[0]

    def ensure_collection(self, collection_name: str) -> None:
        """Create Qdrant collection with multivector config."""
        collections = [c.name for c in self.client.get_collections().collections]
        if collection_name not in collections:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE,
                    multivector_config=MultiVectorConfig(
                        comparator=MultiVectorComparator.MAX_SIM  # MaxSim operation
                    ),
                ),
            )

    async def search(
        self,
        collection_name: str,
        query: str,
        limit: int = 10,
        user_id: str = None,
    ) -> list[dict]:
        """Semantic search using ColBERT late interaction.

        Args:
            collection_name: Qdrant collection name
            query: Search query
            limit: Max results
            user_id: Optional filter

        Returns:
            list[dict]: Search results with scores
        """
        query_vectors = self.query_embed(query)

        # Build filter (user isolation)
        query_filter = None
        if user_id:
            from qdrant_client.models import Filter, FieldCondition
            query_filter = Filter(
                must=[FieldCondition(key="user_id", match={"value": user_id})]
            )

        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vectors,
            limit=limit,
            query_filter=query_filter,
        )

        return [
            {
                "content": r.payload.get("content", ""),
                "score": r.score,
                "metadata": {
                    k: v for k, v in r.payload.items()
                    if k not in ["content", "_id"]
                },
            }
            for r in results
        ]
```

### 6.3 LangGraph Memory + Agents Interface

```python
# infrastructure/memory/langgraph_store_adapter.py
from langgraph.store.postgres import PostgresStore
from langgraph.checkpoint.postgres import PostgresSaver
from domain.models.episodic_memory import EpisodicMemory, TemporalMetadata

class MemoryManager:
    """Manages all three memory types with proper isolation.

    Key Responsibilities:
    1. Graph Memory (Checkpointers): Procedural routing
    2. Agent Memory (Store): Cached research results
    3. Qdrant Memory: Semantic search with ColBERT
    """

    def __init__(self):
        # Graph Memory: Checkpointers for procedural routing
        self.checkpointer = PostgresSaver.from_conn_string(
            "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"
        )

        # Agent Memory: Store for cached research
        self.store = PostgresStore.from_conn_string(
            "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"
        )

        # Qdrant Memory: Semantic search with ColBERT
        self.colbert = ColBERTEmbedder()

    async def store_research_result(
        self,
        query: str,
        user_id: str,
        session_id: str,
        summary: str,
        result: str,
        outcome_quality: str = "medium",
    ) -> str:
        """Store research result in BOTH Store and Qdrant.

        Store: Fast lookup by query hash
        Qdrant: Semantic search by similarity

        Returns:
            str: memory_id
        """
        import uuid
        import hashlib
        from datetime import datetime

        memory_id = str(uuid.uuid4())
        query_hash = hashlib.sha256(query.lower().encode()).hexdigest()
        namespace = ("research", query_hash)

        # Create memory with C005 temporal metadata
        memory = EpisodicMemory(
            memory_id=memory_id,
            query=query,
            query_hash=query_hash,
            summary=summary,
            result=result,
            temporal=TemporalMetadata(
                created_at=datetime.now(),
                modified_at=datetime.now(),
                valid_from=datetime.now(),
                valid_until=None,  # Still valid
                temporal_type="research",
                supersedes=[],
                superseded_by=None,
            ),
            outcome_quality=outcome_quality,
            user_id=user_id,
            session_id=session_id,
        )

        # Store in LangGraph Store (for query hash lookup)
        await self.store.aput(namespace, memory_id, memory.model_dump())

        # Store in Qdrant (for semantic search)
        collection_name = f"mem_research_{user_id}"
        self.colbert.ensure_collection(collection_name)

        # Embed with ColBERT
        vectors = self.colbert.embed_text(summary)

        # Store in Qdrant
        from qdrant_client.models import PointStruct
        self.colbert.client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=memory_id,
                    vector=vectors,
                    payload={
                        "content": summary,
                        "full_result": result,
                        "user_id": user_id,
                        "query": query,
                        **memory.temporal.model_dump(),
                    },
                )
            ],
        )

        return memory_id

    async def search_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 5,
    ) -> list[EpisodicMemory]:
        """Search memories using BOTH Store (exact match) and Qdrant (semantic).

        Returns:
            list[EpisodicMemory]: Combined results
        """
        import hashlib

        # 1. Exact match in Store (by query hash)
        query_hash = hashlib.sha256(query.lower().encode()).hexdigest()
        namespace = ("research", query_hash)

        exact_items = await self.store.asearch(namespace, query=query, limit=1)
        exact_results = [EpisodicMemory(**item.value) for item in exact_items]

        # 2. Semantic search in Qdrant
        collection_name = f"mem_research_{user_id}"
        semantic_results = await self.colbert.search(
            collection_name=collection_name,
            query=query,
            limit=limit,
            user_id=user_id,
        )

        # 3. Merge and deduplicate
        seen_ids = {m.memory_id for m in exact_results}
        for sem in semantic_results:
            if sem["content"] and sem.get("memory_id") not in seen_ids:
                # Convert Qdrant result to EpisodicMemory
                exact_results.append(
                    EpisodicMemory(
                        memory_id=sem.get("id", ""),
                        query=sem["metadata"].get("query", ""),
                        query_hash="",
                        summary=sem["content"],
                        result=sem["metadata"].get("full_result", sem["content"]),
                        temporal=TemporalMetadata(**sem["metadata"]),
                        outcome_quality=sem["metadata"].get("outcome_quality", "medium"),
                        user_id=user_id,
                        session_id="",
                    )
                )

        return exact_results[:limit]
```

### 6.4 Mem0: Preventing Partial Execution Hoarding

```python
# infrastructure/memory/mem0_adapter.py
from mem0 import Memory
from application.use_cases.manage_memory import ConsolidateMemoryUseCase

class Mem0MemoryAdapter:
    """Mem0AI adapter with safeguards against memory hoarding.

    Problem: Mem0 can store every partial execution, bloating memory.
    Solution: Filter and consolidate before storing.
    """

    def __init__(self, consolidation_use_case: ConsolidateMemoryUseCase):
        self.client = Memory.from_config({
            "vector_store": {
                "provider": "qdrant",
                "config": {"host": "localhost", "port": 6333},
            },
        })
        self.consolidation = consolidation_use_case

    async def store_execution_result(
        self,
        query: str,
        result: str,
        user_id: str,
        confidence: float,
    ) -> bool:
        """Store result ONLY if it meets quality thresholds.

        Prevents hoarding by:
        1. Filtering low-confidence results (< 0.6)
        2. Filtering trivial results (< 50 chars)
        3. Checking for duplicates before storing
        """
        # 🔴 CRITICAL: Filter low-quality results
        if confidence < 0.6:
            return False  # Don't store uncertain results

        if len(result.strip()) < 50:
            return False  # Don't store trivial results

        # Check for duplicates (Mem0 does this, but we add extra check)
        existing = self.client.search(query, user_id=user_id, limit=3)
        for ex in existing:
            if ex.get("memory", "") == result:
                return False  # Duplicate, don't store

        # Store if passes all filters
        self.client.add(
            result,
            user_id=user_id,
            metadata={
                "query": query,
                "confidence": confidence,
                "stored_at": datetime.now().isoformat(),
            },
        )

        return True

    async def consolidate_if_needed(self, user_id: str) -> int:
        """Consolidate memories if count exceeds threshold.

        Prevents memory hoarding by consolidating old memories.
        """
        # Get all memories for user
        all_memories = self.client.get_all(user_id=user_id)
        memory_count = len(all_memories.get("results", []))

        # Consolidate if > 100 memories
        if memory_count > 100:
            # Use consolidation use case
            return await self.consolidation.execute(user_id=user_id)

        return 0
```

---

## 7. Progressive Disclosure Implementation

### 7.1 Progressive Disclosure Widget

```typescript
// frontend/components/ProgressiveDisclosure.tsx
import { useState } from "react";

interface Widget {
  widget_type: string;
  title: string;
  content: any;
  priority: number;
}

export function ProgressiveDisclosure({ widgets }: { widgets: Widget[] }) {
  const [showAll, setShowAll] = useState(false);
  const maxVisible = 3;

  const visibleWidgets = showAll ? widgets : widgets.slice(0, maxVisible);
  const hasMore = widgets.length > maxVisible;

  return (
    <div className="widgets-container">
      {visibleWidgets.map((widget, index) => (
        <div
          key={index}
          className="widget-item"
          style={{ order: -widget.priority }}  // Higher priority first
        >
          <WidgetCard widget={widget} />
        </div>
      ))}

      {hasMore && !showAll && (
        <button
          onClick={() => setShowAll(true)}
          className="show-more-button"
        >
          Show {widgets.length - maxVisible} More Widgets
        </button>
      )}
    </div>
  );
}

function WidgetCard({ widget }: { widget: Widget }) {
  switch (widget.widget_type) {
    case "data_table":
      return <DataTable {...widget.content} title={widget.title} />;
    case "chart":
      return <Chart {...widget.content} title={widget.title} />;
    case "timeline":
      return <Timeline {...widget.content} title={widget.title} />;
    default:
      return <TextCard {...widget.content} title={widget.title} />;
  }
}
```

### 7.2 Streaming with Progressive Disclosure

```python
# agent/nodes/synthesizer.py
from typing import AsyncGenerator

async def synthesizer_node(state: AgentState) -> AsyncGenerator[dict, None]:
    """Synthesize response with progressive disclosure.

    Streams text first, then reveals widgets progressively.
    """
    findings = state.get("research_findings", [])
    query = state["query"]
    widgets = state.get("selected_widgets", [])

    # Phase 1: Stream text response
    response_parts = []
    for i, chunk in enumerate(stream_synthesizer(query=query, findings=findings)):
        response_parts.append(chunk)
        yield {
            "streaming_event": TokenEvent(
                token=chunk,
                is_first=(i == 0),
                index=i,
            ),
        }

    final_response = "".join(response_parts)

    # Phase 2: Reveal widgets progressively (highest priority first)
    widgets.sort(key=lambda w: w.priority, reverse=True)

    for i, widget in enumerate(widgets):
        yield {
            "streaming_event": WidgetRevealEvent(
                widget=widget,
                index=i,
                total=len(widgets),
            ),
        }

    # Phase 3: Final completion event
    yield {
        "final_response": final_response,
        "widgets": widgets,
        "widget_count": len(widgets),
        "streaming_event": CompleteEvent(
            final_response=final_response,
            widget_count=len(widgets),
        ),
    }
```

---

## 8. Biological Inspiration: Procedural Memory

### 8.1 From Neuroscience Research

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

## 10. Transient UX for Long-Running Tasks

### 10.1 UX Problem

**User insight**: "Even if a task takes 15 minutes, humans won't wait and will leave."

**Solution**: Keep users engaged with transient UX patterns:

- Skeleton screens (appear within 300ms)
- Streaming responses (token-by-token)
- Progress events (every 1-2s)
- "Continue in background?" prompt (after 15s)

### 10.2 Streaming Response Flow

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

## 11. Technical Decisions

| Decision | Option Chosen | Alternatives | Rationale |
|----------|--------------|--------------|-----------|
| **ReAct hierarchy** | Coordinator deploys sub-agents | Single monolithic agent | Prevents hallucination, limits tools to 3-5 per agent |
| **Tool limit** | MAX_TOOLS_PER_AGENT = 5 | Unlimited tools | Hard limit prevents tool confusion |
| **State-driven routing** | LLM evaluates accumulated state | Static conditionals | "What do I know?" question |
| **Worker creation** | Send API (dynamic) | Fixed nodes | Scalable, flexible |
| **Memory - Graph** | Checkpointers (PostgresSaver) | In-memory | Procedural routing with time-travel |
| **Memory - Agent** | Store (PostgresStore) | In-memory | Cross-thread cached research |
| **Memory - Semantic** | Qdrant + ColBERT | Single-vector embeddings | Late interaction, token-level granularity |
| **Memory - Consolidation** | Mem0AI | Custom LLM summarization | Proven DSPy integration, duplicate detection |
| **ColBERT model** | colbert-ir/colbertv2.0 | BAAI/bge-small-en-v1.5 | State-of-the-art retrieval, 128-dim multivectors |
| **Output format** | Structured (Pydantic) | Text parsing | R014 bug fixed |
| **Progressive disclosure** | 3 visible, "Show More" | All visible | Prevents widget overwhelm |

---

## 12. Voice Subgraph: TTS/STT with Proper Cleanup

### 12.1 The Problem

**Current C010 implementation** uses `asyncio.gather()` for concurrent STT/TTS WebSocket management:

```python
# Current voice_gateway_service.py (PROBLEMATIC)
async def output_task(
    self,
    stt_ws: WebSocket,
    tts_ws: WebSocket,
    frontend_ws: WebSocket,
    session_id: str,
    text_handler: TextStreamHandler,
    process_agent_fn: Callable,
):
    """Forward STT/TTS to frontend."""

    # ❌ PROBLEM: asyncio.gather() doesn't guarantee proper cleanup on errors
    await asyncio.gather(
        stt_ws.recv(),
        tts_ws.recv(),
    )
```

**Issues**:
- No guaranteed cleanup if one WebSocket fails
- No structured state management for voice sessions
- Difficult to interrupt mid-stream
- No integration with LangGraph state machine

### 12.2 Solution: LangGraph Voice Subgraph

Replace raw asyncio with a LangGraph subgraph for voice session management:

```python
# agent/nodes/voice/voice_subgraph.py
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, START, END
from operator import add

class VoiceState(TypedDict):
    """Voice session state for TTS/STT subgraph."""

    # Session identifiers
    session_id: str
    user_id: str

    # WebSocket connections (managed outside state)
    stt_connected: bool
    tts_connected: bool
    frontend_connected: bool

    # Audio streams
    audio_input_buffer: list[bytes]
    audio_output_buffer: list[bytes]

    # Transcription and synthesis
    transcribed_text: str
    synthesis_pending: bool
    synthesis_interrupted: bool

    # Agent communication
    agent_response: str

    # Status tracking
    current_step: Literal[
        "connect_kyutai",
        "listen_audio",
        "transcribe",
        "process_agent",
        "synthesize",
        "stream_audio",
        "check_interrupt",
        "cleanup",
    ]

    # Error handling
    error_message: str | None
    should_terminate: bool
```

### 12.3 Voice Subgraph Nodes

```python
# agent/nodes/voice/voice_nodes.py

async def connect_kyutai_node(state: VoiceState) -> dict:
    """Connect to Kyutai STT and TTS WebSocket servers."""

    session_id = state["session_id"]

    # Connect to STT
    stt_connected = await voice_gateway.connect_stt(session_id)

    # Connect to TTS
    tts_connected = await voice_gateway.connect_tts(session_id)

    if not stt_connected or not tts_connected:
        return {
            "error_message": "Failed to connect to Kyutai servers",
            "should_terminate": True,
            "current_step": "cleanup",
        }

    return {
        "stt_connected": True,
        "tts_connected": True,
        "current_step": "listen_audio",
    }

async def listen_audio_node(state: VoiceState) -> dict:
    """Listen for audio input from frontend (with VAD)."""

    # Receive audio chunk from frontend
    audio_chunk = await frontend_ws.receive_bytes()

    # Apply VAD (Voice Activity Detection)
    has_speech = await vad_service.detect_speech(audio_chunk)

    if has_speech:
        return {
            "audio_input_buffer": [audio_chunk],
            "current_step": "transcribe",
        }

    return {
        "current_step": "listen_audio",  # Keep listening
    }

async def transcribe_node(state: VoiceState) -> dict:
    """Transcribe audio to text using Kyutai STT."""

    audio_buffer = state.get("audio_input_buffer", [])

    # Send audio to STT
    transcribed = await stt_service.transcribe(audio_buffer)

    return {
        "transcribed_text": transcribed,
        "current_step": "process_agent",
        "audio_input_buffer": [],  # Clear buffer
    }

async def process_agent_node(state: VoiceState) -> dict:
    """Process transcribed text through agent (main graph invocation)."""

    transcribed = state.get("transcribed_text", "")

    # Invoke main agent graph with text query
    result = await main_agent_graph.ainvoke(
        {"query": transcribed, "input_path": InputPath.TEXT},
        config={"configurable": {"thread_id": state["session_id"]}},
    )

    response = result.get("final_response", "")

    return {
        "agent_response": response,
        "synthesis_pending": True,
        "current_step": "synthesize",
    }

async def synthesize_node(state: VoiceState) -> dict:
    """Synthesize agent response to audio using Kyutai TTS."""

    response = state.get("agent_response", "")
    session_id = state["session_id"]

    # Stream TTS sentence by sentence
    audio_chunks = []

    async for chunk in tts_service.synthesize_stream(response):
        if state.get("synthesis_interrupted", False):
            break  # User interrupted

        audio_chunks.append(chunk)

    return {
        "audio_output_buffer": audio_chunks,
        "synthesis_pending": False,
        "current_step": "stream_audio",
    }

async def stream_audio_node(state: VoiceState) -> dict:
    """Stream audio output to frontend."""

    audio_buffer = state.get("audio_output_buffer", [])

    for chunk in audio_buffer:
        await frontend_ws.send_bytes(chunk)

    return {
        "audio_output_buffer": [],
        "current_step": "check_interrupt",
    }

async def check_interrupt_node(state: VoiceState) -> dict:
    """Check if user interrupted or session should continue."""

    # Check for interrupt signal from frontend
    interrupt = await frontend_ws.receive_json()

    if interrupt.get("type") == "interrupt":
        return {
            "synthesis_interrupted": True,
            "current_step": "cleanup",
        }

    # Continue listening for next input
    return {
        "synthesis_interrupted": False,
        "current_step": "listen_audio",
    }

async def cleanup_node(state: VoiceState) -> dict:
    """CLEANUP NODE: Always runs, even on errors.

    CRITICAL: This node MUST run to prevent WebSocket leaks.
    """

    session_id = state["session_id"]

    # Close STT WebSocket
    if state.get("stt_connected"):
        await voice_gateway.disconnect_stt(session_id)

    # Close TTS WebSocket
    if state.get("tts_connected"):
        await voice_gateway.disconnect_tts(session_id)

    # Clear session state
    await text_handler.clear_session(session_id)

    return {
        "stt_connected": False,
        "tts_connected": False,
        "audio_input_buffer": [],
        "audio_output_buffer": [],
        "current_step": "cleanup",
    }
```

### 12.4 Voice Subgraph Graph Definition

```python
# agent/nodes/voice/voice_subgraph.py

def build_voice_subgraph() -> StateGraph:
    """Build voice session subgraph with proper cleanup."""

    builder = StateGraph(VoiceState)

    # Add nodes
    builder.add_node("connect_kyutai", connect_kyutai_node)
    builder.add_node("listen_audio", listen_audio_node)
    builder.add_node("transcribe", transcribe_node)
    builder.add_node("process_agent", process_agent_node)
    builder.add_node("synthesize", synthesize_node)
    builder.add_node("stream_audio", stream_audio_node)
    builder.add_node("check_interrupt", check_interrupt_node)
    builder.add_node("cleanup", cleanup_node)

    # Entry point
    builder.add_edge(START, "connect_kyutai")

    # Main flow: connect → listen → transcribe → agent → synthesize → stream → check
    builder.add_conditional_edges(
        "connect_kyutai",
        lambda s: "cleanup" if s.get("should_terminate") else "listen_audio",
    )

    builder.add_conditional_edges(
        "listen_audio",
        lambda s: s.get("current_step", "listen_audio"),
        {
            "transcribe": "transcribe",
            "listen_audio": "listen_audio",  # Continue listening
        },
    )

    builder.add_edge("transcribe", "process_agent")
    builder.add_edge("process_agent", "synthesize")
    builder.add_edge("synthesize", "stream_audio")
    builder.add_edge("stream_audio", "check_interrupt")

    # After check: either continue listening or cleanup
    builder.add_conditional_edges(
        "check_interrupt",
        lambda s: "cleanup" if s.get("synthesis_interrupted") else "listen_audio",
    )

    # ALL paths lead to cleanup (guaranteed cleanup!)
    builder.add_edge("cleanup", END)

    return builder.compile()

# Compile voice subgraph
voice_subgraph = build_voice_subgraph()
```

### 12.5 Integration with Main Graph

```python
# agent/nodes/voice/voice_integration.py

async def voice_input_node(state: AgentState) -> dict:
    """Handle voice input by invoking voice subgraph.

    This node is part of the main agent graph.
    """

    session_id = state["session_id"]
    user_id = state["user_id"]

    # Initialize voice state
    voice_state: VoiceState = {
        "session_id": session_id,
        "user_id": user_id,
        "stt_connected": False,
        "tts_connected": False,
        "frontend_connected": True,
        "audio_input_buffer": [],
        "audio_output_buffer": [],
        "transcribed_text": "",
        "synthesis_pending": False,
        "synthesis_interrupted": False,
        "agent_response": "",
        "current_step": "connect_kyutai",
        "error_message": None,
        "should_terminate": False,
    }

    # Invoke voice subgraph (runs until cleanup)
    voice_result = await voice_subgraph.ainvoke(
        voice_state,
        config={"configurable": {"thread_id": session_id}},
    )

    # Extract transcribed text for main graph
    transcribed = voice_result.get("transcribed_text", "")

    if transcribed:
        # Update main graph state with transcribed query
        return {
            "preprocessed_query": transcribed,
            "input_path": InputPath.TEXT,  # Transcribed to text
        }

    # Handle voice session termination
    if voice_result.get("error_message"):
        return {
            "error_message": voice_result["error_message"],
        }

    return {}
```

### 12.6 Guaranteed Cleanup Pattern

The key improvement over the current `asyncio.gather()` approach:

| Aspect | Current (asyncio.gather) | Voice Subgraph (LangGraph) |
|--------|-------------------------|---------------------------|
| **Error handling** | One failure leaves other WebSocket open | All paths lead to cleanup node |
| **State management** | Ad-hoc variables | Structured VoiceState TypedDict |
| **Interruption** | Manual flag checks | Built into graph routing |
| **Integration** | Separate from main graph | Invoked from main graph node |
| **Cleanup guarantee** | ❌ Not guaranteed | ✅ ALL paths lead to cleanup |

### 12.7 Cleanup Guarantee

```python
# In voice_subgraph.py, ALL conditional edges lead to cleanup:

# 1. Connection error → cleanup
builder.add_conditional_edges(
    "connect_kyutai",
    lambda s: "cleanup" if s.get("should_terminate") else "listen_audio",
)

# 2. User interrupt → cleanup
builder.add_conditional_edges(
    "check_interrupt",
    lambda s: "cleanup" if s.get("synthesis_interrupted") else "listen_audio",
)

# 3. Normal flow → check_interrupt → either listen_audio or cleanup

# 4. Direct edge to END (cleanup is final step)
builder.add_edge("cleanup", END)
```

**Result**: No matter what happens (connection error, user interrupt, normal completion), the cleanup node ALWAYS runs.

---

## 13. Rollout Plan

| Phase | Component | Duration | Dependencies |
|-------|-----------|----------|--------------|
| **Phase 1** | ReAct agent hierarchy | Week 1-2 | DSPy 3.1+, tool limit enforcement |
| **Phase 2** | Graph memory (Checkpointers) + evaluator | Week 2-3 | Postgres running, LangGraph compiled |
| **Phase 3** | Agent memory (Store) + cache lookup | Week 3-4 | PostgresStore configured |
| **Phase 4** | Qdrant + ColBERT embedder | Week 4-5 | Qdrant running, fastembed installed |
| **Phase 5** | Mem0AI consolidation | Week 5-6 | Qdrant backend ready |
| **Phase 6** | Send API dynamic workers | Week 6-7 | All sub-agents implemented |
| **Phase 7** | Transient UX streaming + progressive disclosure | Week 7-8 | Frontend widget components |
| **Phase 8** | STT preprocessing | Week 8-9 | C010 voice-client working |
| **Phase 9** | Integration testing | Week 9-10 | All components connected |
| **Phase 10** | Performance optimization | Week 10-11 | Profiling, caching, consolidation |

---

## 13. Implementation Checklist

### ReAct Agent Hierarchy
- [ ] `CoordinatorAgent` with sub-agent deployment logic
- [ ] `ResearchAgent` (3 tools: search, scrape, cite)
- [ ] `WidgetAgent` (3 tools: select, render_card, show_chart)
- [ ] `SynthesisAgent` (3 tools: summarize, format_text, check_quality)
- [ ] `MemoryAgent` (3 tools: store, search, consolidate)
- [ ] `BaseReActAgent` with tool limit enforcement (MAX_TOOLS_PER_AGENT = 5)

### Memory Implementation
- [ ] `ColBERTEmbedder` with lazy-loading, Qdrant multivector support
- [ ] `MemoryManager` combining Checkpointers + Store + Qdrant
- [ ] `Mem0MemoryAdapter` with quality filtering (confidence >= 0.6, length >= 50)
- [ ] Temporal metadata (C005): created_at, valid_until, supersedes, superseded_by
- [ ] Three-tier memory: Tier 1 (Redis/In-Memory), Tier 2 (Qdrant session), Tier 3 (Qdrant persistent)

### LangGraph Integration
- [ ] Graph compilation with checkpointer and store
- [ ] State accumulation with reducers (`Annotated[list[str], add]`)
- [ ] Evaluator node with `original_query` always passed
- [ ] Send API for dynamic worker creation

### Frontend
- [ ] `ProgressiveDisclosure` component (3 visible, "Show More")
- [ ] Widget streaming events (TokenEvent, WidgetRevealEvent, CompleteEvent)
- [ ] Priority-based widget ordering (higher priority first)

---

## 15. References

- **LangGraph Send API**: `tests/langgraph_workflows_agents.md` (lines 663-768)
- **Evaluator-Optimizer**: `tests/langgraph_workflows_agents.md` (lines 770-912)
- **LangGraph Memory**: `tests/langgraph_memory.md`
- **C005 Memory Specs**: Temporal metadata, consolidation patterns
- **Biological Procedural Memory**: tavily_research on corticostriatal circuits
- **Transient UX Research**: tavily_research on long-running AI task UX

---

**Next**: See `validate.md` for validation against requirements.

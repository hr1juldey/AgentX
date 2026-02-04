# DeepAgents Architecture Research

**Date:** 2026-02-04
**Source:** [LangChain DeepAgents Documentation](https://docs.langchain.com/oss/python/deepagents/overview)
**Status:** Research Complete

---

## Executive Summary

DeepAgents is a standalone library built on LangGraph and LangChain that structures complex, multi-step tasks using modular middleware, explicit planning, a virtual filesystem for large context management, and hierarchical subagents. It is inspired by applications like Claude Code, Deep Research, and Manus.

**Key Differentiator:** Unlike standard LangChain agents that use simple "LLM -> tool -> LLM" loops, DeepAgents emphasize planning, durable orchestration, and hierarchical delegation for long-running or context-heavy workflows.

---

## Table of Contents

1. [What Are DeepAgents?](#what-are-deepagents)
2. [How DeepAgents Differ from Standard LangChain Agents](#how-deepagents-differ-from-standard-langchain-agents)
3. [Core Architecture Components](#core-architecture-components)
4. [Multi-Agent Orchestration Patterns](#multi-agent-orchestration-patterns)
5. [Agent Composition and Hierarchy](#agent-composition-and-hierarchy)
6. [Handling Complex Workflows](#handling-complex-workflows)
7. [LangGraph Integration for Routing](#langgraph-integration-for-routing)
8. [Backends and State Management](#backends-and-state-management)
9. [Middleware Architecture](#middleware-architecture)
10. [When to Use DeepAgents vs Standard Agents](#when-to-use-deepagents-vs-standard-agents)

---

## What Are DeepAgents?

DeepAgents (`deepagents` package) is a standalone library for building agents that can tackle complex, multi-step tasks. It provides:

- **Planning and task decomposition** - Built-in `write_todos` tool for breaking down complex tasks
- **Context management** - File system tools (`ls`, `read_file`, `write_file`, `edit_file`) for offloading large context
- **Subagent spawning** - Built-in `task` tool for delegating to specialized subagents
- **Long-term memory** - Persistent memory across conversations using LangGraph's Store

### Built On

```
DeepAgents
    |
    +-- LangGraph (graph execution, state management, routing)
    +-- LangChain (tools, model integrations)
    +-- LangSmith (observability, evaluation, deployment)
```

---

## How DeepAgents Differ from Standard LangChain Agents

| Aspect | Standard LangChain Agents | DeepAgents |
|--------|---------------------------|------------|
| **Execution Model** | Single LLM -> tool -> LLM loop | Multi-step planning + execution with middleware |
| **Context Management** | Limited to context window | Virtual filesystem for large context |
| **Planning** | Implicit (if any) | Explicit `write_todos` tool with progress tracking |
| **Delegation** | Manual tool delegation | Built-in subagent spawning with isolation |
| **State Persistence** | Thread-scoped state | Cross-thread memory via LangGraph Store |
| **Routing** | Simple conditional logic | LangGraph Command routing with parallel execution |
| **Durability** | Ephemeral | Checkpointing, interrupt recovery, long-term storage |
| **Complexity** | Best for simple, single-step tasks | Best for complex, multi-step workflows |

### Visual Comparison

**Standard LangChain Agent:**
```
User Query -> LLM -> Tool Call -> LLM -> Response
    |
    +-- Context fills up quickly
    +-- No explicit planning
    +-- Limited decomposition
```

**DeepAgent:**
```
User Query -> Planner (write_todos)
                    |
                    v
            Filesystem (context offload)
                    |
                    v
            Supervisor Agent
                    |
        +-----------+-----------+
        |                       |
        v                       v
    Subagent 1              Subagent 2
    (isolated context)      (isolated context)
        |                       |
        +-----------+-----------+
                    |
                    v
            Synthesized Response
    |
    +-- Durable checkpoints
    +-- Hierarchical decomposition
    +-- Cross-thread memory
```

---

## Core Architecture Components

### 1. Agent Harness

The agent harness is the core runtime that compiles a DeepAgent into a LangGraph graph. Created via `create_deep_agent()`:

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="claude-sonnet-4-5-20250929",
    subagents=[...],
    backend=StateBackend(...),
    store=InMemoryStore(),
)
```

**Output:** A compiled LangGraph graph with:
- Streaming support
- Persistence/checkpointing
- Long-term memory access
- Human-in-the-loop capabilities

### 2. Middleware Stack

DeepAgents use a composable middleware architecture. Three default middleware are automatically attached:

| Middleware | Purpose | Tools Provided |
|------------|---------|----------------|
| `TodoListMiddleware` | Planning & task tracking | `write_todos` |
| `FilesystemMiddleware` | Context management | `ls`, `read_file`, `write_file`, `edit_file` |
| `SubAgentMiddleware` | Delegation & isolation | `task` (spawn subagents) |

### 3. Backends (Storage Layer)

Pluggable storage backends for filesystem operations:

| Backend | Description | Persistence | Use Case |
|---------|-------------|-------------|----------|
| `StateBackend` | In-graph state storage | Thread-scoped | Scratch pad, intermediate results |
| `FilesystemBackend` | Local disk access | Persistent | Local dev CLIs, CI/CD |
| `StoreBackend` | LangGraph Store | Cross-thread | Long-term memories, shared state |
| `CompositeBackend` | Path-based routing | Mixed | Route `/memories/` to store, rest to state |

### 4. Subagents

Specialized agent instances spawned by a supervisor agent:

```python
subagent = {
    "name": "research-agent",
    "description": "Conducts in-depth research using web search",
    "system_prompt": "You are a thorough researcher...",
    "tools": [internet_search],
    "model": "openai:gpt-4o",  # Optional model override
}
```

**Benefits:**
- Context quarantine (keeps main agent's context clean)
- Specialized instructions per subagent
- Different model capabilities per task
- Isolated tool sets

---

## Multi-Agent Orchestration Patterns

### 1. Supervisor/Worker (Centralized Control)

**Pattern:** A supervisor node routes to worker nodes using LangGraph Commands.

```python
def supervisor_node(state) -> Command[Literal["think_node", "document_node", "compress_node"]]:
    # Analyze state and decide next worker
    if state["needs_research"]:
        return Command(goto="think_node", update={"phase": "research"})
    elif state["has_data"]:
        return Command(goto="document_node", update={"phase": "documentation"})
    else:
        return Command(goto="compress_node", update={"phase": "summary"})
```

**Workflow:**
```
Supervisor -> [Worker 1] -> Supervisor -> [Worker 2] -> Supervisor -> [Worker 3] -> Final
```

### 2. Router Pattern (Broker/Mediator)

**Pattern:** Classify input with a router LLM and dispatch to specialized agents in parallel.

```python
def router_node(state):
    route = llm_classify(state["query"])  # Returns: "code", "math", "creative"
    return Command(goto=[f"{route}_handler"])  # Parallel execution
```

**Workflow:**
```
Router
    |
    +---> [Code Agent] -----+
    |                       |
    +---> [Math Agent] -----+---> Synthesis
    |                       |
    +---> [Creative Agent] -+
```

**Parallel Execution:** LangGraph automatically waits for all branches to complete before proceeding.

### 3. Hierarchical/Nested Agents

**Pattern:** Top-level orchestrator delegates to subagents with isolated contexts.

```python
orchestrator = create_deep_agent(
    model="claude-sonnet-4-5-20250929",
    subagents=[
        research_subagent,
        analysis_subagent,
        reporting_subagent,
    ]
)
```

**Workflow:**
```
Orchestrator
    |
    +---> [Research Subagent] (isolated context, many tool calls)
    |       |
    |       v
    |   Concise summary
    |
    +---> [Analysis Subagent] (isolated context, different model)
    |       |
    |       v
    |   Concise summary
    |
    +---> [Reporting Subagent] (isolated context)
            |
            v
        Final report
```

### 4. Handoffs and Skills

**Handoffs:** Tool calls update state to trigger routing/configuration changes.

**Skills:** On-demand loading of prompts/knowledge within a single agent (no context isolation).

**Decision Tree:**
```
Need context isolation?
    Yes -> Subagent (handoff)
    No ->
        Need specialized instructions?
            Yes -> Skill
            No -> Direct tool use
```

### 5. Blackboard/Choreography

**Pattern:** Nodes read/write shared state and run in cycles to iterate.

```python
# LangGraph's shared state enables blackboard-style patterns
class AgentState(TypedDict):
    shared_workspace: dict
    completed_tasks: list[str]
    current_phase: str
```

---

## Agent Composition and Hierarchy

### SubAgent Types

#### 1. Dictionary-Based SubAgent

Most common pattern for defining subagents:

```python
research_subagent = {
    "name": "research-agent",  # Required
    "description": "Conducts in-depth research...",  # Required
    "system_prompt": "You are a thorough researcher...",  # Required
    "tools": [internet_search],  # Required
    "model": "openai:gpt-4o",  # Optional - override main agent model
    "middleware": [...],  # Optional - additional middleware
    "interrupt_on": {"web_search": True},  # Optional - HITL
}
```

**Required Fields:**
- `name`: Unique identifier (used for `task()` tool, metadata, streaming)
- `description`: Action-oriented description (used by main agent for delegation decisions)
- `system_prompt`: Instructions for the subagent
- `tools`: Tools the subagent can use

**Optional Fields:**
- `model`: Override main agent's model (format: `"provider:model-name"`)
- `middleware`: Additional middleware for custom behavior
- `interrupt_on`: Configure human-in-the-loop for specific tools

#### 2. CompiledSubAgent

For complex workflows, use a pre-built LangGraph graph:

```python
from deepagents import CompiledSubAgent

custom_graph = create_agent(
    model=your_model,
    tools=specialized_tools,
    prompt="You are a specialized agent..."
)

custom_subagent = CompiledSubAgent(
    name="data-analyzer",
    description="Specialized agent for complex data analysis",
    runnable=custom_graph,  # Must be a compiled LangGraph graph
)
```

**Requirements:**
- Graph must have a state key called `"messages"`
- Graph must be compiled (`.compile()` called)

### The General-Purpose Subagent

Built-in subagent available to all DeepAgents:

- **System prompt:** Same as main agent
- **Tools:** Same as main agent
- **Model:** Same as main agent (unless overridden)

**Purpose:** Context isolation without specialized behavior.

**Example Usage:**
```python
# Main agent delegates to general-purpose subagent
# Subagent performs 10 web searches internally
# Returns only concise summary
result = task(name="general-purpose", task="Research quantum computing trends")
```

### Multi-Level Hierarchies

DeepAgents support nested hierarchies:

```
Orchestrator (Level 0)
    |
    +-- Domain Agent A (Level 1)
    |       |
    |       +-- Specialist A1 (Level 2)
    |       +-- Specialist A2 (Level 2)
    |
    +-- Domain Agent B (Level 1)
            |
            +-- Specialist B1 (Level 2)
```

**Key Points:**
- Each level has isolated context
- Different models can be used at each level
- Intermediate results are not bubbled up (only final summaries)

---

## Handling Complex Workflows

### Durable Execution and Checkpoints

LangGraph provides durable execution for long-running workflows:

```python
# Persistence occurs on:
# - Successful completion
# - Error/failure
# - Human interrupt

# Resume workflow with same thread_id
result = agent.invoke(
    input=None,  # None to resume
    config={"configurable": {"thread_id": "abc123"}}
)
```

**Persistence Modes:**
| Mode | Description | Tradeoff |
|------|-------------|----------|
| **Synchronous** | Persist on exit (success/error/interrupt) | Safer, slower |
| **Asynchronous** | Persist during execution | Faster, small checkpoint loss risk |

### Task Routing and Retry Policies

Routing decisions via `Command` objects or conditional edges:

```python
def supervisor_with_retry(state):
    if state["attempt_count"] >= 3:
        return Command(goto="failure_handler")

    route = classify_task(state["query"])
    return Command(
        goto=f"{route}_handler",
        update={"attempt_count": state["attempt_count"] + 1}
    )
```

**Best Practices:**
- Clear routing conditions
- Fallback paths for all branches
- Attempt counters in state
- Confidence thresholds for LLM-based routing

### Human-in-the-Loop

Interrupt workflows for approval or editing:

```python
agent = create_deep_agent(
    model="claude-sonnet-4-5-20250929",
    interrupt_on={
        "write_file": True,  # Require approval for file writes
        "send_email": True,  # Require approval for emails
    }
)
```

**Workflow:**
```
Execution -> Interrupt (pause) -> Human Approval -> Resume Execution
```

### Long-Running Workflows

Features supporting long-running workflows:
1. **Checkpointing** - Resume from any point after failure
2. **Interrupts** - Human-in-the-loop decision points
3. **Cross-thread memory** - StoreBackend for persistent artifacts
4. **Streaming** - Real-time progress updates

---

## LangGraph Integration for Routing

### How LangGraph Models Routes

LangGraph expresses workflows as **State + Nodes + Edges**:

| Component | Description |
|-----------|-------------|
| **State** | Shared mutable object flowing between steps |
| **Nodes** | Functions that read/write state |
| **Edges** | Connections between nodes (static, conditional, or Command-based) |

### Routing APIs

#### 1. Static Edges

Simple one-way connections:

```python
graph.add_edge("node_a", "node_b")
```

#### 2. Conditional Edges

IF/ELSE-style routing:

```python
def route_function(state):
    if state["category"] == "urgent":
        return "urgent_handler"
    else:
        return "normal_handler"

graph.add_conditional_edges(
    "router",
    route_function,
    {"urgent_handler": ..., "normal_handler": ...}
)
```

#### 3. Command Return Values (Dynamic)

Most powerful routing - nodes decide next nodes:

```python
def supervisor_node(state) -> Command[Literal["worker_a", "worker_b"]]:
    # Complex routing logic
    if state["complex_condition"]:
        return Command(goto="worker_a", update={"phase": "processing"})
    else:
        return Command(goto=["worker_b", "worker_c"])  # Parallel!

# Type hints enable graph rendering and static checking
```

**Key Features:**
- Mutate state AND select next node(s) in one return
- Parallel execution by returning multiple node names
- Runtime-dependent routing decisions

### Parallel Supersteps

When a routing function returns multiple node names, LangGraph runs them in parallel:

```python
def parallel_router(state):
    return Command(goto=["handler_a", "handler_b", "handler_c"])

# All three handlers execute in parallel
# LangGraph waits for ALL to complete before proceeding
```

### LangGraph Agent Protocol

Framework-agnostic protocol for cross-framework interoperability:

- Standardized interface for runs, threads, long-term memory
- Enables agents built on LangGraph to interoperate with AutoGen, CrewAI, etc.
- Protocol-level integration for multi-agent systems

---

## Backends and State Management

### Backend Types

#### StateBackend (Ephemeral)

```python
from deepagents.backends import StateBackend

agent = create_deep_agent(
    backend=lambda rt: StateBackend(rt)  # Default
)
```

**How it works:**
- Stores files in LangGraph agent state for current thread
- Persists across multiple agent turns via checkpoints
- Shared between supervisor and subagents
- Evicts automatically on thread completion

**Best for:**
- Scratch pad for intermediate results
- Automatic eviction of large tool outputs
- Per-thread temporary files

#### FilesystemBackend (Local Disk)

```python
from deepagents.backends import FilesystemBackend

agent = create_deep_agent(
    backend=FilesystemBackend(
        root_dir="/path/to/dir",
        virtual_mode=True  # Enable sandboxing
    )
)
```

**How it works:**
- Reads/writes real files under `root_dir`
- `virtual_mode=True`: Sandboxes paths (blocks `..`, `~`, absolute paths)
- Secure path resolution, prevents unsafe symlink traversal

**Security Considerations:**
- Agents can read any accessible file (including secrets)
- Combined with network tools, may enable SSRF attacks
- **NOT recommended for:** Web servers, HTTP APIs
- **Recommended safeguards:**
  1. Enable Human-in-the-Loop for sensitive operations
  2. Exclude secrets from accessible paths
  3. Use `virtual_mode=True`
  4. Use `SandboxBackend` for production

**Best for:**
- Local development CLIs
- CI/CD pipelines (with proper safeguards)
- Mounted persistent volumes

#### StoreBackend (LangGraph Store)

```python
from langgraph.store.memory import InMemoryStore
from deepagents.backends import StoreBackend

agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt),
    store=InMemoryStore()  # Or Redis, Postgres, etc.
)
```

**How it works:**
- Stores files in LangGraph `BaseStore`
- Cross-thread durable storage
- Survives thread completion

**Best for:**
- Long-term memories
- Shared state across conversations
- Deployments with LangSmith Deployment (auto-provisioned store)

#### CompositeBackend (Router)

```python
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

composite_backend = lambda rt: CompositeBackend(
    default=StateBackend(rt),
    routes={
        "/memories/": StoreBackend(rt),  # Persistent
        "/workspace/": FilesystemBackend(...),  # Local disk
    }
)

agent = create_deep_agent(backend=composite_backend)
```

**How it works:**
- Routes file operations based on path prefix
- Preserves original path prefixes in listings
- Longer prefixes win (e.g., `/memories/projects/` overrides `/memories/`)

**Best for:**
- Mixed ephemeral/persistent storage
- Multiple information sources as single filesystem
- Selective persistence (e.g., memories vs workspace)

### State Management

**LangGraph State Model:**
- Mutable state object accessible to all nodes
- Fields: `messages`, `files`, custom fields
- Checkpoints save state after each node execution

**Consistency:**
- Durable persistence for recoverable workflows
- Asynchronous mode: Faster throughput, small checkpoint loss risk
- Exact strong consistency semantics: Not specified in documentation

---

## Middleware Architecture

### TodoListMiddleware (Planning)

```python
from deepagents.middleware import TodoListMiddleware

agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    middleware=[
        TodoListMiddleware(
            system_prompt="Use write_todos to track progress..."  # Optional custom prompt
        )
    ]
)
```

**Provides:**
- `write_todos` tool for planning
- Automatic prompting to use tool during complex tasks
- Progress tracking and adaptation

**Inspired by:** Claude Code's todo list behavior

### FilesystemMiddleware (Context Management)

```python
from deepagents.middleware import FilesystemMiddleware

agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    middleware=[
        FilesystemMiddleware(
            backend=custom_backend,  # Optional: defaults to StateBackend
            system_prompt="Write to filesystem when...",  # Optional custom prompt
            custom_tool_descriptions={  # Optional: customize tool descriptions
                "ls": "Use ls when...",
                "read_file": "Use read_file to..."
            }
        )
    ]
)
```

**Provides:**
- `ls` - List files
- `read_file` - Read entire file or specific lines
- `write_file` - Create new file
- `edit_file` - Edit existing file

**Purpose:**
- Offload large context from conversation
- Handle variable-length tool results
- Enable piecewise reading of large outputs

### SubAgentMiddleware (Delegation)

```python
from deepagents.middleware import SubAgentMiddleware

agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    middleware=[
        SubAgentMiddleware(
            default_model="claude-sonnet-4-5-20250929",
            default_tools=[...],
            subagents=[...]
        )
    ]
)
```

**Provides:**
- `task` tool for spawning subagents
- Context isolation for delegated work
- Specialized instructions per subagent

**Built-in Subagents:**
- User-defined subagents (via configuration)
- `general-purpose` subagent (always available)

---

## When to Use DeepAgents vs Standard Agents

### Use DeepAgents When:

| Criterion | Indication |
|-----------|------------|
| **Task complexity** | Multi-step, requires decomposition |
| **Context size** | Large intermediate artifacts, variable-length results |
| **Fault tolerance** | Need checkpoints, recovery after failure |
| **Long-running** | Human-in-the-loop, approval workflows |
| **Memory** | Cross-thread persistence needed |
| **Specialization** | Different models/tools for different subtasks |

**Example Use Cases:**
- Research and multi-document synthesis
- Complex task automation with approval
- Multi-source knowledge routing (RAG across sources)
- Specialized domain handlers (legal, financial, technical)
- Frontend copilot experiences

### Use Standard LangChain Agents When:

| Criterion | Indication |
|-----------|------------|
| **Task complexity** | Single-step, simple tool use |
| **Context size** | Small, fits in context window |
| **Latency** | Extremely latency-sensitive |
| **Cost** | Minimal overhead desired |

**Example Use Cases:**
- One-shot QA
- Simple tool chaining
- Quick lookups
- Basic chatbots with tools

### Decision Checklist

```yaml
- Multi-step task requiring decomposition?
  Yes -> DeepAgents
  No ->
- Context size exceeds window?
  Yes -> DeepAgents (use filesystem)
  No ->
- Need cross-thread memory?
  Yes -> DeepAgents (use StoreBackend)
  No ->
- Need human-in-the-loop?
  Yes -> DeepAgents (use interrupt_on)
  No ->
- Extremely latency-sensitive?
  Yes -> Standard LangChain agent
  No -> DeepAgents
```

---

## Key Sources

### Official Documentation
- [DeepAgents Overview](https://docs.langchain.com/oss/python/deepagents/overview)
- [Subagents Documentation](https://docs.langchain.com/oss/python/deepagents/subagents)
- [Middleware Architecture](https://docs.langchain.com/oss/python/deepagents/middleware)
- [Backends Reference](https://docs.langchain.com/oss/python/deepagents/backends)

### External Resources
- [DeepAgents GitHub Repository](https://github.com/langchain-ai/deepagents)
- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [LangGraph Durable Execution](https://docs.langchain.com/oss/python/langgraph/durable-execution)
- [LangChain Multi-Agent Documentation](https://docs.langchain.com/oss/python/langchain/multi-agent)
- [Building Deep Agents with LangChain 1.0 (Medium)](https://medium.com/data-science-collective/building-deep-agents-with-langchain-1-0s-middleware-architecture-7fdbb3e47123)
- [Agents 2.0: From Shallow Loops to Deep Agents (Philipp Schmid)](https://www.philschmid.de/agents-2-0-deep-agents)

---

## Common Pitfalls and Best Practices

### Pitfalls

1. **Routing gaps and dead ends** - Missing fallback paths create unresolvable flows
2. **Cost and latency of subagents** - Extra model calls increase overhead
3. **Overuse for simple tasks** - Unnecessary complexity for trivial work
4. **Checkpoint semantics** - Asynchronous persistence carries small data loss risk

### Best Practices

1. **Design explicit routing rules** - Include fallbacks for all branches
2. **Use structured router outputs** - JSON with parsing fallbacks
3. **Choose appropriate backends** - StateBackend for ephemeral, StoreBackend for persistent
4. **Optimize model selection** - Use cheaper models for simple subagents
5. **Leverage LangSmith tracing** - Debug tool calls, prompts, decisions
6. **Keep subagent roles narrow** - Minimize cross-context confusion
7. **Instruct concise results** - Subagents should return summaries, not raw data

---

## Evidence Gaps

The documentation does NOT provide:
- Full end-to-end Python/TypeScript code samples (only API patterns shown)
- Quantitative benchmarks for latency, throughput, cost, or scalability
- Low-level network protocols or serialization formats for LangGraph Agent Protocol
- Formal consistency/transactional guarantees for distributed StoreBackend scenarios

---

## Summary for AGENTX Integration

DeepAgents provides a robust pattern for AGENTX's personal assistant architecture:

1. **Planning** - `TodoListMiddleware` aligns with AGENTX's goal-setting behavior
2. **Context Management** - `FilesystemMiddleware` solves context window issues
3. **Memory** - `StoreBackend` provides cross-thread persistence (similar to Mem0AI goals)
4. **Delegation** - Subagent pattern enables specialized experts (e.g., travel planner, code assistant)
5. **Routing** - LangGraph Commands enable dynamic, parallel workflows

**Recommended Integration Strategy:**
- Use DeepAgents as the orchestration layer
- Replace Mem0AI with LangGraph Store for memory
- Use DSPy for specialized subagent implementations
- Integrate FastMCP plugins as subagent tools
- Leverage LangGraph for streaming and checkpointing

---

**Document Status:** Research Complete
**Next Steps:** Evaluate migration path from current DSPy+Mem0AI architecture to DeepAgents-based implementation

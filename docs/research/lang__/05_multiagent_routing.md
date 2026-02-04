# LangGraph Multi-Agent Routing Patterns

Research document covering multi-agent routing, conditional routing, agent selector patterns, dynamic agent assembly, supervisor patterns, and subgraph nesting in LangGraph.

**Research Date:** 2026-02-04
**Focus:** Python implementation patterns for multi-agent coordination

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Core Concepts & API Primitives](#core-concepts--api-primitives)
3. [Conditional Routing Patterns](#conditional-routing-patterns)
4. [Agent Selector Patterns](#agent-selector-patterns)
5. [Dynamic Agent Assembly](#dynamic-agent-assembly)
6. [Supervisor Pattern](#supervisor-pattern)
7. [Subgraph Nesting](#subgraph-nesting)
8. [End-to-End Examples](#end-to-end-examples)
9. [Routing Function Design](#routing-function-design)
10. [Error Handling & Retries](#error-handling--retries)
11. [Testing Strategies](#testing-strategies)
12. [Best Practices](#best-practices)
13. [Evidence Gaps](#evidence-gaps)

---

## Executive Summary

LangGraph provides flexible primitives for multi-agent routing:

- **Static conditional edges** - Route based on routing functions that inspect state
- **Dynamic routing via Command objects** - Nodes can return `Command(update=..., goto="node")` to atomically update state and route
- **Agent selector patterns** - Runtime choice of agents/models/tools based on state
- **Supervisor pattern** - Central coordinator that delegates to specialized workers
- **Subgraph nesting** - Hierarchical composition for complex agent structures

**Key Architectural Decision Points:**

| Pattern | Best For | Tradeoffs |
|---------|----------|-----------|
| Conditional Edges | Graph-level routing policy, shared routing logic | Separate from node logic |
| Command.goto | Local node decisions needing atomic state+route | Decision lives inside node |
| Static Graph | Stable agent pool, low compile overhead | Larger LLM context |
| Dynamic Assembly | Variable task structures, smaller context | Per-request compile cost |
| Supervisor | Policy enforcement, tool access control | Central point of coordination |
| Subgraphs | Modular encapsulation, hierarchical teams | State mapping overhead |

---

## Core Concepts & API Primitives

### State Model (AgentState / StateGraph)

```python
from typing import Dict, List, TypedDict

class AgentState(TypedDict):
    """Standard state schema for LangGraph agents."""
    messages: List[Dict]
    current_input: str
    tools_output: Dict
    status: str  # "RUNNING", "ERROR", "COMPLETE"
    error_count: int
```

Key points:
- State is explicit and passed between nodes
- Routing functions read/write state to control flow
- StateGraph supports schema definition via `Annotation.Root`

### Nodes, Edges, and Conditional Edges

```python
from langgraph import StateGraph, START, END

# Create a graph with state schema
graph = StateGraph(AgentState)

# Add nodes (Python functions)
graph.add_node("agent_1", agent_1_function)
graph.add_node("agent_2", agent_2_function)

# Normal edge (direct transition)
graph.add_edge("agent_1", "agent_2")

# Conditional edge (function-based routing)
graph.add_conditional_edges(
    "agent_1",
    route_by_status,
    {
        "process": "execute_tool",
        "retry": "retry_handler",
        "error": "error_handler",
        "end": END
    }
)
```

### Command Objects (Dynamic Routing)

```python
from langgraph import Command

def agent_with_routing(state: AgentState) -> Command[Literal["next_agent", END]]:
    """Node that dynamically routes based on its computation."""
    result = process_something(state["current_input"])

    if result.is_complete:
        return Command(
            update={"status": "COMPLETE", "result": result.value},
            goto=END
        )
    else:
        return Command(
            update={"intermediate": result.partial},
            goto="next_agent"
        )
```

**When to use Command vs Conditional Edges:**

- **Use Command** when you need to both update state AND route in the same operation (e.g., multi-agent handoffs)
- **Use conditional edges** when routing without updating state, or for graph-level routing policy

---

## Conditional Routing Patterns

### Pattern 1: Routing Function Based on State

```python
from typing import Literal

def route_by_status(state: AgentState) -> Literal["process", "retry", "error", "end"]:
    """Routing function that inspects state and returns destination key."""
    if state["status"] == "RUNNING" and state["error_count"] == 0:
        return "process"
    if state["status"] == "RUNNING" and state["error_count"] > 0:
        return "retry"
    if state["status"] == "ERROR":
        return "error"
    return "end"

# Wire up to graph
graph.add_conditional_edges(
    "check_status",
    route_by_status,
    {
        "process": "execute_tool",
        "retry": "retry_handler",
        "error": "error_handler",
        "end": END
    }
)
```

### Pattern 2: Intent-Based Classification Routing

```python
def route_by_intent(state: AgentState) -> Literal["weather", "calculator", "fallback"]:
    """Classify user intent and route to appropriate agent."""
    query = state["current_input"].lower()

    # Keyword-based classification
    if any(word in query for word in ["weather", "rain", "forecast", "temperature"]):
        return "weather"
    if any(tok.isdigit() for tok in query.split()):
        return "calculator"
    return "fallback"

graph.add_conditional_edges(
    "intent_classifier",
    route_by_intent,
    {
        "weather": "weather_agent",
        "calculator": "calculator_agent",
        "fallback": "fallback_agent"
    }
)
```

### Pattern 3: Confidence-Based Routing

```python
def route_by_confidence(state: AgentState) -> Literal["respond", "clarify", "escalate"]:
    """Route based on classification confidence."""
    confidence = state.get("classification_confidence", 0.0)

    if confidence >= 0.9:
        return "respond"
    elif confidence >= 0.5:
        return "clarify"
    else:
        return "escalate"

graph.add_conditional_edges(
    "classifier",
    route_by_confidence,
    {
        "respond": "final_response",
        "clarify": "clarification_agent",
        "escalate": "human_escalation"
    }
)
```

---

## Agent Selector Patterns

### Pattern 1: Model/Tool Selection by Task Type

```python
def model_selector(state: AgentState) -> str:
    """Select appropriate LLM based on task requirements."""
    task = state["current_input"].lower()

    if any(word in task for word in ["invest", "risk", "financial"]):
        return "gpt4_agent"  # High-stakes reasoning
    if any(word in task for word in ["summarize", "simple", "quick"]):
        return "gpt35_agent"  # Cost-effective
    return "default_agent"

graph.add_conditional_edges(
    "model_selector",
    model_selector,
    {
        "gpt4_agent": "gpt4_node",
        "gpt35_agent": "gpt35_node",
        "default_agent": "fallback_node"
    }
)
```

### Pattern 2: Priority-Based Selector

```python
def priority_selector(state: AgentState) -> str:
    """Select agent based on priority level in state."""
    priority = state.get("priority", "normal")

    if priority == "urgent":
        return "urgent_handler"
    elif priority == "high":
        return "high_priority_handler"
    else:
        return "standard_handler"

graph.add_conditional_edges(
    "priority_router",
    priority_selector,
    {
        "urgent_handler": "urgent_agent",
        "high_priority_handler": "high_priority_agent",
        "standard_handler": "standard_agent"
    }
)
```

### Pattern 3: Capability-Based Selector

```python
def capability_selector(state: AgentState) -> str:
    """Route to agent with required capabilities."""
    required_capabilities = state.get("required_capabilities", [])

    if "vision" in required_capabilities:
        return "vision_agent"
    if "code_execution" in required_capabilities:
        return "code_agent"
    if "web_search" in required_capabilities:
        return "search_agent"
    return "chat_agent"

graph.add_conditional_edges(
    "capability_router",
    capability_selector,
    {
        "vision_agent": "vision_node",
        "code_agent": "code_node",
        "search_agent": "search_node",
        "chat_agent": "chat_node"
    }
)
```

---

## Dynamic Agent Assembly

### Approach 1: Runtime Graph Generation

```python
def planner_node(state: AgentState) -> Command:
    """Plan tasks and dynamically create worker nodes."""
    query = state["current_input"]

    # LLM-based planning to decompose into subtasks
    plan = llm_plan(query)
    # Example: plan = ["research", "analyze", "summarize"]

    # Dynamically create nodes for each task
    builder = StateGraph(AgentState)

    for idx, task in enumerate(plan):
        node_name = f"worker_{idx}"
        task_func = make_worker_func(task)
        builder.add_node(node_name, task_func)

    # Wire up edges
    builder.add_edge(START, "worker_0")
    for i in range(len(plan) - 1):
        builder.add_edge(f"worker_{i}", f"worker_{i+1}")
    builder.add_edge(f"worker_{len(plan)-1}", END)

    # Compile and execute
    dynamic_graph = builder.compile()
    result = dynamic_graph.invoke(state)

    return Command(update=result, goto=END)
```

### Approach 2: Static Graph with State-Based Selection

```python
# Define large static graph
graph = StateGraph(AgentState)

# Add all possible agents
graph.add_node("research_agent", research_agent)
graph.add_node("analysis_agent", analysis_agent)
graph.add_node("summary_agent", summary_agent)
graph.add_node("code_agent", code_agent)

# Use state to select which agents to activate
def execution_controller(state: AgentState) -> Command:
    """Control which agents execute based on plan."""
    active_agents = state.get("active_agents", ["research_agent"])

    # Set flags that nodes check
    updated_state = state.copy()
    for agent_name in ["research_agent", "analysis_agent", "summary_agent"]:
        updated_state[f"{agent_name}_enabled"] = agent_name in active_agents

    return Command(update=updated_state, goto="research_agent")

# Nodes check their enabled flag before executing
def research_agent(state: AgentState) -> AgentState:
    if not state.get("research_agent_enabled", False):
        return state  # Skip if not enabled
    # ... actual work ...
    return state
```

### Tradeoffs

| Approach | Pros | Cons |
|----------|------|------|
| Runtime Generation | Smaller LLM context, flexible | Per-request compile overhead |
| Static + State Selection | No compile overhead | Larger context, unused nodes |

---

## Supervisor Pattern

### Concept

The supervisor pattern centralizes routing, validation, and tool access control. The supervisor acts as a central coordinator whose "tools" are other agents.

```python
from typing import Literal
from langgraph import Command

def supervisor(state: AgentState) -> Command[Literal["agent_1", "agent_2", END]]:
    """
    Supervisor that delegates to specialized workers.

    Uses structured output from LLM to determine which agent to call next.
    """
    messages = state["messages"]

    # Call LLM with structured output
    response = supervisor_llm.invoke(messages)

    # Parse structured decision
    next_agent = response.get("next_agent")
    update_data = response.get("update", {})

    # Route to chosen agent
    if next_agent == "__end__":
        return Command(update=update_data, goto=END)

    return Command(
        update={
            **update_data,
            "current_agent": next_agent
        },
        goto=next_agent
    )
```

### Supervisor Graph Structure

```python
# Build supervisor graph
graph = StateGraph(AgentState)

# Add supervisor
graph.add_node("supervisor", supervisor)

# Add worker agents
graph.add_node("agent_1", agent_1)
graph.add_node("agent_2", agent_2)

# Wire supervisor as central router
graph.add_edge(START, "supervisor")

# Workers always return to supervisor
graph.add_edge("agent_1", "supervisor")
graph.add_edge("agent_2", "supervisor")

# Supervisor decides next step
graph.add_conditional_edges(
    "supervisor",
    lambda s: s["current_agent"],
    {
        "agent_1": "agent_1",
        "agent_2": "agent_2",
        "__end__": END
    }
)
```

### Hierarchical Supervisors

```python
# Level 1: Main supervisor
main_supervisor = create_supervisor(
    agents={
        "research_team": research_subgraph,
        "analysis_team": analysis_subgraph,
    }
)

# Level 2: Team supervisors
research_supervisor = create_supervisor(
    agents={
        "web_researcher": web_research_agent,
        "database_researcher": db_research_agent,
    }
)

analysis_supervisor = create_supervisor(
    agents={
        "quant_analyst": quant_agent,
        "qual_analyst": qual_agent,
    }
)
```

### Supervisor with Handoffs

```python
def supervisor_with_handoff(state: AgentState) -> Command:
    """Supervisor that supports agent handoffs with state passing."""
    last_agent = state.get("last_agent", "supervisor")
    messages = state["messages"]

    # LLM decides next agent with handoff reasoning
    decision = supervisor_llm_with_handoff.invoke(
        messages + [{"role": "system", "content": f"Last agent: {last_agent}"}]
    )

    next_agent = decision["next_agent"]
    handoff_context = decision.get("handoff_context", {})

    return Command(
        update={
            "last_agent": next_agent,
            "handoff_context": handoff_context
        },
        goto=next_agent
    )
```

---

## Subgraph Nesting

### Pattern 1: Invoke Subgraph from Node

```python
# Compile subgraph
currency_subgraph = currency_graph.compile()
weather_subgraph = weather_graph.compile()

def invoke_subgraph_node(state: AgentState) -> AgentState:
    """Node that invokes a subgraph with state mapping."""
    query = state["current_input"]

    if "currency" in query.lower():
        # Map parent state to subgraph input
        sub_input = {
            "query": query,
            "user_id": state.get("user_id")
        }

        # Invoke subgraph
        sub_result = currency_subgraph.invoke(sub_input)

        # Map subgraph output back to parent state
        state["tools_output"]["currency_result"] = sub_result.get("result")

    return state
```

### Pattern 2: Add Subgraph as Node

```python
from langgraph.graph import Subgraph

# Create subgraph
subgraph = StateGraph(SubgraphState)
subgraph.add_node("sub_agent", sub_agent_function)
subgraph.add_edge(START, "sub_agent")
subgraph.add_edge("sub_agent", END)
compiled_subgraph = subgraph.compile()

# Add to parent graph
parent_graph = StateGraph(ParentState)
parent_graph.add_node("subgraph_wrapper", compiled_subgraph)
parent_graph.add_edge(START, "subgraph_wrapper")
parent_graph.add_edge("subgraph_wrapper", END)
```

### Pattern 3: Hierarchical Subgraphs

```python
# Level 3: Leaf agents
leaf_agent_1 = StateGraph(AgentState)
leaf_agent_1.add_node("worker", worker_1)
# ...

# Level 2: Team subgraph
team_subgraph = StateGraph(TeamState)
team_subgraph.add_node("leaf_1", leaf_agent_1.compile())
team_subgraph.add_node("leaf_2", leaf_agent_2.compile())
team_subgraph.add_node("team_supervisor", team_supervisor)
# ...

# Level 1: Organization
org_graph = StateGraph(OrgState)
org_graph.add_node("team_a", team_subgraph.compile())
org_graph.add_node("team_b", team_subgraph.compile())
org_graph.add_node("org_supervisor", org_supervisor)
# ...
```

---

## End-to-End Examples

### Example 1: Conditional Routing + Selector

```python
from typing import Dict, Literal
from langgraph import StateGraph, Command, START, END

class AgentState(dict):
    def __init__(self, current_input="", messages=None, tools_output=None,
                 status="RUNNING", error_count=0):
        super().__init__()
        self["current_input"] = current_input
        self["messages"] = messages or []
        self["tools_output"] = tools_output or {}
        self["status"] = status
        self["error_count"] = error_count

def forecast_weather_selector(state: AgentState) -> str:
    """Route based on query keywords."""
    q = state["current_input"].lower()
    if "weather" in q or "rain" in q or "forecast" in q:
        return "weather_node"
    if any(tok.isdigit() or tok in ["+", "-", "*", "/"] for tok in q.split()):
        return "calc_node"
    return "fallback_node"

def weather_node(state: AgentState) -> AgentState:
    """Weather agent - simulate tool call."""
    state["tools_output"]["forecast"] = "It's going to rain."
    state["status"] = "COMPLETE"
    return state

def calc_node(state: AgentState) -> AgentState:
    """Calculator agent - simple arithmetic."""
    state["tools_output"]["calc"] = "2+2=4"
    state["status"] = "COMPLETE"
    return state

def fallback_node(state: AgentState) -> AgentState:
    """Fallback agent."""
    state["tools_output"]["fallback"] = "I couldn't understand that."
    state["status"] = "COMPLETE"
    return state

# Build graph
graph = StateGraph(AgentState)
graph.add_node("router", lambda s: s)
graph.add_node("weather_node", weather_node)
graph.add_node("calc_node", calc_node)
graph.add_node("fallback_node", fallback_node)

graph.add_edge(START, "router")
graph.add_conditional_edges(
    "router",
    forecast_weather_selector,
    {
        "weather_node": "weather_node",
        "calc_node": "calc_node",
        "fallback_node": "fallback_node"
    }
)
graph.add_edge("weather_node", END)
graph.add_edge("calc_node", END)
graph.add_edge("fallback_node", END)

# Execute
compiled = graph.compile()
result = compiled.invoke({"current_input": "Will it rain today?"})
print(result["tools_output"])  # {'forecast': "It's going to rain."}
```

### Example 2: Supervisor with Subgraphs

```python
from langgraph_supervisor import create_supervisor

# Compile subgraphs
currency_subgraph = currency_graph.compile()
weather_subgraph = weather_graph.compile()

def supervisor_router(state: AgentState) -> Command:
    """Supervisor that routes to specialized subgraphs."""
    q = state["current_input"].lower()

    if "exchange" in q or "currency" in q:
        return Command(update={"target_subgraph": "currency"}, goto="currency_worker")
    if "weather" in q:
        return Command(update={"target_subgraph": "weather"}, goto="weather_worker")
    return Command(update={}, goto="fallback_worker")

# Create supervisor
supervisor = create_supervisor(
    agents={
        "currency_worker": currency_subgraph,
        "weather_worker": weather_subgraph,
        "fallback_worker": fallback_agent,
    },
    output_mode="final_only",
    add_handoff_back_messages=True
)

# Execute
response = supervisor.invoke({
    "current_input": "What's the USD to EUR rate?",
    "user_id": "user_123"
})
print(response)
```

---

## Routing Function Design

### Best Practices

1. **Deterministic routing** - Same state should always route to same destination
2. **Explicit state keys** - Use dedicated state fields for routing decisions
3. **Avoid brittle parsing** - Don't rely on raw LLM output parsing
4. **Return enumerated values** - Use string literals or enums for destinations

### Good Pattern

```python
def route_by_status(state: AgentState) -> Literal["process", "retry", "error"]:
    """Clean routing based on explicit state fields."""
    status = state["status"]
    error_count = state["error_count"]

    if status == "ERROR":
        return "error"
    if error_count > 3:
        return "error"
    if error_count > 0:
        return "retry"
    return "process"
```

### Anti-Pattern

```python
def route_by_status(state: AgentState) -> str:
    """Brittle - relies on parsing LLM output."""
    last_message = state["messages"][-1]["content"]

    # Brittle keyword matching
    if "error" in last_message.lower():
        return "error"
    # What if LLM phrases it differently?
    return "process"
```

---

## Error Handling & Retries

### Retry Policy

```python
from langgraph import RetryPolicy

retry_policy = RetryPolicy(
    max_attempts=5,
    initial_interval=1.0,
    backoff_factor=2.0,
    max_interval=10.0,
    retry_on=APIError
)

# Attach to node
graph.add_node(
    "external_api_call",
    api_call_function,
    retry=retry_policy
)
```

### Fallback Pattern

```python
def agent_with_fallback(state: AgentState) -> Command:
    """Agent with fallback on error."""
    try:
        result = risky_operation(state["current_input"])
        return Command(
            update={"result": result},
            goto="next_step"
        )
    except Exception as e:
        state["error_count"] += 1
        if state["error_count"] > 3:
            return Command(
                update={"error": str(e)},
                goto="human_escalation"
            )
        return Command(
            update=state,
            goto="fallback_agent"
        )
```

---

## Testing Strategies

### Unit Tests

```python
import pytest

def test_weather_node_updates_state():
    """Test weather node in isolation."""
    state = AgentState(
        current_input="Will it rain?",
        tools_output={}
    )
    result = weather_node(state)
    assert "forecast" in result["tools_output"]
    assert result["status"] == "COMPLETE"

def test_router_routes_to_weather():
    """Test routing logic."""
    graph = build_example_graph()
    compiled = graph.compile()

    result = compiled.invoke({
        "current_input": "Will it rain today?"
    })

    assert "forecast" in result["tools_output"]
```

### Integration Tests

```python
def test_full_supervisor_flow():
    """Test end-to-end supervisor delegation."""
    supervisor = create_supervisor(agents={
        "weather": weather_agent,
        "calc": calc_agent
    })

    result = supervisor.invoke({
        "current_input": "What's 2+2?"
    })

    assert "calc" in result["tools_output"]
```

---

## Best Practices

1. **Prefer explicit state** - Use dedicated state fields for routing decisions
2. **Command for atomic updates** - Use `Command(update=..., goto=...)` when state+route must be atomic
3. **Centralize tool access** - Use supervisor pattern for policy enforcement
4. **Implement RetryPolicy** - Add retries for transient failures
5. **Design fallback nodes** - Handle retry exhaustion gracefully
6. **Cache compiled graphs** - Avoid repeated compilation for dynamic graphs
7. **Avoid ambiguous routing** - Ensure conditional edges and Command.goto are consistent
8. **Log routing decisions** - Emit trace events for debugging

---

## Evidence Gaps

The following areas require further investigation of official documentation:

1. **Exact API signatures** - Full method signatures for `create_supervisor()`, `compile()`, `invoke()`
2. **Persistence backends** - Concrete storage adapters and serialization formats
3. **Async/concurrency APIs** - Exact primitives for parallel worker execution
4. **Streaming APIs** - Token and event streaming interfaces
5. **Tracing utilities** - Built-in observability and instrumentation APIs

---

## Sources

### Official Documentation
- [LangGraph Graph API Overview](https://docs.langchain.com/oss/python/langgraph/graph-api) - Core API primitives
- [LangChain Multi-Agent Documentation](https://docs.langchain.com/oss/python/langgraph/multi-agent) - Multi-agent patterns (404 - moved location)

### Tutorials & Guides
- [LangGraph Multi-Agent Workflows (LangChain Blog)](https://www.blog.langchain.com/langgraph-multi-agent-workflows/) - Supervisor patterns, hierarchical teams
- [Multi-Agent Structures (LangChain OpenTutorial)](https://langchain-opentutorial.gitbook.io/langchain-opentutorial/17-langgraph/02-structures/08-langgraph-multi-agent-structures-01) - Hands-off patterns, handoffs
- [Advanced LangGraph: Conditional Edges (Dev.to)](https://dev.to/jamesli/advanced-langgraph-implementing-conditional-edges-and-tool-calling-agents-3pdn) - Conditional edge examples

### Community Resources
- [Building a Supervisor Multi-Agent System (Medium)](https://medium.com/@mnai0377/building-a-supervisor-multi-agent-system-with-langgraph-hierarchical-intelligence-in-action-3e9765af181c) - Supervisor implementation
- [LangGraph Multi-Agent Design Pattern (GitHub)](https://github.com/TonySimonovsky/ai-champ-design-patterns/blob/main/ai-agents/LangGraph-multi-agent-user-facing.ipynb) - User-facing patterns
- [Multi-Agent System Design Patterns (Medium)](https://medium.com/@princekrampah/multi-agent-architecture-in-multi-agent-systems-multi-agent-system-design-patterns-langgraph-b92e934bf843) - Design patterns

### Code References
- [langgraph-supervisor-py (GitHub)](https://github.com/langchain-ai/langgraph-supervisor-py) - Supervisor library
- [LangGraph Main Repository](https://github.com/langchain-ai/langgraph) - Official examples

---

## Additional Research Needed

1. **DSPy vs LangGraph integration** - How to combine DSPy ReAct agents with LangGraph routing
2. **MCP tool integration** - Model Context Protocol integration with supervisor pattern
3. **State persistence strategies** - Best practices for long-running agent conversations
4. **Performance benchmarks** - Static vs dynamic graph performance at scale
5. **Memory integration** - Combining Mem0AI with LangGraph state management

---

**Next Steps:** Consider investigating how to adapt these LangGraph patterns for AGENTX's DSPy-based architecture.

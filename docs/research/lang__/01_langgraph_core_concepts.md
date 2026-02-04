# LangGraph Core Concepts

**Research Date:** 2025-02-04
**Topic:** LangGraph StateGraph, Nodes, Edges, Message Passing, and Routing

---

## Executive Summary

LangGraph is a stateful, graph-based workflow framework for building AI agents. Its core philosophy: **"Nodes do the work, edges tell what to do next."** This document covers the fundamental concepts needed to integrate DSPy agents with LangGraph orchestration.

## 1. StateGraph and Agent State Management

### What is StateGraph?

`StateGraph` is LangGraph's primary class for building stateful workflows. Unlike regular graphs, StateGraph maintains a shared state that evolves as nodes execute.

### State Schema Definition

State can be defined using three approaches:

#### 1. TypedDict (Recommended for DSPy Integration)
```python
from typing import TypedDict, Annotated, List
from typing_extensions import TypedDict

class AgentState(TypedDict):
    messages: Annotated[List[str], "Conversation history"]
    current_input: str
    context: dict
    step: int
```

#### 2. Pydantic Models
```python
from pydantic import BaseModel

class AgentState(BaseModel):
    messages: List[str] = []
    current_input: str = ""
    context: dict = {}
    step: int = 0
```

#### 3. MessagesState (Prebuilt)
```python
from langgraph.graph import MessagesState

# Inherits predefined 'messages' field
class MyState(MessagesState):
    custom_field: str = ""
```

### Reducers: How State Updates Merge

Reducers define how multiple state updates combine:

```python
from typing import Annotated

def append_messages(left, right):
    """Custom reducer for appending messages"""
    if not left:
        left = []
    left.extend(right)
    return left

class AgentState(TypedDict):
    # Default append reducer for messages
    messages: Annotated[List[str], append_messages]

    # Default replace reducer (no annotation needed)
    current_step: int
```

**Built-in Reducers:**
- `replace` (default): Overwrites old value
- `add`: For numeric counters
- `append`: For lists
- Custom: Your own reducer function

### State Update Patterns

```python
# Node function signature
def my_node(state: AgentState) -> dict:
    # Read from state
    current_input = state["current_input"]

    # Return partial state update (NOT full state)
    return {
        "messages": ["New message"],
        "current_step": state["current_step"] + 1
    }
```

**Critical:** Nodes return **partial updates**, not the full state. LangGraph merges these using reducers.

## 2. Message Passing and Routing Mechanisms

### Pregel-Inspired Execution

LangGraph uses Google's Pregel message-passing algorithm:

1. **Super-steps:** Discrete iterations over the graph
2. **Node activation:** Nodes activate when they receive messages
3. **Parallel execution:** Nodes with independent inputs run concurrently
4. **Termination:** All nodes inactive + no messages in transit

```python
# Execution flow visualization
# Super-step 1: node_a and node_b run in parallel
# Super-step 2: node_c runs (depends on a and b)
# Super-step 3: termination if no more messages
```

### Message Passing Flow

```python
# Node A produces output
def node_a(state: AgentState):
    return {"messages": ["From A"], "next": "b"}

# Node B receives A's output (via state)
def node_b(state: AgentState):
    # Can read what node_a wrote to state
    return {"messages": ["From B"], "next": "c"}
```

## 3. Conditional Edges and Dynamic Routing

### Conditional Edges

Route based on state with a routing function:

```python
from langgraph.graph import StateGraph, START, END

def route_by_intent(state: AgentState) -> str:
    """Routing function returns node name as string"""
    query = state["current_input"].lower()

    if "weather" in query:
        return "weather_agent"
    elif "calculator" in query:
        return "calculator_agent"
    else:
        return END  # Built-in terminator

# Add conditional edge
graph.add_conditional_edges(
    "router_node",
    route_by_intent,
    {
        "weather_agent": "weather_agent",
        "calculator_agent": "calculator_agent",
        END: END
    }
)
```

### Command Objects (Unified Update + Routing)

Introduced in LangGraph 0.2+, `Command` allows atomic state+route decisions:

```python
from langgraph.types import Command

def smart_node(state: AgentState) -> Command[Literal["a", "b", END]]:
    # Decide based on state
    if state["confidence"] > 0.8:
        return Command(
            update={"result": "high_confidence_answer"},
            goto="a"
        )
    else:
        return Command(
            update={"result": "low_confidence"},
            goto="b"
        )
```

**Benefits of Command:**
- Routing logic lives **inside** the node
- State update and routing are atomic
- No separate router function needed
- Better for runtime adaptation

### Send Objects (Map-Reduce)

```python
from langgraph.types import Send

def fan_out(state: AgentState):
    # Create multiple parallel execution paths
    return [
        Send("process_item", {"item": item})
        for item in state["items"]
    ]
```

## 4. Agent Loops and Iteration

### Recursion Limit

LangGraph has a default recursion limit of 1000 super-steps:

```python
from langgraph.errors import GraphRecursionError

try:
    result = app.invoke(inputs)
except GraphRecursionError:
    print("Graph exceeded recursion limit!")
```

### Accessing the Step Counter

```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

def check_recursion(state: AgentState, config):
    """Check remaining steps before continuing"""
    remaining = config.get("recursion_limit", 1000) - config.get("step", 0)
    if remaining < 10:
        return Command(goto=END, update={"error": "Approaching limit"})
    return {"continue": True}
```

### Loop Patterns

#### ReAct Loop
```python
def should_continue(state: AgentState) -> str:
    """Decide whether to continue thinking"""
    if state.get("tool_calls"):
        return "tools"
    return END

graph.add_conditional_edges("agent", should_continue)
```

#### Reflection Loop
```python
def reflect_until_satisfied(state: AgentState) -> str:
    """Keep refining until quality threshold"""
    if state["quality_score"] > 0.9:
        return END
    return "refine_node"
```

#### Retry Loop
```python
def retry_with_backoff(state: AgentState) -> str:
    """Retry failed operations with exponential backoff"""
    if state["attempts"] >= 3:
        return END
    if state["last_error"]:
        return "retry_node"
    return END
```

## 5. Core Abstractions

### Nodes (Computation Units)

```python
# Simple function node
def simple_node(state: AgentState):
    return {"output": "processed"}

# LLM-powered node
def llm_node(state: AgentState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# Tool-calling node
def tool_node(state: AgentState):
    result = tool.invoke(state["tool_input"])
    return {"tool_result": result}
```

### Edges (Flow Control)

```python
# Normal edge (deterministic)
graph.add_edge("node_a", "node_b")

# Conditional edge (dynamic routing)
graph.add_conditional_edges("router", route_function, mapping)

# Entry point
graph.add_edge(START, "first_node")

# Exit point
graph.add_edge("last_node", END)
```

### Graphs (Container)

```python
from langgraph.graph import StateGraph, START, END

# Build the graph
graph = StateGraph(AgentState)
graph.add_node("node_a", node_a)
graph.add_node("node_b", node_b)
graph.add_edge(START, "node_a")
graph.add_edge("node_a", "node_b")
graph.add_edge("node_b", END)

# Compile for execution
app = graph.compile()
```

## 6. Integration with DSPy

### Wrapping DSPy Modules as Nodes

```python
import dspy

# Define DSPy module
class DSPyAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought("question->answer")

    def forward(self, question):
        return self.prog(question=question)

# Wrap for LangGraph
dspy_agent = DSPyAgent()

def dspy_node(state: AgentState):
    result = dspy_agent(question=state["current_input"])
    return {"messages": [result.answer]}
```

### Converting DSPy Signatures to State

```python
# DSPy signature
signature = "context: str, question: str -> answer: str, reasoning: str"

# LangGraph state schema
class DSPyState(TypedDict):
    context: str
    question: str
    answer: str
    reasoning: str
```

### Memory Integration

```python
# DSPy ReAct with Mem0
class Mem0ReActAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.reAct = dspy.ReAct("question->answer", tools=tools)

# LangGraph wrapper
def mem0_node(state: AgentState, config):
    # Use thread_id from config for Mem0 session
    user_id = config["configurable"]["thread_id"]
    result = mem0_react_agent(question=state["current_input"], user_id=user_id)
    return {"messages": [result.answer]}
```

## 7. Best Practices

### State Design
- Use `TypedDict` for static typing
- Keep state minimal (only what nodes need)
- Use reducers for list fields
- Avoid storing large objects in state

### Node Design
- Keep nodes focused (single responsibility)
- Return partial state updates only
- Use type hints for clarity
- Document state mutations

### Performance
- Minimize state size
- Use `Send` for parallel fan-out
- Cache expensive operations
- Profile node execution time

### Testing
- Test nodes in isolation
- Mock LLM calls for unit tests
- Verify reducer behavior
- Test edge cases (empty state, missing keys)

### Debugging
- Use `debug=True` in compile
- Print state at node boundaries
- Check LangGraph's tracing UI
- Log all state transitions

## 8. Comparison: LangGraph vs DSPy

| Aspect | LangGraph | DSPy |
|--------|-----------|------|
| **Primary Focus** | Orchestration & State | Prompt Optimization |
| **State Management** | Explicit (TypedDict) | Implicit (signatures) |
| **Control Flow** | Graph edges & routing | Module composition |
| **Memory** | Checkpointing | ReAct patterns |
| **Training** | None | GEPA, MIPROv2 |
| **Tools** | ToolNode | dspy.Tool |
| **Best For** | Complex workflows, multi-agent | Single-agent optimization |

**Key Insight:** Use them together! DSPy for agent internals, LangGraph for orchestration.

## 9. Quick Reference

### Creating a Graph
```python
from langgraph.graph import StateGraph, START, END

graph = StateGraph(StateSchema)
graph.add_node("node_name", node_function)
graph.add_edge(START, "node_name")
graph.add_edge("node_name", END)
app = graph.compile(checkpointer=memory)
```

### Invoking a Graph
```python
# Basic invoke
result = app.invoke({"messages": ["hello"]})

# With config (for memory)
config = {"configurable": {"thread_id": "session-123"}}
result = app.invoke({"messages": ["hello"]}, config=config)

# Streaming
for chunk in app.stream(inputs, stream_mode="updates"):
    print(chunk)
```

### State Access Pattern
```python
def my_node(state: MyState) -> dict:
    # READ from state
    current_value = state["field_name"]

    # WRITE partial update
    return {"field_name": "new_value"}
```

## Sources

- [LangGraph Graph API Documentation](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [LangGraph Concepts - Medium](https://medium.com/@diwakarkumar_18755/mastering-langgraph-understanding-core-concepts-graph-vs-a3ec2f5d54ae)
- [Built with LangGraph #4: Components](https://medium.com/@okanyenigun/built-with-langgraph-4-components-d26701f7d16d)
- [LangGraph Deep Dive - Dev.to](https://dev.to/raunaklallala/understanding-core-concepts-of-langgraph-deep-dive-1d7h)
- [From State to Edges: CodeMancers](https://www.codemancers.com/blog/langgraph-states-nodes-edges)
- [Dynamic Routing with Command - DEV.to](https://dev.to/aiengineering/a-beginners-guide-to-dynamic-routing-in-langgraph-with-command-2c5l)
- [LangGraph YouTube: State & Schema](https://www.youtube.com/watch?v=jVZ8mcAiBiY)

---

**Next Steps:**
- See `02_deepagents_architecture.md` for multi-agent patterns
- See `06_dspy_langgraph_integration.md` for DSPy integration patterns
- See `04_async_streaming_patterns.md` for async streaming implementation

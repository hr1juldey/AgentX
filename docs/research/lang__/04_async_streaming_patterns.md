# LangGraph Async Streaming Patterns

**Author:** Claude Code
**Date:** 2026-02-04
**Version:** 1.0
**Status:** Final Research Report

## Table of Contents

1. [Overview](#overview)
2. [astream() and astream_events() Methods](#1-astream-and-astream_events-methods)
3. [Implementing Async Streaming Nodes](#2-implementing-async-streaming-nodes)
4. [Streaming Partial Outputs from Agents](#3-streaming-partial-outputs-from-agents)
5. [Managing Async State Across Agent Boundaries](#4-managing-async-state-across-agent-boundaries)
6. [Error Handling in Async Streaming Workflows](#5-error-handling-in-async-streaming-workflows)
7. [Best Practices and Patterns](#best-practices-and-patterns)
8. [Known Issues and Limitations](#known-issues-and-limitations)
9. [Code Examples](#code-examples)
10. [References](#references)

---

## Overview

LangGraph implements a comprehensive streaming system designed to surface real-time updates from agent workflows. This system is critical for building responsive AI applications, as it allows displaying output progressively before complete responses are ready, significantly improving user experience (UX) particularly when dealing with LLM latency.

### Key Benefits of Async Streaming

- **Improved Responsiveness**: Users see progress updates in real-time
- **Better UX**: Token-by-token streaming creates ChatGPT-like experiences
- **Debugging Capabilities**: Detailed event streams reveal execution flow
- **Early Feedback**: Partial results allow users to make decisions faster
- **Resource Efficiency**: Stream processing avoids buffering large responses

### Streaming System Architecture

LangGraph's streaming leverages its Runnable/callback framework. An agent built via `create_agent()` is essentially a LangGraph graph of runnables. When calling `agent.stream()`, LangGraph orchestrates graph execution and hooks into each step, firing callback events like `on_llm_new_token` that the streaming API surfaces immediately to callers.

---

## 1. astream() and astream_events() Methods

### 1.1 Basic astream() Usage

The `astream()` method is the primary async streaming interface in LangGraph. It yields outputs as an async generator as the agent progresses.

```python
from langgraph.graph import StateGraph, START, END

# Basic async streaming
async for chunk in graph.astream(
    inputs={"messages": [("user", "What is the weather in SF?")]},
    stream_mode="updates"
):
    print(chunk)
```

**Key Parameters:**
- `inputs`: The initial state/input for the graph
- `config`: Optional RunnableConfig containing thread_id, tracing info
- `stream_mode`: Determines what gets streamed (see modes below)
- `interrupt_before`: Nodes to interrupt before execution
- `interrupt_after`: Nodes to interrupt after execution

### 1.2 Stream Modes

LangGraph supports multiple streaming modes, each serving different use cases:

| Mode | Description | Use Case |
|------|-------------|----------|
| `values` | Streams full state after each step | Debugging, complete state tracking |
| `updates` | Streams state changes after each step | Efficient change tracking, bandwidth optimization |
| `messages` | Streams LLM tokens as 2-tuples (token, metadata) | Chat UIs, token-by-token display |
| `custom` | Streams custom user-defined data from nodes | Progress tracking, custom events |
| `debug` | Streams maximum information | Development, troubleshooting |

#### Values Mode

```python
async for state_snapshot in graph.astream(inputs, stream_mode="values"):
    # state_snapshot contains complete state at each step
    print(f"Messages: {state_snapshot['messages']}")
```

**When to use:**
- Need complete state history
- Building debuggers
- State inspection tools
- When state size is manageable

#### Updates Mode

```python
async for update in graph.astream(inputs, stream_mode="updates"):
    # update is a dict: {node_name: {state_updates}}
    for node_name, changes in update.items():
        print(f"{node_name}: {changes}")
```

**When to use:**
- Want efficient bandwidth usage
- Only care about changes
- Building progress displays
- State is large

#### Messages Mode

```python
async for token, metadata in graph.astream(inputs, stream_mode="messages"):
    # token is the LLM token/message chunk
    # metadata contains info like which node generated it
    print(token.content, end="", flush=True)
```

**When to use:**
- Building chat interfaces
- Token-by-token streaming
- Real-time response generation
- ChatGPT-like experiences

#### Custom Mode

```python
async for custom_data in graph.astream(inputs, stream_mode="custom"):
    # custom_data is whatever your nodes emit via StreamWriter
    print(f"Progress: {custom_data['percentage']}%")
```

**When to use:**
- Custom progress tracking
- Long-running operations
- Need to emit domain-specific events
- Tool progress updates

#### Combining Multiple Modes

You can combine multiple modes for comprehensive streaming:

```python
async for mode, data in graph.astream(
    inputs,
    stream_mode=["updates", "custom"]
):
    if mode == "updates":
        print(f"State update: {data}")
    elif mode == "custom":
        print(f"Custom event: {data}")
```

### 1.3 astream_events() Method

The `astream_events()` API provides even more detailed event information, covering the entire lifecycle of a graph run from start to finish. This is particularly useful for observability and debugging.

```python
events = app.astream_events(
    input={"messages": [HumanMessage(content="Hi, How are you?")]},
    version="v2"
)

async for event in events:
    if event["event"] == "on_chat_model_stream":
        # Extract token from streaming LLM
        token = event["data"]["chunk"].content
        print(token, end="", flush=True)
```

**Event Structure:**
```python
{
    "event": "on_chat_model_stream",  # Event type
    "data": {
        "chunk": AIMessageChunk(content="Hello"),  # Token/message chunk
        # ... additional data
    },
    "metadata": {
        "langgraph_node": "agent",  # Which node emitted this
        "run_id": "...",  # Execution run ID
        # ... additional metadata
    }
}
```

**Common Event Types:**

| Event Type | Description | When to Use |
|------------|-------------|-------------|
| `on_chain_start` | Node/chain execution starts | Debugging execution flow |
| `on_chain_end` | Node/chain execution completes | State inspection after nodes |
| `on_chain_stream` | Streaming output from chains | Intermediate results |
| `on_chat_model_start` | LLM invocation starts | Model debugging |
| `on_chat_model_stream` | LLM token generation | Token streaming |
| `on_chat_model_end` | LLM invocation completes | Result inspection |
| `on_tool_start` | Tool invocation starts | Tool debugging |
| `on_tool_end` | Tool invocation completes | Tool result inspection |

**Example: Filtering for Specific Events**

```python
async for event in app.astream_events(inputs, version="v2"):
    event_type = event["event"]

    # Only stream LLM tokens from specific node
    if event_type == "on_chat_model_stream":
        node = event["metadata"].get("langgraph_node", "")
        if node == "my_agent":
            token = event["data"]["chunk"].content
            yield token

    # Track tool calls
    elif event_type == "on_tool_start":
        tool_name = event["data"].get("input", {}).get("name")
        print(f"[Calling tool: {tool_name}]")
```

### 1.4 Differences: astream() vs astream_events()

| Feature | astream() | astream_events() |
|---------|-----------|------------------|
| Granularity | Node-level outputs | Token/tool-level events |
| Use Case | User-facing streaming | Debugging/observability |
| Performance | Lower overhead | Higher overhead |
| Information | Filtered state | Raw execution details |
| Best For | Production UIs | Development tools |

**When to use which:**
- Use `astream()` for production applications and user-facing features
- Use `astream_events()` for debugging, monitoring, and development tools

---

## 2. Implementing Async Streaming Nodes

### 2.1 StreamWriter Basics

The `StreamWriter` is the primary mechanism for sending custom data from within nodes during execution. It allows nodes to emit arbitrary data that will be streamed to the caller when using `stream_mode="custom"`.

```python
from typing import TypedDict
from langgraph.types import StreamWriter

class State(TypedDict):
    topic: str
    joke: str

async def generate_joke(state: State, writer: StreamWriter):
    """Async node that streams custom data during execution"""

    # Stream progress update
    writer({
        "type": "progress",
        "message": f"Starting joke generation for: {state['topic']}"
    })

    # Do some work...
    joke = f"Why did the {state['topic']} cross the road? To get to the other side!"

    # Stream another update
    writer({
        "type": "progress",
        "message": "Joke generated successfully!"
    })

    # Return final state update
    return {"joke": joke}
```

**Key points:**
- Add `writer: StreamWriter` parameter to your async node function
- LangGraph automatically injects the StreamWriter
- Use `writer(data)` to emit custom data
- Data must be JSON-serializable
- Works with both nodes and tools

### 2.2 Using get_stream_writer()

For more advanced scenarios, you can use `get_stream_writer()` to access the stream writer from within a node:

```python
from langgraph.config import get_stream_writer

def call_arbitrary_model(state):
    """Example node that calls an arbitrary model and streams output"""

    # Get the stream writer
    writer = get_stream_writer()

    # Send initial status
    writer({"status": "Initializing model..."})

    # Stream chunks from a custom streaming client
    for chunk in your_custom_streaming_client(state["topic"]):
        # Stream each chunk
        writer({"token": chunk})

    # Send completion status
    writer({"status": "Complete"})

    return {"result": "done"}
```

### 2.3 Python < 3.11 Compatibility

**Critical Limitation:** In async code running on Python < 3.11, `get_stream_writer()` will not work. Instead, you must add a `writer` parameter to your node or tool and pass it manually.

#### Python 3.11+ (Preferred)

```python
from langgraph.config import get_stream_writer

async def my_node(state):
    writer = get_stream_writer()  # Works in Python 3.11+
    writer({"status": "Working..."})
    return state
```

#### Python < 3.11 (Required Pattern)

```python
from langgraph.types import StreamWriter

async def my_node(state: State, writer: StreamWriter):
    # Must add writer parameter explicitly
    writer({"status": "Working..."})
    return state
```

### 2.4 Streaming from Tools

Tools can also stream custom data:

```python
from langchain_core.tools import tool
from langgraph.config import get_stream_writer

@tool
async def long_running_task(task_id: str) -> str:
    """Tool that streams progress updates"""
    writer = get_stream_writer()

    # Stream initial status
    writer({
        "task_id": task_id,
        "status": "started",
        "progress": 0
    })

    # Simulate work with progress updates
    for i in range(10):
        await asyncio.sleep(1)
        writer({
            "task_id": task_id,
            "status": "processing",
            "progress": (i + 1) * 10
        })

    # Stream completion
    writer({
        "task_id": task_id,
        "status": "completed",
        "progress": 100
    })

    return f"Task {task_id} completed successfully"
```

### 2.5 Streaming LLM Outputs from Nodes

When using LLMs within nodes, you can stream their outputs:

```python
async def call_model(state, config):
    """Node that streams LLM tokens"""
    topic = state["topic"]

    # Initialize model with streaming enabled
    model = init_chat_model(model="gpt-4o-mini", streaming=True)

    # Stream tokens
    response = ""
    async for chunk in model.astream(
        f"Tell me a joke about {topic}",
        config=config  # Pass config for proper context propagation
    ):
        token = chunk.content
        response += token

        # Optionally stream via writer
        writer = get_stream_writer()
        writer({"token": token})

    return {"joke": response}
```

### 2.6 Async Node Patterns

#### Pattern 1: Progress Updates

```python
async def process_data_node(state: State, writer: StreamWriter):
    total_items = len(state["items"])

    for i, item in enumerate(state["items"]):
        # Process item
        result = await process_item(item)

        # Stream progress
        writer({
            "type": "progress",
            "current": i + 1,
            "total": total_items,
            "percentage": ((i + 1) / total_items) * 100
        })

    return {"results": results}
```

#### Pattern 2: Streaming Results

```python
async def search_node(state: State, writer: StreamWriter):
    query = state["query"]

    # Stream each search result as it arrives
    async for result in search_engine.stream_search(query):
        writer({
            "type": "search_result",
            "title": result["title"],
            "url": result["url"]
        })

    return {"search_complete": True}
```

#### Pattern 3: Multi-Stage Processing

```python
async def multi_stage_node(state: State, writer: StreamWriter):
    # Stage 1: Validation
    writer({"stage": "validation", "status": "starting"})
    is_valid = await validate_data(state["data"])
    writer({"stage": "validation", "status": "complete", "valid": is_valid})

    if not is_valid:
        return {"error": "Invalid data"}

    # Stage 2: Processing
    writer({"stage": "processing", "status": "starting"})
    result = await process_data(state["data"])
    writer({"stage": "processing", "status": "complete"})

    # Stage 3: Formatting
    writer({"stage": "formatting", "status": "starting"})
    formatted = format_result(result)
    writer({"stage": "formatting", "status": "complete"})

    return {"result": formatted}
```

---

## 3. Streaming Partial Outputs from Agents

### 3.1 Token-by-Token Streaming

The most common partial output pattern is streaming LLM tokens as they're generated:

```python
from langchain.agents import create_react_agent
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

# Create agent
agent = create_react_agent(
    model="gpt-4o-mini",
    tools=[get_weather]
)

# Stream tokens
async for token, metadata in agent.astream(
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
    stream_mode="messages"
):
    # metadata contains info about which node generated the token
    node_name = metadata.get("langgraph_node", "")

    # Filter for specific nodes if needed
    if node_name == "agent":
        if hasattr(token, "content"):
            print(token.content, end="", flush=True)
```

### 3.2 Streaming Agent Steps

For debugging and observability, stream each agent step:

```python
async for update in agent.astream(
    {"messages": [("user", "What is the weather in SF?")]},
    stream_mode="updates"
):
    # update shows what changed after each step
    for node_name, changes in update.items():
        print(f"\n[{node_name}]")
        print(f"Changes: {changes}")
```

**Output structure:**
```python
{
    "agent": {
        "messages": [AIMessage(content="...", tool_calls=[...])]
    },
    "tools": {
        "messages": [ToolMessage(content="It's sunny!")]
    }
}
```

### 3.3 Streaming Tool Calls

Stream both partial tool call JSON and completed results:

```python
async for event in agent.astream_events(
    {"messages": [("user", "What is the weather in SF?")]},
    version="v2"
):
    event_type = event["event"]

    # Partial tool calls (as JSON is being generated)
    if event_type == "on_chat_model_stream":
        chunk = event["data"]["chunk"]
        if chunk.tool_call_chunks:
            for tc in chunk.tool_call_chunks:
                print(f"Tool call chunk: {tc['args']}", end="")

    # Completed tool calls
    elif event_type == "on_tool_start":
        print(f"\n[Calling tool: {event['name']}]")

    elif event_type == "on_tool_end":
        print(f"[Tool result: {event['data']['output']}]")
```

### 3.4 Streaming with Structured Output

When using structured output (e.g., JSON), you can stream partial JSON:

```python
async for chunk in agent.astream(
    {"messages": [{"role": "user", "content": "Extract data from: ..."}]},
    stream_mode="messages"
):
    if hasattr(chunk, 'content') and chunk.content:
        # Stream partial JSON
        try:
            # Try to parse as JSON (may fail for partial chunks)
            data = json.loads(chunk.content)
            print(f"Valid JSON: {data}")
        except json.JSONDecodeError:
            # Partial JSON - just display as-is
            print(chunk.content, end="", flush=True)
```

### 3.5 Filtering Stream by Node

Filter streaming output by specific nodes:

```python
async def stream_from_supervisor_only(supervisor, state, config):
    """Stream only tokens from the supervisor node"""
    async for message, meta in supervisor.astream(
        state,
        config=config,
        stream_mode="messages"
    ):
        # Filter for specific node
        if meta.get("langgraph_node") != "supervisor":
            continue

        if isinstance(message, AIMessageChunk):
            token = message.content or ""
            # Yield only the delta token
            yield token
        elif isinstance(message, AIMessage):
            # Handle final full message
            pass
```

### 3.6 Combining Streaming Modes

Stream both tokens and updates simultaneously:

```python
async for mode, data in agent.astream(
    inputs,
    stream_mode=["messages", "updates"]
):
    if mode == "messages":
        # Token streaming
        token, metadata = data
        print(token.content, end="", flush=True)

    elif mode == "updates":
        # State updates
        print(f"\n[State update: {data}]")
```

### 3.7 Streaming from Nested Graphs

When using subgraphs, streaming works recursively:

```python
# Create subgraph
subgraph = StateGraph(SubState)
subgraph.add_node("process", process_node)
subgraph = subgraph.compile()

# Create main graph with subgraph as node
main_graph = StateGraph(MainState)
main_graph.add_node("subgraph", subgraph)
main_graph = main_graph.compile()

# Stream from nested graph
async for update in main_graph.astream(inputs, stream_mode="updates"):
    # Updates include nested graph execution
    print(f"Update: {update}")
```

**Note:** There's a known issue where calling `.astream` inside another graph's `.astream_events` may set `stream_mode="value"` regardless of config. See "Known Issues" section.

---

## 4. Managing Async State Across Agent Boundaries

### 4.1 State Management Fundamentals

LangGraph uses a shared state architecture where:

1. **State is shared memory** - All nodes access the same state object
2. **Updates are merged** - Multiple node updates are combined using reducers
3. **Execution happens in super-steps** - Nodes execute in discrete steps
4. **Checkpoints provide persistence** - State can be saved and restored

```python
from typing_extensions import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_info: dict
    current_intent: str
    resolved: bool
```

**Key concept:** Using `Annotated[list, operator.add]` ensures messages are appended rather than replaced.

### 4.2 Subgraph State Patterns

#### Shared State Pattern

The simplest approach: subgraphs share state keys with parent graph.

```python
# Parent graph state
class ParentState(TypedDict):
    messages: Annotated[list, operator.add]
    research_data: list

# Subgraph uses same keys
class SubgraphState(TypedDict):
    messages: Annotated[list, operator.add]  # Same key
    research_data: list  # Same key

# When subgraph executes, updates flow automatically
subgraph = StateGraph(SubgraphState)
subgraph.add_node("research", research_node)
subgraph = subgraph.compile()

# Add to parent as node
parent = StateGraph(ParentState)
parent.add_node("research_agent", subgraph)
parent = parent.compile()
```

**Pros:**
- Automatic communication
- Simple to implement
- No transformation needed

**Cons:**
- No privacy between agents
- Subgraph can modify all parent state
- Potential for conflicts

#### Isolated State Pattern

Subgraphs have independent state with explicit transformation:

```python
# Parent state
class ParentState(TypedDict):
    shared_context: dict
    final_results: list

# Subgraph has different state
class SubgraphState(TypedDict):
    private_data: dict
    internal_steps: list

# Transform state at boundaries
def parent_to_subgraph(state: ParentState) -> SubgraphState:
    return {
        "private_data": state["shared_context"].copy(),
        "internal_steps": []
    }

def subgraph_to_parent(state: SubgraphState, parent: ParentState) -> ParentState:
    return {
        "final_results": state["internal_steps"],
        **parent  # Preserve other fields
    }

# Use in graph
subgraph = StateGraph(SubgraphState)
# ... add nodes ...
subgraph = subgraph.compile()

# Add to parent with state transformation
parent = StateGraph(ParentState)
parent.add_node("subgraph",
    transform_input=parent_to_subgraph,
    transform_output=subgraph_to_parent
)
```

**Pros:**
- Clear boundaries
- Privacy maintained
- Explicit data flow

**Cons:**
- More boilerplate
- Manual transformation
- Potential for sync issues

### 4.3 Concurrent State Updates

When multiple nodes execute in parallel, LangGraph merges their updates:

```python
from langgraph.graph import StateGraph

# Define graph with parallel execution
graph = StateGraph(AgentState)
graph.add_node("node_a", node_a_func)
graph.add_node("node_b", node_b_func)
graph.add_node("node_c", node_c_func)

# Execute A, B, C in parallel
graph.add_edge(START, "node_a")
graph.add_edge(START, "node_b")
graph.add_edge(START, "node_c")
graph.add_edge("node_a", "merge")
graph.add_edge("node_b", "merge")
graph.add_edge("node_c", "merge")

# Merge node processes all updates
async def merge_node(state):
    # All updates from A, B, C are merged here
    # Using reducers to combine conflicts
    return state

graph = graph.compile()
```

**Conflict Resolution:**

```python
from typing import Annotated
from typing_extensions import TypedDict

def merge_left(existing, new):
    """Keep existing value (left wins)"""
    return existing

def merge_right(existing, new):
    """Use new value (right wins)"""
    return new

def merge_append(existing, new):
    """Append both values"""
    return existing + new

class State(TypedDict):
    field1: Annotated[str, merge_left]
    field2: Annotated[str, merge_right]
    field3: Annotated[list, merge_append]
```

### 4.4 State Persistence with Checkpointers

Async state management requires async checkpointer:

```python
from langgraph.checkpoint.aiosqlite import AsyncSqliteSaver

# Create async checkpointer
memory = AsyncSqliteSaver.from_conn_string(":memory:")

# Create agent with checkpointing
agent = create_react_agent(
    model,
    tools,
    checkpointer=memory
)

# Use thread_id for conversation persistence
config = {"configurable": {"thread_id": "user-123"}}

# Stream with persistence
async for event in agent.astream_events(
    {"messages": [HumanMessage(content="Hello")]},
    config=config,
    version="v2"
):
    # Each checkpoint is saved automatically
    if event["event"] == "on_chain_end":
        # State checkpointed here
        pass
```

**Checkpointing Modes:**

```python
# Async durability (default) - non-blocking
app = graph.compile(checkpointer=memory)

# Sync mode - blocks until checkpoint written
app = graph.compile(checkpointer=memory, checkpointer_mode="sync")

# Exit mode - only checkpoint at completion
app = graph.compile(checkpointer=memory, checkpointer_mode="exit")
```

### 4.5 Handoff Between Agents

When Agent A hands off to Agent B, structured context transfer is crucial:

```python
def agent_a_handoff(state):
    """Agent A prepares handoff to Agent B"""
    return {
        "handoff_source": "agent_a",
        "handoff_context": {
            "previous_results": state["results"],
            "conversation_summary": summarize_conversation(state["messages"]),
            "pending_tasks": state["tasks"]
        },
        "current_agent": "agent_b"
    }

def agent_b_receive(state):
    """Agent B receives handoff"""
    context = state.get("handoff_context", {})

    # Process based on handoff context
    if context.get("pending_tasks"):
        # Continue from Agent A's work
        return continue_tasks(context["pending_tasks"])
    else:
        # Start fresh
        return start_new_task()
```

### 4.6 State Streaming Across Boundaries

Stream state changes as they propagate through subgraphs:

```python
async for update in main_graph.astream(
    initial_state,
    stream_mode="updates",
    subgraphs=True  # Enable subgraph streaming
):
    # update includes nested graph updates
    for node_name, changes in update.items():
        if node_name.startswith("subgraph:"):
            # Extract subgraph name
            subgraph_name = node_name.split(":")[1]
            print(f"[{subgraph_name}] {changes}")
        else:
            print(f"[{node_name}] {changes}")
```

---

## 5. Error Handling in Async Streaming Workflows

### 5.1 Error Handling Strategies

LangGraph provides multiple strategies for handling errors in async streaming workflows:

#### Strategy 1: Error State Tracking

```python
class ErrorState(TypedDict):
    errors: Annotated[list[dict], operator.add]
    error_count: int
    last_error: dict | None

async def error_handling_node(state):
    """Node that captures and tracks errors"""
    try:
        # Do work that might fail
        result = await risky_operation()
        return {"result": result}
    except Exception as e:
        # Add error to state
        error = {
            "type": type(e).__name__,
            "message": str(e),
            "timestamp": datetime.now().isoformat(),
            "node": "error_handling_node"
        }
        return {
            "errors": [error],
            "error_count": state.get("error_count", 0) + 1,
            "last_error": error
        }
```

#### Strategy 2: Conditional Error Routing

```python
def should_retry(state) -> str:
    """Route based on error type"""
    last_error = state.get("last_error")

    if not last_error:
        return "continue"

    error_type = last_error.get("type")

    # Transient errors - retry
    if error_type in ["TimeoutError", "ConnectionError"]:
        return "retry"

    # Recoverable errors - let LLM handle
    elif error_type in ["ValidationError", "ParseError"]:
        return "llm_recovery"

    # Fatal errors - stop
    else:
        return "error"

graph.add_conditional_edges(
    "process_node",
    should_retry,
    {
        "continue": "next_node",
        "retry": "process_node",  # Loop back
        "llm_recovery": "error_recovery_node",
        "error": END
    }
)
```

#### Strategy 3: LLM-Guided Error Recovery

```python
async def error_recovery_node(state):
    """Let LLM attempt to recover from error"""
    last_error = state["last_error"]

    # Provide error context to LLM
    prompt = f"""
    The following error occurred:
    Type: {last_error['type']}
    Message: {last_error['message']}

    Original task: {state.get('task')}

    Please analyze this error and either:
    1. Suggest a fix
    2. Propose an alternative approach
    3. Explain why this task cannot be completed
    """

    response = await llm.ainvoke(prompt)

    return {
        "error_recovery_suggestion": response.content,
        "needs_human_input": "unclear" in response.content.lower()
    }
```

### 5.2 Error Handling in Streaming Contexts

Handle errors while maintaining stream:

```python
async def safe_stream(graph, inputs, config):
    """Stream with error handling"""
    try:
        async for chunk in graph.astream(inputs, config=config, stream_mode="messages"):
            yield {"status": "success", "data": chunk}

    except StopAsyncIteration:
        # Normal end of stream
        yield {"status": "complete"}

    except Exception as e:
        # Error during streaming
        yield {
            "status": "error",
            "error": {
                "type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        }
```

### 5.3 Streaming Errors to Client

Send error events via StreamWriter:

```python
async def node_with_error_streaming(state, writer):
    try:
        # Normal processing
        result = await process(state["data"])

        # Stream success
        writer({
            "type": "status",
            "status": "success",
            "result": result
        })

    except ValidationError as e:
        # Stream validation error
        writer({
            "type": "error",
            "error_type": "validation",
            "message": str(e),
            "recoverable": True
        })

    except Exception as e:
        # Stream unexpected error
        writer({
            "type": "error",
            "error_type": "unexpected",
            "message": str(e),
            "recoverable": False
        })
        raise  # Re-raise for graph-level handling
```

### 5.4 Retry Policies

Implement automatic retry with exponential backoff:

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((TimeoutError, ConnectionError))
)
async def robust_api_call(state):
    """API call with automatic retry"""
    response = await external_api.call(state["query"])
    return {"api_result": response}
```

### 5.5 Error Categories and Responses

| Error Type | Strategy | Example |
|------------|----------|---------|
| **Transient** | Automatic retry | Network timeout, rate limit |
| **LLM-Recoverable** | Loop back with context | Tool failure, parse error |
| **User-Fixable** | Pause with interrupt | Missing data, unclear request |
| **Unexpected** | Bubble up for debugging | Unknown errors, bugs |

#### Transient Error Example

```python
async def handle_transient_error(state):
    """Network timeout - retry automatically"""
    retries = state.get("retries", 0)
    max_retries = 3

    if retries < max_retries:
        return {
            "retries": retries + 1,
            "next_action": "retry"
        }
    else:
        return {
            "error": "Max retries exceeded",
            "next_action": "fail"
        }
```

#### User-Fixable Error Example

```python
async def handle_user_error(state):
    """Missing data - pause for user input"""
    missing_fields = validate_required_fields(state)

    if missing_fields:
        # Interrupt execution for user input
        graph.interrupt(
            f"Please provide: {', '.join(missing_fields)}"
        )

    return state
```

### 5.6 Error Analytics

Track errors for analysis:

```python
async def analytics_node(state):
    """Collect error analytics"""
    errors = state.get("errors", [])

    if not errors:
        return {"analytics": None}

    # Compute analytics
    analytics = {
        "total_errors": len(errors),
        "by_type": count_by_type(errors),
        "by_node": count_by_node(errors),
        "recovery_rate": calculate_recovery_rate(errors),
        "most_common": most_common_error(errors)
    }

    return {"analytics": analytics}

def count_by_type(errors):
    counts = {}
    for error in errors:
        error_type = error["type"]
        counts[error_type] = counts.get(error_type, 0) + 1
    return counts
```

### 5.7 Circuit Breaker Pattern

Prevent cascading failures:

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    async def call(self, func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            raise

# Usage in node
circuit_breaker = CircuitBreaker()

async def protected_node(state):
    return await circuit_breaker.call(
        risky_operation,
        state["data"]
    )
```

---

## Best Practices and Patterns

### 1. Start Simple, Add Complexity

1. Start with `values` or `updates` to see state changes
2. Add `messages` when building chat interfaces
3. Implement `custom` events for specialized needs
4. Use `debug` during development only

### 2. Choose Right Stream Mode

| Use Case | Recommended Mode |
|----------|-----------------|
| Debugging state | `values` |
| Production APIs | `updates` |
| Chat UIs | `messages` |
| Progress bars | `custom` |
| Development | `debug` |

### 3. Handle Python Version Differences

```python
import sys

if sys.version_info >= (3, 11):
    # Use get_stream_writer()
    from langgraph.config import get_stream_writer
    writer = get_stream_writer()
else:
    # Add writer parameter to function
    from langgraph.types import StreamWriter
    # Writer injected by LangGraph
```

### 4. Always Pass Config in Async

```python
# WRONG - may have streaming issues
async def bad_node(state):
    return await model.ainvoke(state["query"])

# CORRECT - proper context propagation
async def good_node(state, config):
    return await model.ainvoke(state["query"], config=config)
```

### 5. Filter Events Appropriately

```python
# Don't process every event - filter what you need
async for event in app.astream_events(inputs, version="v2"):
    # Filter by event type
    if event["event"] != "on_chat_model_stream":
        continue

    # Filter by node
    if event["metadata"].get("langgraph_node") != "my_agent":
        continue

    # Process relevant events only
    process_token(event["data"]["chunk"])
```

### 6. Use Reducers for Conflict Resolution

```python
from typing import Annotated

class State(TypedDict):
    # Append instead of overwrite
    messages: Annotated[list, operator.add]

    # Custom merge logic
    results: Annotated[list, merge_left_right]

    # Single writer (last write wins)
    status: str
```

### 7. Implement Timeouts

```python
import asyncio

async def node_with_timeout(state):
    try:
        result = await asyncio.wait_for(
            long_running_operation(),
            timeout=30.0  # 30 second timeout
        )
        return {"result": result}
    except asyncio.TimeoutError:
        return {"error": "Operation timed out"}
```

### 8. Use Checkpointers for Long-Running Workflows

```python
from langgraph.checkpoint.aiosqlite import AsyncSqliteSaver

memory = AsyncSqliteSaver.from_conn_string("checkpoints.db")
app = graph.compile(checkpointer=memory)

# Resume from checkpoint
config = {"configurable": {"thread_id": "workflow-123"}}
async for chunk in app.astream(inputs, config=config):
    # Can resume if interrupted
    pass
```

### 9. Separate Concerns

- **Nodes**: Business logic
- **Edges**: Routing logic
- **State**: Data storage
- **Checkpointers**: Persistence
- **Stream Writers**: Real-time updates

### 10. Test Streaming Locally First

```python
# Test streaming patterns locally before deploying
async def test_streaming():
    chunks = []
    async for chunk in graph.astream(test_input, stream_mode="messages"):
        chunks.append(chunk)
        print(chunk.content, end="", flush=True)

    assert len(chunks) > 0, "No chunks streamed"
    assert all(c.content for c in chunks), "Empty chunks"
```

---

## Known Issues and Limitations

### Issue 1: Async Tools Don't Support Custom Events (GitHub #6447)

**Problem:** When running async tools in custom stream mode, messages emitted via `get_stream_writer()` are not captured. This only affects async tools; sync tools work correctly.

**Workaround:**
```python
# Use sync wrapper for now
@tool
def sync_tool_wrapper(param: str) -> str:
    # Wrap async logic in sync tool
    return asyncio.run(async_implementation(param))
```

**Status:** Open issue as of 2025-11-14

### Issue 2: astream Inside astream_events Sets Wrong Mode (GitHub #2351)

**Problem:** Calling `.astream()` inside another graph's `.astream_events()` forces `stream_mode="value"` regardless of config.

**Workaround:**
```python
# Avoid nesting astream inside astream_events
# Use astream_events at top level only
```

**Status:** Closed issue, but behavior may persist in some versions

### Issue 3: StreamWriter Doesn't Stream in Async Nodes (GitHub #4610)

**Problem:** StreamWriter works in sync nodes but only renders final response in async nodes (Python 3.11).

**Workaround:**
```python
# Use writer parameter instead of get_stream_writer()
async def my_node(state: State, writer: StreamWriter):
    writer({"status": "working"})
    return state
```

**Status:** Open issue as of 2025-02-06

### Issue 4: Event Stream Stalls with Long-Running Tools

**Problem:** When using `get_stream_writer()` with async tools that run 1-10 minutes, the event stream may stall even though backend completes successfully.

**Workaround:**
```python
# Emit periodic heartbeat events
async def long_running_tool(state):
    writer = get_stream_writer()

    # Send initial status
    writer({"status": "started"})

    # Emit heartbeat every 10 seconds
    last_heartbeat = time.time()

    while doing_work:
        # Do work...

        # Check if heartbeat needed
        if time.time() - last_heartbeat > 10:
            writer({"heartbeat": True})
            last_heartbeat = time.time()

    writer({"status": "completed"})
```

**Status:** Community discussion ongoing

### Issue 5: StopAsyncIteration in langgraph-supervisor

**Problem:** Streaming from `langgraph-supervisor` with `stream_mode="messages"` results in `RuntimeError: async generator raised StopAsyncIteration`.

**Workaround:**
```python
output = ""
try:
    async for chunk in supervisor.astream(
        state, config=config, stream_mode="messages"
    ):
        msg, metadata = chunk
        if isinstance(msg, AIMessageChunk):
            output += msg.content
            yield output
except StopAsyncIteration:
    pass  # Expected end of stream
```

**Status:** Community workaround documented

### Limitation: Python < 3.11 Async Support

**Limitation:** `get_stream_writer()` doesn't work in async code on Python < 3.11.

**Workaround:** Always include `writer: StreamWriter` parameter in async node signatures.

**Solution:** Upgrade to Python 3.11+

### Limitation: Structured Output Breaks Streaming

**Limitation:** When using `with_structured_output()`, streaming token-by-token doesn't work - entire output comes at once.

**Workaround:**
```python
# Don't use with_structured_output() for streaming
# Stream raw tokens and parse manually
async for chunk in llm.astream(messages):
    # Parse partial JSON as it arrives
    try:
        data = json.loads(chunk.content)
    except json.JSONDecodeError:
        # Partial data - accumulate
        pass
```

---

## Code Examples

### Example 1: Complete Streaming Agent

```python
from typing import TypedDict, Annotated
from langchain_core.tools import tool
from langchain_core.messages import AnyMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.aiosqlite import AsyncSqliteSaver
import operator

# Define state
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    current_step: str
    progress: int

# Define tool
@tool
async def research_tool(query: str) -> str:
    """Research a topic"""
    await asyncio.sleep(1)  # Simulate work
    return f"Research results for: {query}"

# Define streaming node
from langgraph.types import StreamWriter

async def agent_node(state: AgentState, writer: StreamWriter):
    """Agent node that streams progress"""

    # Stream start
    writer({
        "type": "progress",
        "step": "starting",
        "message": "Beginning research..."
    })

    # Process messages
    last_message = state["messages"][-1]
    query = last_message.content

    # Stream processing
    writer({
        "type": "progress",
        "step": "processing",
        "message": f"Researching: {query}"
    })

    # Simulate LLM call
    await asyncio.sleep(0.5)

    # Stream completion
    writer({
        "type": "progress",
        "step": "complete",
        "message": "Research complete!"
    })

    return {
        "current_step": "complete",
        "progress": 100
    }

# Build graph
graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_edge(START, "agent")
graph.add_edge("agent", END)

# Compile with checkpointer
memory = AsyncSqliteSaver.from_conn_string(":memory:")
app = graph.compile(checkpointer=memory)

# Stream execution
async def main():
    config = {"configurable": {"thread_id": "test-1"}}

    async for mode, data in app.astream(
        {"messages": [("user", "Research AI")]},
        config=config,
        stream_mode=["updates", "custom"]
    ):
        if mode == "updates":
            print(f"[State Update] {data}")
        elif mode == "custom":
            print(f"[Event] {data['message']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 2: Multi-Agent System with Streaming

```python
from typing import Literal

class MultiAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    current_agent: str
    research_results: list[str]
    final_answer: str

def router(state) -> Literal["researcher", "analyst", "end"]:
    """Route to appropriate agent"""
    agent = state.get("current_agent", "researcher")

    if agent == "researcher":
        return "researcher"
    elif agent == "analyst":
        return "analyst"
    else:
        return "end"

async def researcher_agent(state: MultiAgentState, writer: StreamWriter):
    """Research agent that streams progress"""
    writer({"agent": "researcher", "status": "starting"})

    # Do research
    results = await do_research(state["messages"][-1].content)

    writer({"agent": "researcher", "status": "complete", "results": results})

    return {
        "research_results": results,
        "current_agent": "analyst"
    }

async def analyst_agent(state: MultiAgentState, writer: StreamWriter):
    """Analyst agent that streams progress"""
    writer({"agent": "analyst", "status": "starting"})

    # Analyze research
    analysis = await analyze_results(state["research_results"])

    writer({"agent": "analyst", "status": "complete"})

    return {
        "final_answer": analysis,
        "current_agent": "end"
    }

# Build multi-agent graph
graph = StateGraph(MultiAgentState)
graph.add_node("researcher", researcher_agent)
graph.add_node("analyst", analyst_agent)
graph.add_conditional_edges(START, router)
graph.add_conditional_edges("researcher", router)
graph.add_conditional_edges("analyst", router)
graph.add_edge("end", END)

app = graph.compile()

# Stream multi-agent execution
async def stream_multi_agent():
    async for update in app.astream(
        {"messages": [("user", "What is AI?")]},
        stream_mode="updates"
    ):
        for agent, changes in update.items():
            print(f"[{agent}] {changes}")
```

### Example 3: Error Recovery with Streaming

```python
class ErrorState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    errors: list[dict]
    retry_count: int
    status: str

async def risky_operation_node(state: ErrorState, writer: StreamWriter):
    """Node with error handling and streaming"""

    retry_count = state.get("retry_count", 0)
    max_retries = 3

    try:
        writer({"status": f"Attempt {retry_count + 1}/{max_retries}"})

        # Do risky operation
        result = await risky_operation()

        writer({"status": "success", "result": result})

        return {
            "status": "success",
            "retry_count": 0  # Reset on success
        }

    except TimeoutError as e:
        error = {
            "type": "TimeoutError",
            "message": str(e),
            "retry_count": retry_count + 1
        }

        writer({"status": "error", "error": error})

        if retry_count < max_retries:
            # Retry
            return {
                "errors": [error],
                "retry_count": retry_count + 1,
                "status": "retrying"
            }
        else:
            # Give up
            return {
                "errors": [error],
                "status": "failed"
            }

    except Exception as e:
        # Unexpected error - don't retry
        error = {
            "type": type(e).__name__,
            "message": str(e),
            "unexpected": True
        }

        writer({"status": "error", "error": error})

        return {
            "errors": [error],
            "status": "failed"
        }

def should_retry(state) -> Literal["retry", "fail", "success"]:
    status = state.get("status")

    if status == "retrying":
        return "retry"
    elif status == "failed":
        return "fail"
    else:
        return "success"

# Build graph with error recovery
graph = StateGraph(ErrorState)
graph.add_node("risky_operation", risky_operation_node)
graph.add_conditional_edges(
    "risky_operation",
    should_retry,
    {
        "retry": "risky_operation",
        "fail": END,
        "success": END
    }
)

app = graph.compile()

# Stream with error recovery
async def stream_with_recovery():
    async for mode, data in app.astream(
        {"messages": [("user", "Do something")]},
        stream_mode=["updates", "custom"]
    ):
        if mode == "custom":
            status = data.get("status")
            print(f"Status: {status}")

            if "error" in data:
                print(f"Error: {data['error']['message']}")
```

---

## References

### Official Documentation

1. **LangGraph Streaming Documentation**
   - URL: https://docs.langchain.com/oss/python/langgraph/streaming
   - Covers: Stream modes, custom data, StreamWriter, Python version compatibility

2. **LangGraph Graph API**
   - URL: https://docs.langchain.com/oss/python/langgraph/graph-api
   - Covers: State management, nodes, edges, super-steps

3. **LangSmith Streaming API**
   - URL: https://docs.langchain.com/langsmith/streaming
   - Covers: Streaming modes, SDK usage, deployment streaming

### Community Resources

4. **Medium: Built with LangGraph! #16: Streaming**
   - Author: Okan Yenigün
   - URL: https://medium.com/codetodeploy/built-with-langgraph-16-streaming-e572afd298e7
   - Covers: astream_events(), token streaming, practical examples

5. **Stackademic: LangGraph Streaming 101**
   - Author: Sreeni
   - URL: https://dev.to/sreeni5018/langgraph-streaming-101-5-modes-to-build-responsive-ai-applications-4p3f
   - Covers: All 5 stream modes with examples

6. **LinkedIn: LangChain Streaming + Structured Output**
   - Author: Yash Sarode
   - URL: https://www.linkedin.com/pulse/langchain-streaming-structured-output-yash-sarode-2b6cf
   - Covers: Token streaming, structured output, agent streaming

### GitHub Issues

7. **Issue #6447: Async tools don't support custom events**
   - URL: https://github.com/langchain-ai/langgraph/issues/6447
   - Status: Open
   - Affects: Async tools with get_stream_writer()

8. **Issue #4610: StreamWriter doesn't stream in async nodes**
   - URL: https://github.com/langchain-ai/langgraph/issues/4610
   - Status: Open
   - Affects: Python 3.11 async nodes

9. **Issue #2351: astream inside astream_events bug**
   - URL: https://github.com/langchain-ai/langgraph/issues/2351
   - Status: Closed
   - Affects: Nested streaming

### Forum Discussions

10. **Streaming from langgraph-supervisor**
    - URL: https://forum.langchain.com/t/streaming-from-langgraph-supervisor/1789
    - Covers: StopAsyncIteration workaround, token filtering

11. **How to stream an LLM from a tool**
    - URL: https://forum.langchain.com/t/how-to-stream-an-llm-from-a-tool/1402
    - Covers: Subgraph patterns, LLM-in-tool streaming

12. **Best practices for catching exceptions**
    - URL: https://forum.langchain.com/t/best-practices-for-catching-and-handling-exceptions-in-langgraph/1244
    - Covers: Error handling patterns, state management

### Video Tutorials

13. **LangGraph Crash Course #40 - Streaming**
    - Platform: YouTube
    - URL: https://www.youtube.com/watch?v=VDsh62uIaf8
    - Covers: Deep dive into streaming, all modes, debug mode

14. **LangGraph Streaming: Custom Mode & LLM Message Streaming**
    - Platform: YouTube
    - Author: Mohamed Naji Aboo
    - URL: https://www.youtube.com/watch?v=YqBYU2_IUlA
    - Covers: Custom mode, message streaming, combining modes

### Research Articles

15. **State Management in Multi-Agent AI Systems**
    - Author: Ranjan Kumar
    - URL: https://ranjankumar.in/building-agents-that-remember-state-management-in-multi-agent-ai-systems
    - Covers: Memory architecture, handoff protocols, future trends

16. **Scaling LangGraph Agents: Parallelization**
    - Platform: AI Practitioner
    - URL: https://aipractitioner.substack.com/p/scaling-langgraph-agents-parallelization
    - Covers: Parallel execution, subgraphs, state isolation

17. **Advanced Error Handling Strategies in LangGraph**
    - Platform: Sparkco.ai
    - URL: https://sparkco.ai/blog/advanced-error-handling-strategies-in-langgraph-applications
    - Covers: Multi-level error management, typed errors, recovery strategies

### Additional Resources

18. **LangChain OSS Python Streaming Overview**
    - URL: https://docs.langchain.com/oss/python/langchain/streaming/overview
    - Covers: LLM tokens, tool calls, common patterns

19. **Thinking in LangGraph**
    - URL: https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph
    - Covers: Design philosophy, error handling, state management

20. **LangGraph Tutorial: Error Handling Patterns**
    - Platform: AI Product Engineer
    - URL: https://aiproduct.engineer/tutorials/langgraph-tutorial-error-handling-patterns-unit-23-exercise-6
    - Covers: Comprehensive error handling implementation

---

## Appendix: Quick Reference

### Stream Mode Decision Tree

```
Need to see complete state?
├─ Yes → stream_mode="values"
└─ No
    ├─ Need token-by-token?
    │  ├─ Yes → stream_mode="messages"
    │  └─ No
    │      ├─ Only care about changes?
    │      │  ├─ Yes → stream_mode="updates"
    │      └─ Need custom progress/events?
    │          ├─ Yes → stream_mode="custom"
    │          └─ No → stream_mode="debug" (development only)
```

### Error Handling Decision Tree

```
Error occurred in async node
├─ Transient? (network, timeout)
│  └─ Yes → Retry with exponential backoff
├─ LLM recoverable? (tool failure, parse error)
│  └─ Yes → Store error in state, loop back for LLM recovery
├─ User fixable? (missing data, unclear request)
│  └─ Yes → Pause with interrupt(), wait for human input
└─ Unexpected?
   └─ Yes → Log error, bubble up for debugging
```

### Python Version Compatibility

| Feature | Python < 3.11 | Python 3.11+ |
|---------|--------------|--------------|
| `get_stream_writer()` | ❌ Doesn't work | ✅ Works |
| `writer` parameter | ✅ Required | ✅ Works |
| Async streaming | ✅ Works (with workaround) | ✅ Works |
| All stream modes | ✅ Supported | ✅ Supported |

### Common Event Types (astream_events)

| Event Type | Description | Stream Component |
|------------|-------------|------------------|
| `on_chain_start` | Node starts execution | - |
| `on_chain_end` | Node completes | State snapshot |
| `on_chain_stream` | Node streaming output | Partial results |
| `on_chat_model_start` | LLM call starts | - |
| `on_chat_model_stream` | LLM token generation | Token chunks |
| `on_chat_model_end` | LLM call completes | Final message |
| `on_tool_start` | Tool call starts | Tool name, args |
| `on_tool_end` | Tool call completes | Tool result |

---

**Document End**

For updates and corrections, refer to the official LangGraph documentation at https://docs.langchain.com/langgraph

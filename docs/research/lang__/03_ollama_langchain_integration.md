# Ollama Integration with LangChain/LangGraph Research

**Date**: 2025-02-04
**Focus**: Local LLM integration with LangChain/LangGraph
**Target**: AGENTX project integration patterns

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [Basic ChatOllama Configuration](#basic-chatollama-configuration)
3. [Async Patterns](#async-patterns)
4. [Streaming Patterns](#streaming-patterns)
5. [Pydantic Serialization Issues](#pydantic-serialization-issues)
6. [LangGraph Integration](#langgraph-integration)
7. [Checkpointing and Persistence](#checkpointing-and-persistence)
8. [Best Practices](#best-practices)

---

## Installation and Setup

### Required Packages

```bash
# Core LangChain Ollama integration
pip install -qU langchain-ollama

# Additional required packages
pip install -qU langchain-core langgraph

# For image/multimodal support
pip install -qU pillow

# Update Ollama to latest version
pip install -U ollama
```

### Ollama Server Setup

```bash
# Start Ollama server
ollama serve

# Pull recommended models
ollama pull llama3.1
ollama pull gemma3:4b
ollama pull gpt-oss:20b  # For tool calling
ollama pull granite3.2:8b  # For reasoning models
ollama pull bakllava  # For multimodal
ollama pull llava:latest  # For vision
```

### Ollama Model Locations

- **macOS**: `~/.ollama/models`
- **Linux/WSL**: `/usr/share/ollama/.ollama/models`

---

## Basic ChatOllama Configuration

### Instantiation

```python
from langchain_ollama import ChatOllama

# Basic instantiation
llm = ChatOllama(
    model="llama3.1",
    temperature=0,
)

# With additional parameters
llm = ChatOllama(
    model="llama3.1",
    temperature=0,
    num_ctx=4096,  # Context window size
    num_predict=512,  # Max tokens to predict
    top_k=40,
    top_p=0.9,
    repeat_penalty=1.1,
)
```

### Basic Invocation

```python
from langchain.messages import HumanMessage, SystemMessage

messages = [
    SystemMessage(content="You are a helpful assistant that translates English to French."),
    HumanMessage(content="I love programming."),
]

ai_msg = llm.invoke(messages)
print(ai_msg.content)
# Output: "J'adore la programmation."
```

### Response Structure

```python
# AIMessage contains:
ai_msg.content  # Text response
ai_msg.response_metadata  # {
    'model': 'llama3.1',
    'created_at': '2025-06-25T18:43:00.483666Z',
    'done': True,
    'done_reason': 'stop',
    'total_duration': 619971208,
    'prompt_eval_count': 35,
    'eval_count': 22,
    'model_name': 'llama3.1'
}
ai_msg.usage_metadata  # {
    'input_tokens': 35,
    'output_tokens': 22,
    'total_tokens': 57
}
```

### Model Features Support

| Feature | Supported |
|---------|-----------|
| Tool calling | YES |
| Structured output | YES |
| Image input (multimodal) | YES |
| Audio input | NO |
| Video input | NO |
| Token-level streaming | YES |
| Native async | YES |
| Token usage | NO |
| Log probabilities | NO |

---

## Async Patterns

### Basic Async Invocation

```python
# Use ainvoke() for async calls
async def main():
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="Hello!"),
    ]
    ai_msg = await llm.ainvoke(messages)
    print(ai_msg.content)

import asyncio
asyncio.run(main())
```

### LangGraph Async Patterns

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class State(TypedDict):
    topic: str
    joke: str

async def call_model(state: State) -> State:
    """Async node that calls Ollama model."""
    # IMPORTANT: Pass config for context propagation
    config = {"configurable": {"thread_id": "my-thread"}}
    joke_response = await llm.ainvoke(
        [{"role": "user", "content": f"Write a joke about {state['topic']}"}],
        config,  # Pass config to model.ainvoke()
    )
    return {"joke": joke_response.content}

# Build graph
graph = (
    StateGraph(State)
    .add_node("call_model", call_model)
    .add_edge(START, "call_model")
    .add_edge("call_model", END)
    .compile()
)

# Run async
async def run_graph():
    async for chunk in graph.astream({"topic": "ice cream"}):
        print(chunk)

asyncio.run(run_graph())
```

### Astream Events (Advanced)

```python
# Stream all events from graph execution
async def stream_events():
    async for event in graph.astream_events(
        {"messages": [input_message]},
        version="v1",
        config={"configurable": {"thread_id": thread_id}}
    ):
        # Filter specific events
        if event["event"] == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            print(chunk.content, end="", flush=True)

asyncio.run(stream_events())
```

**Important Note**: There's a known bug where ChatOllama switches between `on_chat_model_stream` and `on_llm_stream` events on subsequent calls in the same session. Handle both event types:

```python
# Handle both event types
if event["event"] in ["on_chat_model_stream", "on_llm_stream"]:
    # Process chunk
    pass
```

---

## Streaming Patterns

### Basic Token Streaming

```python
# Stream tokens one by one
for token in llm.stream("Tell me a joke about programming"):
    print(token.content, end="", flush=True)
```

### LangGraph Streaming Modes

LangGraph supports multiple streaming modes:

| Mode | Description |
|------|-------------|
| `values` | Stream full graph state after each super-step |
| `updates` | Stream state updates after each step |
| `messages` | Stream LLM tokens as 2-tuples `(message, metadata)` |
| `debug` | Stream maximum information |
| `custom` | Stream custom data from nodes |

### Streaming Messages (Recommended for Chat)

```python
# Set stream_mode="messages" for token-by-token streaming
async for chunk, metadata in graph.astream(
    {"topic": "ice cream"},
    stream_mode="messages",
):
    if chunk.content:
        print(chunk.content, end="|", flush=True)

# Get node name from metadata
current_node = metadata.get("langgraph_node")
if current_node == "supervisor":
    # Only process supervisor tokens
    pass
```

### Streaming with FastAPI

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from asyncio import sleep

app = FastAPI()

@app.post("/chat")
async def chat_endpoint(message: str):
    async def generate():
        async for chunk, metadata in graph.astream(
            {"messages": [HumanMessage(content=message)]},
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessageChunk):
                token = chunk.content or ""
                # Format as Server-Sent Events
                yield f"data: {json.dumps({'token': token})}\n\n"
                await sleep(0.01)  # Prevent overwhelming client

    return StreamingResponse(generate(), media_type="text/event-stream")
```

### Streaming with Structured Output

**Important**: Do NOT use `with_structured_output()` followed by `.bind_tools()` - this is not supported and will cause errors.

```python
# WRONG - not supported
structured_llm = llm.with_structured_output(ResponseModel)
llm_with_tools = structured_llm.bind_tools([tool])  # ERROR

# CORRECT - use bind_tools with response_format
llm_with_tools = llm.bind_tools(
    [tool],
    response_format=ResponseModel,
    strict=True,
)
```

---

## Pydantic Serialization Issues

### Issue 1: Pickle Errors with Thread Locks

**Error**: `TypeError: can't pickle '_thread.lock' objects`

**Cause**: ChromaDB or similar libraries create thread locks in class `__init__`, which can't be pickled during LangGraph checkpointing.

**Solution**: Use `default_factory` for dynamic fields

```python
from datetime import datetime, UTC
from pydantic import BaseModel, Field

# WRONG - creates shared timestamp
class Investment(BaseModel):
    created_at: datetime = datetime.now(UTC)  # Executed at import time

# CORRECT - uses default_factory
class Investment(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
```

### Issue 2: Non-Serializable State Objects

**Error**: `Object of type X is not JSON serializable`

**Cause**: LangGraph's default `JsonPlusSerializer` uses msgpack/JSON, which doesn't support all Python types.

**Solution 1**: Make objects inherit from `Serializable`

```python
from langgraph.checkpoint.serde.base import Serializable

class MyState(Serializable):
    def __init__(self, value: str):
        self.value = value
```

**Solution 2**: Use pickle fallback (not recommended for production)

```python
from langgraph.checkpoint.serde import JsonPlusSerializer

# Use pickle for unsupported types (e.g., Pandas DataFrames)
serializer = JsonPlusSerializer(pickle_fallback=True)
checkpointer = MemorySaver(serde=serializer)
```

**Solution 3**: Custom pickle-only serializer (use with encryption)

```python
import pickle
from langgraph.checkpoint.serde.base import SerializerProtocol
from langgraph.checkpoint.memory import MemorySaver

class PickleOnlySerializer(SerializerProtocol):
    def dumps_typed(self, obj):
        return ("pickle", pickle.dumps(obj))

    def loads_typed(self, data):
        t, b = data
        if t != "pickle":
            raise ValueError(f"Unexpected type: {t}")
        return pickle.loads(b)

checkpointer = MemorySaver(serde=PickleOnlySerializer())
```

### Issue 3: Exception Serialization

**Problem**: Exceptions cannot inherit from `Serializable`

**Workaround**: Store exception information as strings

```python
class ErrorState(BaseModel):
    error_type: str = ""
    error_message: str = ""
    error_traceback: str = ""

# In your node
try:
    result = risky_operation()
except Exception as e:
    return {
        "error": ErrorState(
            error_type=type(e).__name__,
            error_message=str(e),
            error_traceback=traceback.format_exc(),
        )
    }
```

---

## LangGraph Integration

### Tool Calling with Ollama

```python
from langchain.tools import tool
from langchain_ollama import ChatOllama

@tool
def validate_user(user_id: int, addresses: list[str]) -> bool:
    """Validate user using historical addresses."""
    return True

# Use a model fine-tuned for tool use
llm = ChatOllama(
    model="gpt-oss:20b",
    validate_model_on_init=True,
    temperature=0,
).bind_tools([validate_user])

result = llm.invoke(
    "Could you validate user 123? They previously lived at "
    "123 Fake St in Boston MA and 234 Pretend Boulevard in Houston TX."
)

if result.tool_calls:
    print(result.tool_calls)
    # Output: [{'name': 'validate_user', 'args': {...}, 'id': '...', 'type': 'tool_call'}]
```

**Note**: Make sure to use an Ollama model that supports [tool calling](https://ollama.com/search?&c=tools).

### Multimodal Support

```python
import base64
from io import BytesIO
from PIL import Image
from langchain.messages import HumanMessage

def convert_to_base64(pil_image):
    """Convert PIL images to Base64 encoded strings."""
    buffered = BytesIO()
    pil_image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# Load image
pil_image = Image.open("path/to/image.jpg")
image_b64 = convert_to_base64(pil_image)

# Create multimodal message
llm = ChatOllama(model="bakllava", temperature=0)

messages = [[
    HumanMessage(content=[
        {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_b64}"},
        {"type": "text", "text": "What is in this image?"},
    ])
]]

response = llm.invoke(messages)
print(response.content)
```

### Reasoning Models with Custom Roles

Some models like Granite 3.2 support custom message roles for thinking:

```python
from langchain_core.messages import ChatMessage

llm = ChatOllama(model="granite3.2:8b")

messages = [
    ChatMessage(role="control", content="thinking"),  # Enable thinking mode
    HumanMessage(content="What is 3^3?"),
]

response = llm.invoke(messages)
print(response.content)
# Output includes thought process + final answer
```

---

## Checkpointing and Persistence

### Basic Checkpointing Setup

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

# Create checkpointer
checkpointer = MemorySaver()

# Compile graph with checkpointer
graph = workflow.compile(checkpointer=checkpointer)

# Use thread_id for conversation persistence
config = {"configurable": {"thread_id": "user_session_123"}}
result = graph.invoke({"messages": [HumanMessage("Hello")]}, config)

# State is persisted - subsequent calls remember context
result2 = graph.invoke({"messages": [HumanMessage("What's my name?")]}, config)
```

### Production Checkpointer (PostgreSQL)

```python
from langgraph_checkpoint_postgres import PostgresSaver

# Recommended for production
checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:pass@localhost:5432/langgraph"
)
```

### Checkpointer Best Practices

1. **Use Thread IDs for Conversation Isolation**

```python
config = {
    "configurable": {
        "thread_id": f"customer_{customer_id}_session_{session_id}",
        "user_id": customer_id
    }
}
```

2. **Avoid Non-Serializable State**

```python
# WRONG - ChromaDB with locks
class State(TypedDict):
    chroma_client: Chroma  # Can't be pickled

# CORRECT - Store IDs, recreate client
class State(TypedDict):
    collection_name: str
    persistent_client: bool = False

# Recreate ChromaDB client in node using state values
```

3. **Use Appropriate Serializer**

```python
# For most use cases
from langgraph.checkpoint.serde import JsonPlusSerializer

# For dataframes or other special types
serializer = JsonPlusSerializer(pickle_fallback=True)
checkpointer = MemorySaver(serde=serializer)
```

### Time Travel with Checkpoints

```python
# Replay from specific checkpoint
config = {
    "configurable": {
        "thread_id": "1",
        "checkpoint_id": "0c62ca34-ac19-445d-bbb0-5b4984975b2a"
    }
}

# Replays steps before checkpoint_id, executes after
graph.invoke(None, config=config)
```

---

## Best Practices

### 1. Model Selection

| Model | Use Case | Notes |
|-------|----------|-------|
| `llama3.1` | General chat | Good balance of speed and quality |
| `gemma3:4b` | AGENTX chat default | Fast, good for voice applications |
| `gpt-oss:20b` | Tool calling | Fine-tuned for tool use |
| `granite3.2:8b` | Reasoning | Exposes thought process |
| `bakllava` | Vision tasks | Multimodal support |
| `llava:latest` | Vision tasks | Alternative multimodal model |

### 2. Streaming Best Practices

- Use `stream_mode="messages"` for chat applications
- Always check `langgraph_node` in metadata to filter events
- Handle both `on_chat_model_stream` and `on_llm_stream` events for Ollama
- Use `flush=True` when printing streamed output

### 3. State Management

- Use `default_factory` for dynamic Pydantic fields
- Avoid storing unpicklable objects in state (locks, open connections)
- Store IDs/references, recreate objects in nodes
- Use `Serializable` base class for custom state objects

### 4. Async Patterns

- Always use `ainvoke()` in async contexts
- Pass `config` parameter for context propagation
- Use `astream_events()` for fine-grained event handling
- Use `astream()` with `stream_mode="messages"` for token streaming

### 5. Tool Calling

- Use models fine-tuned for tool use (`gpt-oss`)
- Do NOT combine `with_structured_output()` and `bind_tools()`
- Use `response_format` parameter in `bind_tools()` for structured output

### 6. Error Handling

```python
# Handle Ollama connection errors
try:
    result = await llm.ainvoke(messages)
except ConnectionError as e:
    logger.error(f"Ollama not running: {e}")
    # Fallback or error response
except Exception as e:
    logger.error(f"LLM error: {e}")
```

### 7. Performance Optimization

- Set appropriate `num_ctx` (context window) for your use case
- Use `temperature=0` for deterministic responses
- Consider `num_predict` to limit output tokens
- Use `repeat_penalty` to reduce repetition

### 8. Testing

```python
# Mock ChatOllama for testing
from unittest.mock import MagicMock, AsyncMock

mock_llm = MagicMock(spec=ChatOllama)
mock_llm.ainvoke = AsyncMock(return_value=AIMessage(content="Test response"))

# Use in tests
result = await mock_llm.ainvoke(messages)
```

---

## Troubleshooting

### Issue: "No module named 'langchain_ollama'"

**Solution**: Install the package
```bash
pip install langchain-ollama
```

### Issue: "ollama: connection refused"

**Solution**: Start Ollama server
```bash
ollama serve
```

### Issue: "Cannot pickle '_thread.lock' object"

**Solution**: Check for ChromaDB or similar objects in state, use `default_factory` for dynamic fields

### Issue: "Object of type X is not JSON serializable"

**Solution**: Make objects inherit from `Serializable`, use `pickle_fallback=True`, or store as primitive types

### Issue: Streaming switches between event types

**Solution**: Handle both `on_chat_model_stream` and `on_llm_stream` events

### Issue: "bind_tools not callable after with_structured_output"

**Solution**: Do NOT chain these methods. Use `bind_tools(response_format=...)` instead

---

## References and Sources

- [ChatOllama - LangChain Documentation](https://docs.langchain.com/oss/python/integrations/chat/ollama)
- [Ollama Official](https://ollama.com/)
- [Ollama Model Library](https://ollama.com/search)
- [Ollama Tool Support](https://ollama.com/blog/tool-support)
- [Ollama Structured Outputs](https://ollama.com/blog/structured-outputs)
- [LangChain Streaming Documentation](https://docs.langchain.com/oss/python/langgraph/streaming)
- [LangGraph Checkpointing Guide](https://docs.langchain.com/oss/python/langgraph/persistence)
- [Mastering LangGraph Checkpointing (SparkCo.ai)](https://sparkco.ai/blog/mastering-langgraph-checkpointing-best-practices-for-2025)
- [Ollama Python Library](https://pypi.org/project/langchain-ollama/)
- [LangChain Python Help Forum](https://forum.langchain.com/)

---

## Appendix: Complete Example

```python
import asyncio
from typing import TypedDict, Annotated
from langchain_ollama import ChatOllama
from langchain.tools import tool
from langchain.messages import HumanMessage, AIMessage, AIMessageChunk
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# 1. Define tools
@tool
def get_weather(location: str) -> str:
    """Get weather at a location."""
    return f"It's sunny in {location}."

# 2. Define state
class State(TypedDict):
    messages: Annotated[list, "messages"]
    next: str

# 3. Define nodes
async def agent_node(state: State) -> State:
    """Agent node that decides what to do."""
    llm = ChatOllama(
        model="llama3.1",
        temperature=0,
    ).bind_tools([get_weather])

    response = await llm.ainvoke(state["messages"])
    return {"messages": [response]}

async def tool_node(state: State) -> State:
    """Execute tool calls."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls"):
        results = []
        for tool_call in last_message.tool_calls:
            if tool_call["name"] == "get_weather":
                result = get_weather.invoke(tool_call["args"])
                results.append(
                    {"role": "tool", "content": result, "tool_call_id": tool_call["id"]}
                )
        return {"messages": results}
    return state

# 4. Build graph
workflow = StateGraph(State)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.add_edge(START, "agent")

# Conditional routing
def should_continue(state: State):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

# 5. Compile with checkpointer
checkpointer = MemorySaver()
graph = workflow.compile(checkpointer=checkpointer)

# 6. Run with streaming
async def main():
    config = {"configurable": {"thread_id": "test_session"}}

    print("Streaming tokens:")
    async for chunk, metadata in graph.astream(
        {"messages": [HumanMessage("What's the weather in San Francisco?")]},
        config,
        stream_mode="messages",
    ):
        if isinstance(chunk, AIMessageChunk) and chunk.content:
            print(chunk.content, end="", flush=True)

    print("\n\nDone!")

asyncio.run(main())
```

---

**Document Status**: Complete
**Last Updated**: 2025-02-04
**Version**: 1.0

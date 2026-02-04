# DSPy Async Streaming with Ollama

**Research Date:** 2025-02-04
**Topic:** Async streaming patterns for DSPy with Ollama backend

---

## Executive Summary

DSPy 2.6.0+ supports async streaming for Ollama backends using `dspy.streamify()`. This document covers the implementation patterns for token-by-token streaming, intermediate status messages, and ReAct agent streaming with Ollama's `ollama_chat/` prefix.

## 1. Core DSPy Streaming Concepts

### Two Types of Streaming

1. **Output Token Streaming**: Stream individual tokens as they're generated
2. **Intermediate Status Streaming**: Provide real-time updates about program execution

### Key Requirements

- Streamed field must be of type `str`
- Requires async context (`async for`)
- Works with any module in the pipeline, not just final output
- Compatible with Ollama via `ollama_chat/` model prefix

## 2. Basic Streaming with Ollama

### Configure DSPy with Ollama

```python
import dspy

# Configure DSPy with Ollama backend
ollama_lm = dspy.LM(
    "ollama_chat/gemma3:4b",  # Note: ollama_chat/ prefix required
    api_base="http://localhost:11434",
    api_key="",
    temperature=0.7
)

dspy.configure(lm=ollama_lm)
```

### Basic Token Streaming

```python
import asyncio
import dspy

# Create base predictor
predict = dspy.Predict("question->answer")

# Wrap with streaming for 'answer' field
stream_predict = dspy.streamify(
    predict,
    stream_listeners=[
        dspy.streaming.StreamListener(signature_field_name="answer")
    ],
)

# Consume the stream
async def read_stream():
    output = stream_predict(question="Why did a chicken cross the kitchen?")

    async for chunk in output:
        if isinstance(chunk, dspy.streaming.StreamResponse):
            print(f"Token: {chunk.chunk}")
        elif isinstance(chunk, dspy.Prediction):
            print(f"Final: {chunk.answer}")

asyncio.run(read_stream())
```

**Output:**
```
Token: To
Token:  get
Token:  to
Token:  the
Token:  other
Token:  side
Token:  of
Token:  the
Token:  frying
Token:  pan!
Final: To get to the other side of the frying pan!
```

## 3. Understanding StreamResponse

`StreamResponse` has three fields:

```python
@dataclass
class StreamResponse:
    predict_name: str           # Which predictor (e.g., 'self', 'predict1')
    signature_field_name: str   # Which output field (e.g., 'answer')
    chunk: str                  # The token value
```

### Handling Different Stream Types

```python
async for chunk in stream_predict(question="..."):
    if isinstance(chunk, dspy.streaming.StreamResponse):
        # Token streaming
        print(f"Token from {chunk.signature_field_name}: {chunk.chunk}")
    elif isinstance(chunk, dspy.streaming.StatusMessage):
        # Status update
        print(f"Status: {chunk.message}")
    elif isinstance(chunk, dspy.Prediction):
        # Final result
        print(f"Result: {chunk}")
```

## 4. Streaming with ReAct Agents

### ReAct with Reusable StreamListener

ReAct agents call the same module multiple times (in a loop). Use `allow_reuse=True`:

```python
import asyncio
import dspy

# Define tools
def fetch_user_info(user_name: str) -> dict:
    return {"name": user_name, "birthday": "2009-05-16"}

def get_sports_news(year: int) -> str:
    if year == 2009:
        return "Usain Bolt broke the 100m world record."
    return None

# Create ReAct agent
react = dspy.ReAct("question->answer", tools=[fetch_user_info, get_sports_news])

# IMPORTANT: allow_reuse=True for ReAct (multiple iterations)
stream_react = dspy.streamify(
    react,
    stream_listeners=[
        dspy.streaming.StreamListener(
            signature_field_name="next_thought",  # ReAct's built-in field
            allow_reuse=True  # Required for ReAct!
        )
    ],
)

async def stream_react_example():
    output = stream_react(question="What sports news happened when Adam was born?")

    async for chunk in output:
        if isinstance(chunk, dspy.streaming.StreamResponse):
            print(f"Thought: {chunk.chunk}")
        elif isinstance(chunk, dspy.Prediction):
            print(f"Final Answer: {chunk.answer}")

asyncio.run(stream_react_example())
```

**Key Points:**
- ReAct has built-in `next_thought` field for intermediate reasoning
- `allow_reuse=True` is critical for ReAct (otherwise only first iteration streams)
- Each tool call produces a `next_thought` chunk

## 5. Multi-Module Streaming

### Streaming Multiple Fields

```python
import asyncio
import dspy

class MyModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict1 = dspy.Predict("question->answer")
        self.predict2 = dspy.Predict("answer->simplified_answer")

    def forward(self, question: str, **kwargs):
        answer = self.predict1(question=question)
        simplified = self.predict2(answer=answer.answer)
        return simplified

# Create listeners for both fields
stream_listeners = [
    dspy.streaming.StreamListener(signature_field_name="answer"),
    dspy.streaming.StreamListener(signature_field_name="simplified_answer"),
]

stream_predict = dspy.streamify(
    MyModule(),
    stream_listeners=stream_listeners,
)

async def multi_field_stream():
    output = stream_predict(question="Explain quantum entanglement simply")

    async for chunk in output:
        if isinstance(chunk, dspy.streaming.StreamResponse):
            print(f"[{chunk.predict_name}:{chunk.signature_field_name}] {chunk.chunk}")
```

### Handling Duplicate Field Names

When multiple predictors have fields with the same name:

```python
stream_listeners = [
    dspy.streaming.StreamListener(
        signature_field_name="answer",
        predict=predict.predict1,    # Disambiguate by predict instance
        predict_name="predict1"
    ),
    dspy.streaming.StreamListener(
        signature_field_name="answer",
        predict=predict.predict2,
        predict_name="predict2"
    ),
]
```

## 6. Status Message Streaming

### Custom Status Provider

```python
import dspy

class MyStatusProvider(dspy.streaming.StatusMessageProvider):
    def lm_start_status_message(self, instance, inputs):
        return f"🤖 Calling LLM with: {inputs}"

    def lm_end_status_message(self, outputs):
        return f"✅ LLM finished"

    def tool_start_status_message(self, instance, inputs):
        return f"🔧 Calling tool: {instance.name}"

    def tool_end_status_message(self, outputs):
        return f"✨ Tool result: {outputs}"

    def module_start_status_message(self, instance, inputs):
        return f"📦 Module {instance.__class__.__name__} starting"

    def module_end_status_message(self, outputs):
        return f"📦 Module finished"

# Use with streaming
stream_predict = dspy.streamify(
    react,
    stream_listeners=[...],
    status_message_provider=MyStatusProvider(),
)

# Handle status messages
async for chunk in stream_predict(question="..."):
    if isinstance(chunk, dspy.streaming.StatusMessage):
        print(f"[STATUS] {chunk.message}")
```

## 7. Synchronous vs Async Streaming

### Default: Async Generator

```python
# Returns async generator
stream_predict = dspy.streamify(predict, stream_listeners=[...])

async for chunk in stream_predict(question="..."):
    ...
```

### Sync Generator (Set `async_streaming=False`)

```python
# Returns sync generator
stream_predict = dspy.streamify(
    predict,
    stream_listeners=[...],
    async_streaming=False,  # Returns sync generator
)

for chunk in stream_predict(question="..."):
    ...
```

**Use sync when:**
- Running in Jupyter/Colab (existing event loop)
- Not using async/await elsewhere

**Use async when:**
- Building async APIs (FastAPI, etc.)
- Need concurrent operations
- Integration with LangGraph async nodes

## 8. Streaming with Caching

When cache is enabled and a cached result exists:

```python
# With cache=True (default)
lm = dspy.LM("ollama_chat/gemma3:4b", cache=True)
dspy.configure(lm=lm)

stream_predict = dspy.streamify(predict, stream_listeners=[...])

# First call: streams tokens
async for chunk in stream_predict(question="What is 42?"):
    # StreamResponse + Prediction

# Second call (cached): skips to final only
async for chunk in stream_predict(question="What is 42?"):
    # Only Prediction (no StreamResponse)
```

**To always stream:** Set `cache=False` on LM.

## 9. Deployment Patterns

### FastAPI with Server-Sent Events

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import dspy
import asyncio

app = FastAPI()

# Configure DSPy with Ollama
ollama_lm = dspy.LM(
    "ollama_chat/gemma3:4b",
    api_base="http://localhost:11434",
    api_key="",
    temperature=0.7
)
dspy.configure(lm=ollama_lm)

# Create streaming program
predict = dspy.Predict("question->answer")
stream_predict = dspy.streamify(
    predict,
    stream_listeners=[dspy.streaming.StreamListener(signature_field_name="answer")],
)

@app.post("/chat/stream")
async def chat_stream(question: str):
    """Server-Sent Events endpoint for streaming chat."""

    async def generate():
        async for value in stream_predict(question=question):
            if isinstance(value, dspy.streaming.StreamResponse):
                # Stream token
                data = {"token": value.chunk}
                yield f"data: {json.dumps(data)}\n\n"
            elif isinstance(value, dspy.Prediction):
                # Final result
                data = {"done": True, "answer": value.answer}
                yield f"data: {json.dumps(data)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )
```

### WebSocket Streaming (for Voice/TTS)

```python
from fastapi import WebSocket

@app.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket):
    await websocket.accept()

    try:
        # Receive question
        data = await websocket.receive_json()
        question = data["question"]

        # Stream DSPy output
        async for chunk in stream_predict(question=question):
            if isinstance(chunk, dspy.streaming.StreamResponse):
                # Send token for TTS
                await websocket.send_json({
                    "type": "token",
                    "text": chunk.chunk
                })
            elif isinstance(chunk, dspy.Prediction):
                # Final result
                await websocket.send_json({
                    "type": "done",
                    "answer": chunk.answer
                })
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
```

## 10. Integration with LangGraph

### DSPy Streaming in LangGraph Node

```python
from langgraph.graph import StateGraph
from langgraph.types import StreamWriter
from typing import TypedDict

class AgentState(TypedDict):
    question: str
    answer: str
    tokens: list[str]

# Configure DSPy
ollama_lm = dspy.LM("ollama_chat/gemma3:4b", api_base="http://localhost:11434")
dspy.configure(lm=ollama_lm)

# Create streaming DSPy module
predict = dspy.Predict("question->answer")
stream_predict = dspy.streamify(
    predict,
    stream_listeners=[dspy.streaming.StreamListener(signature_field_name="answer")],
)

async def dspy_streaming_node(
    state: AgentState,
    config: RunnableConfig,
    writer: StreamWriter  # LangGraph streaming support
):
    """LangGraph node that streams DSPy output."""

    full_answer = ""
    async for chunk in stream_predict(question=state["question"]):
        if isinstance(chunk, dspy.streaming.StreamResponse):
            # Accumulate tokens
            full_answer += chunk.chunk

            # Stream to client via StreamWriter
            await writer({"token": chunk.chunk})

        elif isinstance(chunk, dspy.Prediction):
            # Final prediction
            full_answer = chunk.answer

    return {"answer": full_answer}

# Build graph
graph = StateGraph(AgentState)
graph.add_node("agent", dspy_streaming_node)
graph.add_edge(START, "agent")
graph.add_edge("agent", END)

app = graph.compile()

# Stream from LangGraph
async for chunk in app.stream({"question": "Hello"}):
    print(chunk)  # Includes DSPy tokens via StreamWriter
```

## 11. Best Practices

### 1. Always Use `allow_reuse=True` for ReAct

```python
# WRONG - only first iteration streams
listener = dspy.streaming.StreamListener(signature_field_name="next_thought")

# RIGHT - all iterations stream
listener = dspy.streaming.StreamListener(
    signature_field_name="next_thought",
    allow_reuse=True  # Required for ReAct!
)
```

### 2. Disable Cache for Always-Streaming

```python
# Cache can skip token streaming
lm = dspy.LM("ollama_chat/gemma3:4b", cache=False)
```

### 3. Use Async for Production APIs

```python
# For FastAPI, async web servers, etc.
stream_predict = dspy.streamify(predict, stream_listeners=[...])
# async_streaming=True is default

async for chunk in stream_predict(...):
    ...
```

### 4. Handle All Chunk Types

```python
async for chunk in stream_predict(...):
    if isinstance(chunk, dspy.streaming.StreamResponse):
        # Tokens
    elif isinstance(chunk, dspy.streaming.StatusMessage):
        # Status updates
    elif isinstance(chunk, dspy.Prediction):
        # Final result
```

### 5. Set Timeout for Long-Running Streams

```python
import asyncio

async def stream_with_timeout():
    try:
        async for chunk in asyncio.wait_for(
            stream_predict(question="...").__anext__(),
            timeout=30.0
        ):
            yield chunk
    except asyncio.TimeoutError:
        print("Stream timeout")
```

## 12. Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Only first token streams | Missing `allow_reuse=True` | Add to ReAct StreamListener |
| No tokens (just final) | Cache enabled | Set `cache=False` on LM |
| "Not an async generator" | Used `for` instead of `async for` | Use `async for` or set `async_streaming=False` |
| Slow streaming | Ollama not optimized | Use smaller models or GPU |
| Broken chunks | Token boundary issues | DSPy handles this automatically |

## 13. Quick Reference

### Basic Setup
```python
import dspy

lm = dspy.LM("ollama_chat/gemma3:4b", api_base="http://localhost:11434")
dspy.configure(lm=lm)
```

### Basic Streaming
```python
stream_predict = dspy.streamify(
    predict,
    stream_listeners=[
        dspy.streaming.StreamListener(signature_field_name="field_name")
    ],
)

async for chunk in stream_predict(...):
    if isinstance(chunk, dspy.streaming.StreamResponse):
        print(chunk.chunk)
```

### ReAct Streaming
```python
stream_react = dspy.streamify(
    react,
    stream_listeners=[
        dspy.streaming.StreamListener(
            signature_field_name="next_thought",
            allow_reuse=True  # Required!
        )
    ],
)
```

### Status Messages
```python
class MyProvider(dspy.streaming.StatusMessageProvider):
    def lm_start_status_message(self, instance, inputs):
        return f"Calling LLM..."

stream_predict = dspy.streamify(
    predict,
    stream_listeners=[...],
    status_message_provider=MyProvider(),
)
```

## Sources

- [DSPy Streaming Tutorial](https://dspy.ai/tutorials/streaming/)
- [DSPy streamify API Reference](https://dspy.ai/api/utils/streamify/)
- [DSPy Deployment Guide](https://dspy.ai/tutorials/deployment/)
- [DSPy Language Models Documentation](https://dspy.ai/learn/programming/language_models/)
- [DSPy GitHub Issue #338 - Streaming](https://github.com/stanfordnlp/dspy/issues/338)
- [Ollama Streaming Documentation](https://docs.ollama.com/capabilities/streaming)
- [DSPy for Prompt Engineers - DEV.to](https://dev.to/beowulfcodes/dspy-for-prompt-engineers-build-your-first-modular-llm-program-openai-llama-2j62)

---

**Next Steps:**
- See `04_async_streaming_patterns.md` for LangGraph streaming
- See `06_dspy_langgraph_integration.md` for hybrid patterns
- See `03_ollama_langchain_integration.md` for Ollama configuration

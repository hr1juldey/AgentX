# DSPy + LangGraph Integration Guide

**Research Date:** 2026-02-04  
**Status:** Comprehensive research completed  
**Focus:** Hybrid architectures combining DSPy's programmatic LLM framework with LangGraph's stateful orchestration

---

## Executive Summary

This document provides comprehensive guidance on integrating DSPy modules (including ReAct agents) as nodes within LangGraph workflows. The integration leverages the strengths of both frameworks:

- **DSPy**: Declarative prompting, programmatic modules, automatic optimization (MIPROv2, GEPA), ReAct agents with tools
- **LangGraph**: Stateful orchestration, explicit state management, checkpointing/persistence, control flow graphs

**Key Pattern**: Use LangGraph for orchestration (state, routing, persistence) and wrap DSPy modules as computational nodes for optimized LLM interactions.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Pattern 1: Wrapping DSPy Modules as LangGraph Nodes](#pattern-1-wrapping-dspy-modules-as-langgraph-nodes)
3. [Pattern 2: Converting DSPy Signatures to LangGraph State](#pattern-2-converting-dspy-signatures-to-langgraph-state)
4. [Pattern 3: Tool Integration Patterns](#pattern-3-tool-integration-patterns)
5. [Pattern 4: Memory and Persistence](#pattern-4-memory-and-persistence)
6. [Complete Code Examples](#complete-code-examples)
7. [Best Practices](#best-practices)
8. [References](#references)

---

## Architecture Overview

### Why Combine DSPy + LangGraph?

| Framework | Strengths | Role in Hybrid Architecture |
|-----------|-----------|----------------------------|
| **DSPy** | - Declarative signatures<br>- Programmatic modules<br>- Auto-optimization (MIPROv2, GEPA)<br>- ReAct agents with tools | Computational units for LLM interactions |
| **LangGraph** | - Stateful orchestration<br>- Explicit state schemas (TypedDict/Pydantic)<br>- Checkpointing/persistence<br>- Control flow (START/END/edges) | Orchestration layer for multi-step workflows |

### Complementary Capabilities

```python
# DSPy excels at:
- Prompt optimization (BootstrapFewShot, MIPROv2, KNN)
- Tool-using agents (ReAct with automatic tool selection)
- Programmatic LM interfaces (Signatures, Modules)
- Evaluation and metrics (SemanticF1, answer_exact_match)

# LangGraph excels at:
- Multi-agent coordination
- State management and persistence
- Long-running workflows with checkpointing
- Conditional routing and parallel execution
```

---

## Pattern 1: Wrapping DSPy Modules as LangGraph Nodes

### 1.1 Basic Node Wrapper Pattern

```python
import dspy
from typing import TypedDict, Annotated
from operator import add
from langgraph.graph import StateGraph, START, END

# ========== DSPy Module Definition ==========

class QuestionAnswerSignature(dspy.Signature):
    """Answer questions about a given context."""
    context = dspy.InputField(desc="Background information")
    question = dspy.InputField(desc="Question to answer")
    answer = dspy.OutputField(desc="Answer to the question")

class QAModule(dspy.Module):
    """DSPy module for Q&A tasks."""

    def __init__(self):
        super().__init__()
        self.generate_answer = dspy.ChainOfThought(QuestionAnswerSignature)

    def forward(self, context: str, question: str):
        return self.generate_answer(context=context, question=question)

# ========== LangGraph State Definition ==========

class GraphState(TypedDict):
    question: str
    context: str
    answer: str
    messages: Annotated[list, add_messages]  # Append-only reducer

# ========== LangGraph Node Wrapper ==========

# Initialize DSPy module (reuse instance)
qa_module = QAModule()

def dspy_qa_node(state: GraphState) -> dict:
    """
    LangGraph node that wraps a DSPy module.

    Args:
        state: Current graph state

    Returns:
        Partial state update (keys to update)
    """
    # Call DSPy module
    result = qa_module(
        context=state["context"],
        question=state["question"]
    )

    # Return partial state update
    return {
        "answer": result.answer,
        "messages": [{"role": "assistant", "content": result.answer}]
    }

# ========== Build Graph ==========

graph = StateGraph(GraphState)
graph.add_node("qa", dspy_qa_node)
graph.add_edge(START, "qa")
graph.add_edge("qa", END)

app = graph.compile()
```

### 1.2 Wrapping DSPy ReAct Agents

```python
import dspy
from typing import Callable

# ========== Define Tools ==========

def search_web(query: str) -> str:
    """Search the web for information."""
    # Implementation
    return f"Search results for: {query}"

def get_weather(city: str) -> str:
    """Get current weather for a city."""
    # Implementation
    return f"Weather in {city}: Sunny, 75°F"

def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"

# ========== DSPy ReAct Agent ==========

react_agent = dspy.ReAct(
    signature="question -> answer",
    tools=[search_web, get_weather, calculator],
    max_iters=10
)

# ========== LangGraph Node Wrapper ==========

def dspy_react_node(state: GraphState) -> dict:
    """
    LangGraph node wrapping DSPy ReAct agent.

    The ReAct agent will:
    1. Reason about the question
    2. Select appropriate tools
    3. Execute tool calls
    4. Iterate until completion (max_iters)
    """
    result = react_agent(question=state["question"])

    return {
        "answer": result.answer,
        "messages": [
            {"role": "assistant", "content": result.answer}
        ]
    }
```

### 1.3 Async Node Wrappers

```python
import asyncio

async def async_dspy_node(state: GraphState) -> dict:
    """
    Async LangGraph node wrapping DSPy module.

    Use async nodes when:
    - Tools make async calls (HTTP requests, DB queries)
    - You need concurrent execution
    - Working with async DSPy modules
    """
    # Use acall for async DSPy operations
    result = await qa_module.acall(
        context=state["context"],
        question=state["question"]
    )

    return {
        "answer": result.answer,
        "messages": [{"role": "assistant", "content": result.answer}]
    }

# For async tools in ReAct:
async def async_search(query: str) -> str:
    """Async web search."""
    await asyncio.sleep(0.1)  # Simulate async I/O
    return f"Results for: {query}"

async_react_agent = dspy.ReAct(
    signature="question -> answer",
    tools=[async_search],
    max_iters=5
)

async def async_react_node(state: GraphState) -> dict:
    result = await async_react_agent.acall(question=state["question"])
    return {"answer": result.answer}
```

### 1.4 Module Instance Management

**Best Practice**: Store DSPy module instances in LangGraph's runtime context to avoid reinitialization:

```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

# Initialize module once
qa_module = QAModule()

def create_graph_with_module():
    """Create graph with pre-initialized module."""
    graph = StateGraph(GraphState)

    # Closure captures module instance
    def qa_node(state):
        result = qa_module(context=state["context"], question=state["question"])
        return {"answer": result.answer}

    graph.add_node("qa", qa_node)
    graph.add_edge(START, "qa")
    graph.add_edge("qa", END)

    return graph.compile(checkpointer=MemorySaver())
```

---

## Pattern 2: Converting DSPy Signatures to LangGraph State

### 2.1 Simple Signature Mapping

```python
# ========== DSPy Signature ==========
class SimpleQA(dspy.Signature):
    """Simple question answering."""
    question = dspy.InputField()
    answer = dspy.OutputField()

# ========== LangGraph State Schema ==========
class GraphState(TypedDict):
    question: str      # Maps to DSPy InputField
    answer: str        # Maps to DSPy OutputField
    context: str       # Additional state (not in signature)
```

### 2.2 Complex Signature with Multiple Fields

```python
# ========== DSPy Signature ==========
class ResearchSignature(dspy.Signature):
    """Conduct research on a topic."""
    topic = dspy.InputField(desc="Research topic")
    depth_level = dspy.InputField(desc="1=brief, 2=detailed, 3=comprehensive")
    findings = dspy.OutputField(desc="Key findings")
    sources = dspy.OutputField(desc="List of sources cited")
    confidence = dspy.OutputField(desc="Confidence score (0-1)")

# ========== LangGraph State Schema ==========
class ResearchState(TypedDict):
    topic: str
    depth_level: int
    findings: str
    sources: list[str]
    confidence: float
    status: str  # Additional state for workflow tracking
    timestamp: str  # Additional metadata
```

### 2.3 Optional Fields and Default Values

```python
from typing import Optional

# ========== DSPy Signature with Optionals ==========
class FlexibleQA(dspy.Signature):
    """Question answering with optional context."""
    question = dspy.InputField(desc="Question to answer")
    context = dspy.InputField(desc="Optional background context", default="")
    answer = dspy.OutputField()

# ========== LangGraph State with Optionals ==========
class FlexibleState(TypedDict):
    question: str
    context: Optional[str]  # Explicit optional in state
    answer: str
    has_context: bool  # Flag to track if context was provided
```

### 2.4 Pydantic-Based State Schema

```python
from pydantic import BaseModel, Field

# ========== DSPy Signature ==========
class DocumentSummarySignature(dspy.Signature):
    """Summarize a document."""
    document = dspy.InputField(desc="Full document text")
    max_length = dspy.InputField(desc="Maximum summary length", default=500)
    summary = dspy.OutputField()
    key_points = dspy.OutputField(desc="List of key points")

# ========== LangGraph State (Pydantic) ==========
class SummaryState(BaseModel):
    document: str = Field(..., description="Full document text")
    max_length: int = Field(500, description="Maximum summary length")
    summary: str = Field("", description="Generated summary")
    key_points: list[str] = Field(default_factory=list, description="Key points extracted")
    word_count: int = Field(0, description="Summary word count")
    quality_score: float = Field(0.0, description="Summary quality score")

# LangGraph accepts Pydantic models as state_schema
graph = StateGraph(state_schema=SummaryState)
```

### 2.5 State Reducers for Aggregation

```python
from typing import Annotated
from operator import add

# ========== Reducer for append-only lists ==========
class MultiResearchState(TypedDict):
    query: str
    # Each research result appends to this list
    results: Annotated[list[dict], add]  # reducer: operator.add
    # Counter increments with each iteration
    iteration: Annotated[int, add]
    completed: bool

def research_node(state: MultiResearchState) -> dict:
    """Node that adds to results list."""
    new_result = {"source": "web", "data": "..." * 20}

    return {
        "results": [new_result],  # Appends to existing list
        "iteration": 1,  # Increments counter
        "completed": len(state["results"]) >= 3
    }
```

---

## Pattern 3: Tool Integration Patterns

### 3.1 Basic Tool Wrapping for DSPy

```python
import dspy

# Define tools as plain Python functions
def search_database(query: str) -> str:
    """Search the internal database."""
    # Implementation
    return f"DB results for: {query}"

def fetch_user_data(user_id: int) -> dict:
    """Fetch user information by ID."""
    # Implementation
    return {"id": user_id, "name": "John Doe", "email": "john@example.com"}

# Wrap in dspy.Tool for DSPy
tools = [
    dspy.Tool(search_database),
    dspy.Tool(fetch_user_data)
]

# Use with ReAct
react_agent = dspy.ReAct(
    signature="query -> response",
    tools=tools,
    max_iters=5
)
```

### 3.2 Tool Registry Pattern

```python
from typing import Dict, Callable, Any

class ToolRegistry:
    """
    Registry for managing tools with metadata.

    Provides:
    - Tool discovery
    - Permission scoping
    - Rate limiting
    - Audit logging
    """

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._metadata: Dict[str, dict] = {}

    def register(
        self,
        func: Callable,
        scope: str = "public",
        rate_limit: int = 100,
        description: str = ""
    ):
        """Register a tool with metadata."""
        name = func.__name__
        self._tools[name] = func
        self._metadata[name] = {
            "scope": scope,
            "rate_limit": rate_limit,
            "description": description or func.__doc__,
            "callable": func
        }

    def get_tools(self, scope: str = "public") -> list[dspy.Tool]:
        """Get tools by scope."""
        return [
            dspy.Tool(meta["callable"])
            for name, meta in self._metadata.items()
            if meta["scope"] == scope
        ]

    def get_tool(self, name: str) -> Callable:
        """Get specific tool by name."""
        return self._tools.get(name)

# Usage
registry = ToolRegistry()

@registry.register(scope="admin", rate_limit=10)
def delete_user(user_id: int) -> str:
    """Delete a user (admin only)."""
    return f"Deleted user {user_id}"

@registry.register(scope="public")
def get_user(user_id: int) -> dict:
    """Get user info (public)."""
    return {"id": user_id, "name": "User"}

# Get scoped tools for DSPy ReAct
admin_tools = registry.get_tools(scope="admin")
public_agent = dspy.ReAct("query -> answer", tools=registry.get_tools(scope="public"))
admin_agent = dspy.ReAct("query -> answer", tools=admin_tools)
```

### 3.3 Passing Tools Through LangGraph State

```python
class ToolAwareState(TypedDict):
    question: str
    answer: str
    available_tools: list[Callable]  # Tools passed through state
    tool_results: list[dict]
    iteration: int

def tool_routing_node(state: ToolAwareState) -> dict:
    """
    Node that uses tools from state.

    Tools can be injected at graph invocation time.
    """
    # Get tools from state (injected at runtime)
    tools = state.get("available_tools", [])

    # Create ReAct agent with dynamic tools
    agent = dspy.ReAct(
        signature="question -> answer",
        tools=tools,
        max_iters=5
    )

    result = agent(question=state["question"])

    return {
        "answer": result.answer,
        "tool_results": getattr(result, "trajectory", []),
        "iteration": state.get("iteration", 0) + 1
    }

# Invoke with custom tools
app = graph.compile()
result = app.invoke(
    {"question": "What's the weather?", "available_tools": [get_weather]},
    config={"configurable": {"thread_id": "123"}}
)
```

### 3.4 Tool Security and Permissions

```python
from functools import wraps
import time

class SecureTool:
    """
    Wrapper for tools with security features.

    Implements:
    - Rate limiting
    - Audit logging
    - Permission checks
    """

    def __init__(self, func, permissions=None, rate_limit=100):
        self.func = func
        self.permissions = permissions or []
        self.rate_limit = rate_limit
        self.call_count = 0
        self.last_reset = time.time()
        self.audit_log = []

    def __call__(self, *args, **kwargs):
        # Check rate limit
        if time.time() - self.last_reset > 60:
            self.call_count = 0
            self.last_reset = time.time()

        if self.call_count >= self.rate_limit:
            raise Exception(f"Rate limit exceeded for {self.func.__name__}")

        # Audit log
        self.audit_log.append({
            "timestamp": time.time(),
            "args": args,
            "kwargs": kwargs
        })

        self.call_count += 1
        return self.func(*args, **kwargs)

# Wrap tools with security
secure_search = SecureTool(search_web, rate_limit=50)
secure_db = SecureTool(search_database, permissions=["admin"])

# Use in DSPy
secure_agent = dspy.ReAct(
    signature="query -> answer",
    tools=[secure_search, secure_db],
    max_iters=5
)
```

### 3.5 Native vs Manual Tool Calling

```python
# ========== Native Tool Calling (Default for JSONAdapter) ==========

# Configure adapter to use native function calling
chat_adapter = dspy.ChatAdapter(use_native_function_calling=True)
dspy.configure(lm=dspy.LM("ollama_chat/gemma3:4b"), adapter=chat_adapter)

# Native calling uses model's built-in function calling
react_native = dspy.ReAct(
    "question -> answer",
    tools=[search_web, get_weather]
)

# ========== Manual Tool Calling (Text-based) ==========

# Disable native calling for text-based parsing
json_adapter = dspy.JSONAdapter(use_native_function_calling=False)
dspy.configure(lm=dspy.LM("ollama_chat/gemma3:4b"), adapter=json_adapter)

# Manual calling parses tool calls from text
react_manual = dspy.ReAct(
    "question -> answer",
    tools=[search_web, get_weather]
)
```

---

## Pattern 4: Memory and Persistence

### 4.1 LangGraph Checkpointing with DSPy

```python
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import MemorySaver

# ========== Checkpointer Setup ==========

# For production (durable)
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")

# For development (ephemeral)
checkpointer = MemorySaver()

# ========== Build Graph with Checkpointing ==========

graph = StateGraph(GraphState)
graph.add_node("qa", dspy_qa_node)
graph.add_edge(START, "qa")
graph.add_edge("qa", END)

app = graph.compile(checkpointer=checkpointer)

# ========== Invoke with Thread ID ==========

result = app.invoke(
    {"question": "What is AGENTX?", "context": "..."},
    config={"configurable": {"thread_id": "session_123"}}
)

# Resume from checkpoint
result2 = app.invoke(
    None,  # None continues from last state
    config={"configurable": {"thread_id": "session_123"}}
)
```

### 4.2 Persistence Modes

LangGraph offers three persistence modes with different durability/performance tradeoffs:

| Mode | Description | Durability | Performance |
|------|-------------|------------|-------------|
| **exit** | Checkpoints written only when execution finishes | Low (crashes lose data) | Best |
| **async** | Checkpoints written asynchronously during execution | Medium (small risk) | Good |
| **sync** | Checkpoints written synchronously before each step | High (atomic) | Slower |

```python
# Sync persistence (highest durability)
app = graph.compile(
    checkpointer=SqliteSaver.from_conn_string("checkpoints.db"),
    interrupt_before=None,  # No interrupts
)

# Async persistence (balanced)
# Configure at graph level or per invocation
result = app.invoke(
    state,
    config={"configurable": {"thread_id": "123"}},
    mode="async"  # Async checkpointing
)
```

### 4.3 State Snapshot History

```python
# Get checkpoint history
from langgraph.checkpoint import Checkpoint

thread_id = "session_123"

# List all checkpoints for a thread
checkpoints = []
for checkpoint in app.checkpointer.list(config={"configurable": {"thread_id": thread_id}}):
    checkpoints.append(checkpoint)

# Get specific checkpoint
config = {"configurable": {"thread_id": thread_id}, "checkpoint_ns": "", "checkpoint_id": checkpoints[0].config["checkpoint_id"]}
state_snapshot = app.get_state(config)

print(state_snapshot.values)  # State at this checkpoint
print(state_snapshot.next)  # Next node to execute
print(state_snapshot.metadata)  # Checkpoint metadata
```

### 4.4 Integrating DSPy Memory (Mem0AI) with LangGraph

```python
from mem0 import Memory

# ========== Mem0AI Setup ==========
memory = Memory.from_config({
    "provider": "qdrant",
    "config": {
        "host": "localhost",
        "port": 6333,
        "collection_name": "agentx_memory"
    }
})

# ========== Memory-Augmented State ==========
class MemoryState(TypedDict):
    question: str
    answer: str
    user_id: str  # For memory retrieval
    context: str  # Retrieved memories
    conversation_id: str

# ========== Node with Memory ==========
def memory_retrieve_node(state: MemoryState) -> dict:
    """Retrieve relevant memories before answering."""

    # Search memories
    memories = memory.search(
        query=state["question"],
        user_id=state["user_id"],
        limit=5
    )

    # Format context
    context_str = "\n".join([m["memory"] for m in memories])

    return {"context": context_str}

def dspy_qa_with_memory(state: MemoryState) -> dict:
    """Answer question with retrieved memory context."""

    # Use DSPy with memory context
    result = qa_module(
        context=state["context"],
        question=state["question"]
    )

    # Store new memory
    memory.add(
        memory=f"User asked: {state['question']}\nAnswer: {result.answer}",
        user_id=state["user_id"],
        metadata={"conversation_id": state["conversation_id"]}
    )

    return {"answer": result.answer}

# ========== Build Graph ==========
graph = StateGraph(MemoryState)
graph.add_node("retrieve_memory", memory_retrieve_node)
graph.add_node("qa", dspy_qa_with_memory)
graph.add_edge(START, "retrieve_memory")
graph.add_edge("retrieve_memory", "qa")
graph.add_edge("qa", END)

app = graph.compile(checkpointer=SqliteSaver.from_conn_string("checkpoints.db"))
```

### 4.5 Vector Store Integration

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# ========== Vector Store Setup ==========
qdrant = QdrantClient(url="http://localhost:6333")

# Create collection
qdrant.create_collection(
    collection_name="agentx_vectors",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
)

# ========== Tool for Vector Search ==========
def vector_search(query: str, top_k: int = 5) -> str:
    """
    Search vector store for relevant documents.

    This tool can be used by DSPy ReAct agents.
    """
    # Embed query (using your embedding model)
    query_vector = embed_query(query)  # Placeholder

    # Search Qdrant
    results = qdrant.search(
        collection_name="agentx_vectors",
        query_vector=query_vector,
        limit=top_k
    )

    # Format results
    return "\n".join([r.payload["text"] for r in results])

# Register as tool
registry = ToolRegistry()
registry.register(vector_search, scope="public")

# Use in DSPy agent
rag_agent = dspy.ReAct(
    signature="question -> answer",
    tools=[vector_search],
    max_iters=3
)
```

---

## Complete Code Examples

### Example 1: Simple Q&A Pipeline

```python
import dspy
from typing import TypedDict, Annotated
from operator import add
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

# ========== DSPy Setup ==========
lm = dspy.LM("ollama_chat/gemma3:4b", api_base="http://localhost:11434")
dspy.configure(lm=lm)

# ========== DSPy Module ==========
class QASignature(dspy.Signature):
    """Answer a question based on context."""
    context = dspy.InputField(desc="Background information")
    question = dspy.InputField(desc="Question to answer")
    answer = dspy.OutputField(desc="Answer to the question")

class QAModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(QASignature)

    def forward(self, context: str, question: str):
        return self.generate(context=context, question=question)

# Initialize module
qa_module = QAModule()

# ========== LangGraph State ==========
class QAGraphState(TypedDict):
    question: str
    context: str
    answer: str
    messages: Annotated[list, add]

# ========== LangGraph Nodes ==========
def qa_node(state: QAGraphState) -> dict:
    """DSPy-powered Q&A node."""
    result = qa_module(
        context=state["context"],
        question=state["question"]
    )

    return {
        "answer": result.answer,
        "messages": [{"role": "assistant", "content": result.answer}]
    }

# ========== Build Graph ==========
def create_qa_graph():
    graph = StateGraph(QAGraphState)
    graph.add_node("qa", qa_node)
    graph.add_edge(START, "qa")
    graph.add_edge("qa", END)

    return graph.compile(
        checkpointer=SqliteSaver.from_conn_string("qa_checkpoints.db")
    )

# ========== Usage ==========
if __name__ == "__main__":
    app = create_qa_graph()

    result = app.invoke(
        {
            "question": "What is AGENTX?",
            "context": "AGENTX is a personal AI assistant framework...",
            "messages": []
        },
        config={"configurable": {"thread_id": "session_1"}}
    )

    print(f"Answer: {result['answer']}")
```

### Example 2: Multi-Step Research Agent with Tools

```python
import dspy
from typing import TypedDict, Annotated, Callable
from operator import add
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

# ========== Tools ==========
def search_web(query: str) -> str:
    """Search the web for information."""
    # Implementation (e.g., SearXNG, Tavily)
    return f"Search results for: {query}"

def search_database(query: str) -> str:
    """Search internal knowledge base."""
    # Implementation (e.g., Qdrant vector search)
    return f"DB results for: {query}"

def summarize(text: str) -> str:
    """Summarize text."""
    # Implementation (DSPy ChainOfThought)
    return f"Summary: {text[:100]}..."

tools = [search_web, search_database, summarize]

# ========== DSPy ReAct Agent ==========
research_agent = dspy.ReAct(
    signature="research_query -> findings",
    tools=tools,
    max_iters=10
)

# ========== LangGraph State ==========
class ResearchState(TypedDict):
    query: str
    findings: str
    sources: list[str]
    iteration: int
    max_iterations: int
    completed: bool
    messages: Annotated[list, add]

# ========== LangGraph Nodes ==========
def research_node(state: ResearchState) -> dict:
    """Research using DSPy ReAct agent."""
    if state["iteration"] >= state["max_iterations"]:
        return {"completed": True}

    result = research_agent(research_query=state["query"])

    return {
        "findings": result.findings,
        "sources": result.trajectory,  # Tool call history
        "iteration": state["iteration"] + 1,
        "messages": [{"role": "assistant", "content": result.findings}]
    }

def should_continue(state: ResearchState) -> str:
    """Conditional routing."""
    if state["completed"] or state["iteration"] >= state["max_iterations"]:
        return "end"
    return "continue"

# ========== Build Graph ==========
def create_research_graph():
    graph = StateGraph(ResearchState)
    graph.add_node("research", research_node)
    graph.add_edge(START, "research")

    # Conditional edge
    graph.add_conditional_edges(
        "research",
        should_continue,
        {
            "continue": "research",  # Loop back
            "end": END
        }
    )

    return graph.compile(
        checkpointer=SqliteSaver.from_conn_string("research_checkpoints.db")
    )

# ========== Usage ==========
if __name__ == "__main__":
    app = create_research_graph()

    result = app.invoke(
        {
            "query": "Latest developments in LLM agents",
            "findings": "",
            "sources": [],
            "iteration": 0,
            "max_iterations": 3,
            "completed": False,
            "messages": []
        },
        config={"configurable": {"thread_id": "research_1"}}
    )

    print(f"Findings: {result['findings']}")
    print(f"Sources: {result['sources']}")
```

### Example 3: Hybrid DSPy + LangGraph with Memory

```python
import dspy
from typing import TypedDict, Annotated
from operator import add
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from mem0 import Memory

# ========== Setup ==========
lm = dspy.LM("ollama_chat/gemma3:4b", api_base="http://localhost:11434")
dspy.configure(lm=lm)

memory = Memory.from_config({
    "provider": "qdrant",
    "config": {"host": "localhost", "port": 6333}
})

# ========== DSPy Modules ==========
class MemoryRetrievalSignature(dspy.Signature):
    """Retrieve relevant memories."""
    query = dspy.InputField()
    user_context = dspy.InputField()
    relevant_memories = dspy.OutputField()

class MemoryQASignature(dspy.Signature):
    """Answer with memory context."""
    question = dspy.InputField()
    memories = dspy.InputField()
    answer = dspy.OutputField()

class MemoryRetrievalModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.retrieve = dspy.Predict(MemoryRetrievalSignature)

    def forward(self, query: str, user_context: str):
        return self.retrieve(query=query, user_context=user_context)

class MemoryQAModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.answer = dspy.ChainOfThought(MemoryQASignature)

    def forward(self, question: str, memories: str):
        return self.answer(question=question, memories=memories)

retrieval_module = MemoryRetrievalModule()
qa_module = MemoryQAModule()

# ========== LangGraph State ==========
class MemoryState(TypedDict):
    question: str
    user_id: str
    user_context: str
    retrieved_memories: str
    answer: str
    messages: Annotated[list, add]

# ========== Nodes ==========
def retrieve_memory_node(state: MemoryState) -> dict:
    """Retrieve relevant memories from Mem0AI."""

    # Search vector store
    memories = memory.search(
        query=state["question"],
        user_id=state["user_id"],
        limit=5
    )

    # Format for DSPy
    memory_context = "\n".join([m["memory"] for m in memories])

    # Optional: Use DSPy to rank/reformat memories
    dspy_result = retrieval_module(
        query=state["question"],
        user_context=state["user_context"]
    )

    return {
        "retrieved_memories": memory_context,
        "messages": [{"role": "system", "content": f"Memories: {memory_context}"}]
    }

def answer_with_memory_node(state: MemoryState) -> dict:
    """Answer question using memory context."""

    result = qa_module(
        question=state["question"],
        memories=state["retrieved_memories"]
    )

    # Store interaction in memory
    memory.add(
        memory=f"Q: {state['question']}\nA: {result.answer}",
        user_id=state["user_id"],
        metadata={"type": "qa_interaction"}
    )

    return {
        "answer": result.answer,
        "messages": [{"role": "assistant", "content": result.answer}]
    }

# ========== Build Graph ==========
def create_memory_graph():
    graph = StateGraph(MemoryState)
    graph.add_node("retrieve", retrieve_memory_node)
    graph.add_node("answer", answer_with_memory_node)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "answer")
    graph.add_edge("answer", END)

    return graph.compile(
        checkpointer=SqliteSaver.from_conn_string("memory_checkpoints.db")
    )

# ========== Usage ==========
if __name__ == "__main__":
    app = create_memory_graph()

    result = app.invoke(
        {
            "question": "What did I work on yesterday?",
            "user_id": "user_123",
            "user_context": "Software developer working on AGENTX",
            "retrieved_memories": "",
            "messages": []
        },
        config={"configurable": {"thread_id": "conv_1"}}
    )

    print(f"Answer: {result['answer']}")
```

---

## Best Practices

### 1. Separation of Concerns

```python
# ✅ GOOD: Clear separation
# LangGraph handles orchestration
def orchestrate_node(state):
    # Route to appropriate DSPy module based on state
    if state["task_type"] == "qa":
        result = qa_module(question=state["question"])
    elif state["task_type"] == "research":
        result = research_module(query=state["query"])
    return {"result": result}

# ❌ BAD: Mixing concerns
def mixed_node(state):
    # Don't put orchestration logic inside DSPy modules
    # Don't put DSPy optimization logic in LangGraph nodes
    pass
```

### 2. Module Reuse

```python
# ✅ GOOD: Reuse DSPy module instances
class GraphComponents:
    """Container for reusable DSPy modules."""

    def __init__(self):
        self.qa_module = QAModule()
        self.react_agent = dspy.ReAct("query -> answer", tools=tools)
        self.summarizer = SummarizerModule()

    def get_qa_module(self):
        return self.qa_module

    def get_react_agent(self):
        return self.react_agent

components = GraphComponents()

def qa_node(state):
    result = components.get_qa_module()(question=state["question"])
    return {"answer": result.answer}

# ❌ BAD: Creating new module instances per call
def qa_node_bad(state):
    # This defeats the purpose of DSPy's optimization
    qa = QAModule()  # New instance each time
    result = qa(question=state["question"])
    return {"answer": result.answer}
```

### 3. State Schema Design

```python
# ✅ GOOD: Explicit, type-safe state
from pydantic import BaseModel, Field

class AgentState(BaseModel):
    """Type-safe state with validation."""
    question: str = Field(..., min_length=1)
    answer: str = Field(default="")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    tool_calls: list[dict] = Field(default_factory=list)

# ❌ BAD: Untyped, implicit state
class AgentStateBad(TypedDict):
    question: any  # No type checking
    answer: any
    data: dict  # Vague, unclear structure
```

### 4. Error Handling

```python
# ✅ GOOD: Explicit error handling in nodes
def robust_dspy_node(state: GraphState) -> dict:
    try:
        result = dspy_module(input=state["input"])
        return {"output": result.output, "error": None}
    except Exception as e:
        logger.error(f"DSPy module error: {e}")
        return {
            "output": None,
            "error": str(e),
            "messages": [{"role": "system", "content": f"Error: {e}"}]
        }

# ✅ GOOD: Use LangGraph's retry mechanisms
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def dspy_node_with_retry(state: GraphState) -> dict:
    result = dspy_module(input=state["input"])
    return {"output": result.output}
```

### 5. Observability

```python
# ✅ GOOD: Instrument both DSPy and LangGraph
import time

def instrumented_dspy_node(state: GraphState) -> dict:
    start_time = time.time()

    # Log input
    logger.info(f"[DSPy] Input: {state['input']}")

    # Call DSPy module
    result = dspy_module(input=state["input"])

    # Log output and timing
    duration = time.time() - start_time
    logger.info(f"[DSPy] Output: {result.output} (took {duration:.2f}s)")

    return {
        "output": result.output,
        "metrics": {"dspy_duration": duration}
    }

# Enable DSPy tracing
dspy.configure(settings=dict(trace_enabled=True))
```

### 6. Checkpointing Strategy

```python
# ✅ GOOD: Production-ready checkpointing
from langgraph.checkpoint.postgres import PostgresSaver

# Use PostgreSQL for durability
checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:pass@localhost:5432/langgraph"
)

app = graph.compile(checkpointer=checkpointer)

# ✅ GOOD: Selective persistence
class StateWithSelectivePersistence(TypedDict):
    question: str  # Transient, not checkpointed
    answer: str    # Checkpointed
    large_data: str  # Use selective memory for large data

# ❌ BAD: In-memory for production
checkpointer = MemorySaver()  # Lost on restart
```

### 7. Tool Organization

```python
# ✅ GOOD: Organized tool registry
class ToolRegistry:
    """Centralized tool management."""

    def __init__(self):
        self._registry = {
            "search": {
                "func": search_web,
                "scope": "public",
                "rate_limit": 100
            },
            "admin": {
                "func": admin_function,
                "scope": "admin",
                "rate_limit": 10
            }
        }

    def get_tools_by_scope(self, scope: str) -> list[Callable]:
        return [
            t["func"] for t in self._registry.values()
            if t["scope"] == scope or t["scope"] == "public"
        ]

# Use scoped tools
registry = ToolRegistry()
public_agent = dspy.ReAct(
    "query -> answer",
    tools=registry.get_tools_by_scope("public")
)
```

### 8. Testing

```python
# ✅ GOOD: Unit test DSPy modules independently
def test_qa_module():
    module = QAModule()
    result = module(context="Test context", question="Test question")
    assert result.answer is not None
    assert len(result.answer) > 0

# ✅ GOOD: Unit test LangGraph nodes independently
def test_qa_node():
    state = {
        "context": "Test",
        "question": "What is test?",
        "messages": []
    }
    result = qa_node(state)
    assert "answer" in result
    assert result["answer"] is not None

# ✅ GOOD: Integration test for full graph
def test_qa_graph():
    app = create_qa_graph()
    result = app.invoke(
        {"question": "Test?", "context": "Context", "messages": []},
        config={"configurable": {"thread_id": "test_1"}}
    )
    assert result["answer"] is not None
```

---

## Advanced Patterns

### 1. Parallel DSPy Execution in LangGraph

```python
from langgraph.graph import Send

# ========== State ==========
class ParallelState(TypedDict):
    questions: list[str]
    answers: list[str]
    completed: int

# ========== Parallel Node ==========
def parallel_qa_node(state: ParallelState) -> dict:
    """Process multiple questions in parallel using DSPy."""
    results = []

    for question in state["questions"]:
        result = qa_module(context="...", question=question)
        results.append(result.answer)

    return {
        "answers": results,
        "completed": len(results)
    }

# ========== Build Graph ==========
graph = StateGraph(ParallelState)
graph.add_node("parallel_qa", parallel_qa_node)
graph.add_edge(START, "parallel_qa")
graph.add_edge("parallel_qa", END)

app = graph.compile()
```

### 2. Hierarchical Agents

```python
# ========== Manager Agent ==========
manager_agent = dspy.ReAct(
    "task -> delegation",
    tools=[
        lambda task: f"Delegate to research: {task}",
        lambda task: f"Delegate to qa: {task}",
        lambda task: f"Delegate to summary: {task}"
    ]
)

# ========== Worker Agents ==========
research_agent = dspy.ReAct("research_query -> findings", tools=[search_web])
qa_agent = dspy.ReAct("question -> answer", tools=[search_db])
summary_agent = dspy.ChainOfThought("text -> summary")

# ========== LangGraph Orchestration ==========
def manager_node(state: dict) -> dict:
    result = manager_agent(task=state["task"])
    return {"delegation": result.delegation}

def route_to_worker(state: dict) -> str:
    if "research" in state["delegation"]:
        return "research"
    elif "qa" in state["delegation"]:
        return "qa"
    else:
        return "summary"

def research_worker_node(state: dict) -> dict:
    result = research_agent(research_query=state["task"])
    return {"result": result.findings}
```

### 3. Streaming DSPy Outputs in LangGraph

```python
from dspy.streaming import streamify

# ========== Stream DSPy Module ==========
streaming_qa = streamify(qa_module)

# ========== LangGraph Node with Streaming ==========
async def streaming_qa_node(state: GraphState) -> dict:
    """Stream DSPy outputs through LangGraph."""

    answer_chunks = []

    async for chunk in streaming_qa(context=state["context"], question=state["question"]):
        answer_chunks.append(chunk)
        # Can yield intermediate state updates
        # yield {"partial_answer": chunk}

    return {"answer": "".join(answer_chunks)}

# ========== Usage ==========
async for chunk in app.stream({"question": "What is...", "context": "..."}):
    print(chunk)  # Stream intermediate results
```

---

## Troubleshooting

### Common Issues

1. **DSPy Module Not Found**
   - Ensure DSPy is installed: `uv pip install dspy-ai`
   - Check LM configuration: `dspy.LM("ollama_chat/gemma3:4b")`

2. **Tool Execution Failures**
   - Verify tools are callable (have `__call__` method)
   - Check tool signatures match expected parameters
   - Use `dspy.Tool()` wrapper for plain functions

3. **State Not Persisting**
   - Ensure checkpointer is configured: `checkpointer=SqliteSaver(...)`
   - Use thread_id in config: `config={"configurable": {"thread_id": "123"}}`
   - Verify database connection for durable checkpointers

4. **Async/Sync Mismatch**
   - Use `acall()` for async DSPy modules
   - Use `await` in async LangGraph nodes
   - Enable `allow_tool_async_sync_conversion=True` if needed

5. **Memory Not Retrieved**
   - Verify Mem0AI/Qdrant connection
   - Check user_id is passed correctly
   - Ensure vectors are embedded before search

---

## References

### Official Documentation

- [DSPy GitHub Repository](https://github.com/stanfordnlp/dspy)
- [DSPy Official Website](https://dspy.ai/)
- [DSPy Tools Documentation](https://dspy.ai/tutorials/tools/) (local: `/home/riju279/Downloads/dspy-main/dspy-main/docs/docs/learn/programming/tools.md`)
- [DSPy ReAct Module API](https://dspy.ai/api/modules/ReAct/) (local: `/home/riju279/Downloads/dspy-main/dspy-main/docs/docs/api/modules/ReAct.md`)
- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)

### Integration Resources

- [LangGraph + DSPy + GEPA: Agentic Researcher](https://rajapatnaik.com/blog/2025/10/23/langgraph-dspy-gepa-researcher)
- [DSPy, De-Risked: A Practical Guide](https://www.cohorte.co/blog/dspy-de-risked-a-practical-guide-to-llm-system-programming-auto-optimisation)
- [LangGraph & DSPy: Orchestrating Multi-Agent AI Workflows](https://medium.com/@akankshasinha247/langgraph-dspy-orchestrating-multi-agent-ai-workflows-declarative-prompting-93b2bd06e995)
- [Best AI Agent Frameworks in 2025: Comparing LangGraph, DSPy](https://langwatch.ai/blog/best-ai-agent-frameworks-in-2025-comparing-langgraph-dspy-crewai-agno-and-more)

### Community Examples

- [LangGraphDSPyCourse GitHub](https://github.com/Ronoh4/LangGraphDSPyCourse)
- [DSPy Examples Repository](https://github.com/mbakgun/dspy-examples)
- [LangGraph ReAct Agent Template](https://github.com/langchain-ai/react-agent)

### Tutorials

- [Udemy: LangGraph & DSPy - Build Smarter Controllable AI Agents](https://www.udemy.com/course/langgraph-dspy-build-smarter-controllable-ai-agents-with-tools/)
- [Building AI Agents with DSPy Tutorial](https://dspy.ai/tutorials/customer_service_agent/)

### Security & Best Practices

- [Securing DSPy's MCP Integration](https://medium.com/@richardhightower/securing-dspys-mcp-integration-programmatic-ai-meets-enterprise-security-1eb742bbe69a)
- [Mastering LangGraph Checkpointing](https://sparkco.ai/blog/mastering-langgraph-checkpointing-best-practices-for-2025)

### Observability & Tracing

- [Langfuse LangGraph Integration Guide](https://langfuse.com/guides/cookbook/integration_langgraph)
- [DSPy Trace ID Mapping Discussion](https://github.com/langfuse/discussions/3553)

---

## Appendix: Quick Reference

### DSPy Module Patterns

```python
# Simple ChainOfThought
cot = dspy.ChainOfThought("question -> answer")
result = cot(question="What is...")

# ReAct with Tools
react = dspy.ReAct("query -> answer", tools=[tool1, tool2], max_iters=10)
result = react(query="Search for...")

# Custom Module
class MyModule(dspy.Module):
    def forward(self, input_field):
        return self.predictor(input_field=input_field)
```

### LangGraph Node Patterns

```python
# Sync Node
def my_node(state: GraphState) -> dict:
    return {"key": "value"}

# Async Node
async def my_async_node(state: GraphState) -> dict:
    result = await some_async_operation()
    return {"key": result}

# Node with DSPy
def dspy_node(state: GraphState) -> dict:
    result = dspy_module(input=state["input"])
    return {"output": result.output}
```

### State Schema Patterns

```python
# TypedDict
from typing import TypedDict, Annotated
from operator import add

class MyState(TypedDict):
    messages: Annotated[list, add]  # Append-only
    counter: Annotated[int, add]    # Increment

# Pydantic
from pydantic import BaseModel

class MyState(BaseModel):
    messages: list = []
    counter: int = 0
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-04  
**Maintained By:** AGENTX Research Team

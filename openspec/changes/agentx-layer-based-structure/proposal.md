# Proposal: AGENTX Layer-Based Folder Structure

## Why

The `agentx/` directory currently lacks clear organization conventions for where code should live as the codebase expands. Without established folder structure rules, the project will face:
- Unclear placement of DSPy signatures, modules, agents, and tools
- Mixed concerns (API models alongside DSPy models)
- No clear place for LangGraph graphs, routing, and mutation logic
- No clear expansion strategy as new agents and features are added
- Difficulty locating code as the codebase grows

**Why now:** The research phase (stem cell agent architecture, ColBERTv2, Mem0AI patterns, LangGraph integration) is complete. We need to establish folder structure conventions before implementing specialized agents and dynamic graph orchestration.

## What Changes

**Establish folder structure conventions and placement rules:**

- Define where DSPy signatures, modules, agents, and tools live
- Define where LangGraph graphs, routing, and mutation logic live
- Define where Pydantic models live (separate DSPy models from API models)
- Define where STT/TTS clients and other external services live
- Define API router and endpoint organization
- Define central configuration and lifespan management
- Define codebase expansion and differentiation algorithm

**BREAKING:** Current `main.py` imports will need updating to use new folder structure

## Capabilities

### New Capabilities

- `folder-structure-conventions`: Clear rules for where code belongs
- `codebase-expansion-algorithm`: Step-by-step process for adding new agents/features
- `differentiation-pattern`: How stem cell agents differentiate into specialized types

### Modified Capabilities

None (this establishes conventions, not behavioral changes)

## Impact

**Affected code:**

- `agentx/main.py` - Imports will need updating to use new folder structure
- New folder structure under `agentx/` following conventions

**No API or dependency changes** - this is purely organizational

---

# Folder Structure Conventions

## Overview

```
agentx/
├── core/                          # Global configuration, singleton dependencies
│   ├── config.py                  # Pydantic Settings (all env vars)
│   ├── dependencies.py            # Global singletons (LM, RM, Mem0AI, etc.)
│   ├── middleware/                # FastAPI middleware (CORS, logging, etc.)
│   └── exceptions.py              # Global exception definitions
│
├── domain/                        # Business logic (no external dependencies)
│   ├── entities/                  # Core business entities (@dataclass)
│   │   ├── graph.py               # Graph entity (ID, spec, metadata, score)
│   │   ├── mutation.py            # Mutation entity (type, target, params)
│   │   └── execution.py           # Execution entity (session, trace, result)
│   ├── signatures/                # DSPy signatures (reusable input/output contracts)
│   ├── services/                  # Domain services (business logic, stateless)
│   └── value_objects/             # Immutable value objects
│
├── application/
│   ├── agents/                    # DSPy agents (stem cell + differentiated)
│   │   ├── stem_cell.py           # Base StemCellAgent class
│   │   ├── conversation.py        # Conversation agent
│   │   ├── researcher.py          # Research agent
│   │   ├── analyst.py             # Analyst agent
│   │   └── ...                    # Other specialized agents
│   │
│   ├── graphs/                    # LangGraph graph definitions and builders
│   │   ├── builder/               # DSPy → LangGraph compiler
│   │   │   ├── graph_compiler.py  # JSON spec → StateGraph
│   │   │   └── node_factory.py     # Create DSPy nodes from agent registry
│   │   ├── routing/               # Dynamic routing logic
│   │   │   ├── router.py          # Route between graphs based on context
│   │   │   └── conditional.py     # Conditional edge logic
│   │   ├── mutation/              # Graph mutation operations
│   │   │   ├── add_node.py        # Add node to running graph
│   │   │   ├── remove_edge.py     # Remove edge from running graph
│   │   │   ├── modify_condition.py # Change routing condition
│   │   │   └── spawn_subgraph.py  # Create isolated subgraph
│   │   ├── storage/               # Graph persistence to Qdrant
│   │   │   ├── graph_store.py     # Save/load graphs to Qdrant
│   │   │   └── variation_store.py # Store genetic variations
│   │   └── presets/               # Predefined graph templates
│   │       ├── conversation_graph.py
│   │       ├── research_graph.py
│   │       └── ...
│   │
│   ├── evaluation/                # Critic and evaluator logic
│   │   ├── critic.py              # Evaluate graph execution quality
│   │   ├── metrics.py             # Quality metrics (latency, accuracy, etc.)
│   │   └── evaluator.py           # Compare graph variations
│   │
│   ├── coordination/              # Coordinator (continue/replan/mutate decisions)
│   │   └── coordinator.py         # Decide next action based on critic score
│   │
│   ├── tools/                     # DSPy tools (wrapped functions)
│   │   └── <domain>/              # Grouped by domain (e.g., web/, memory/)
│   ├── use_cases/                 # Use case facades (coordinate agents + services)
│   ├── models/                    # Pydantic models for DSPy (internal)
│   └── mappers/                   # Entity ↔ DTO converters
│
├── infrastructure/                # External concerns (DB, HTTP, storage)
│   ├── memory/                    # Memory system implementations
│   │   ├── mem0_client.py         # Mem0AI wrapper
│   │   ├── qdrant_rm.py           # Qdrant retriever with prefetch
│   │   ├── langgraph_store.py     # LangGraph checkpoint store (Redis)
│   │   └── graph_collection.py    # Qdrant collection for graph storage
│   ├── voice/                     # STT/TTS client libraries (using libs/voice_client/ SDK)
│   │   ├── voice_adapter.py       # VoiceSDKAdapter wrapping voice_client.VoiceClient
│   │   ├── voice_gateway.py       # WebSocket gateway service
│   │   └── text_stream_handler.py # STT buffering/TTS splitting
│   ├── retrieval/                 # RAG and search implementations
│   │   ├── prefetch_rm.py         # Prefetch wrapper (dense → ColBERT)
│   │   └── searxng_client.py      # SearXNG web search client
│   ├── repositories/              # Data access implementations
│   └── external/                  # External API clients
│
├── presentation/                  # FastAPI interface
│   ├── api/
│   │   └── v1/
│   │       ├── agents/            # Agent-related endpoints
│   │       │   ├── __init__.py
│   │       │   └── routes.py       # All agent endpoints in one file
│   │       ├── graphs/            # Graph management endpoints
│   │       │   ├── __init__.py
│   │       │   └── routes.py       # Graph CRUD, execution endpoints
│   │       ├── memory/            # Memory-related endpoints
│   │       ├── voice/             # Voice WebSocket endpoints
│   │       ├── threads/           # Thread management endpoints
│   │       └── websocket/         # Real-time WebSocket endpoints
│   ├── models/                    # Pydantic models for API (request/response)
│   │   ├── requests.py            # Request DTOs
│   │   └── responses.py           # Response DTOs
│   └── middleware/                # Additional API middleware
│
└── main.py                        # Application entry point (FastAPI factory)
```

## Placement Rules

### Graph Entities (`domain/entities/`)

**Purpose:** Core business entities for graph lifecycle

**When to create:** When you need a data structure for graphs, mutations, or executions

**Pattern:**
```python
# domain/entities/graph.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Graph:
    """Represents a LangGraph StateGraph specification."""
    id: str
    spec: dict  # JSON graph spec
    metadata: dict
    score: float  # Quality score from critic
    created_at: datetime
    version: int
```

### Graph Builders (`application/graphs/builder/`)

**Purpose:** DSPy → LangGraph compilation logic

**When to create:** When adding new graph compilation patterns

**Pattern:**
```python
# application/graphs/builder/graph_compiler.py
from langgraph.graph import StateGraph

class GraphCompiler:
    """Compile DSPy agent registry into LangGraph StateGraph."""

    def compile(self, agents: dict, edges: list) -> StateGraph:
        """Build StateGraph from agent registry and edge definitions."""
        graph = StateGraph()
        # Add nodes from agents
        # Add edges from routing logic
        return graph.compile()
```

### Graph Routing (`application/graphs/routing/`)

**Purpose:** Dynamic routing logic between graphs

**When to create:** When adding new routing strategies

**Pattern:**
```python
# application/graphs/routing/router.py
from agentx.domain.entities import Graph, Execution

class Router:
    """Route between graphs based on execution context."""

    def select_graph(self, query: str, context: dict) -> Graph:
        """Select best graph for this query."""
        # Query Qdrant for similar past graphs
        # Return best matching graph
```

### Graph Mutation (`application/graphs/mutation/`)

**Purpose:** Self-modifying graph operations

**When to create:** When adding new mutation types

**Pattern:**
```python
# application/graphs/mutation/add_node.py
from langgraph.graph import StateGraph

def add_node(graph: StateGraph, node_id: str, agent: str) -> StateGraph:
    """Add a new node to the running graph."""
    graph.add_node(node_id, agent)
    return graph
```

### Graph Storage (`application/graphs/storage/`)

**Purpose:** Persist graphs and variations to Qdrant

**When to create:** When implementing graph persistence

**Pattern:**
```python
# application/graphs/storage/graph_store.py
from agentx.domain.entities import Graph

class GraphStore:
    """Store and retrieve graphs from Qdrant."""

    def save_graph(self, graph: Graph) -> str:
        """Save graph to Qdrant for future retrieval."""
        # Vectorize graph spec and store

    def find_similar(self, query: str, k: int = 5) -> list[Graph]:
        """Find similar graphs for this query."""
        # Qdrant search for similar graph specs
```

### Graph Presets (`application/graphs/presets/`)

**Purpose:** Predefined graph templates for common patterns

**When to create:** When you have a reusable graph pattern

**Pattern:**
```python
# application/graphs/presets/conversation_graph.py
from langgraph.graph import StateGraph

def build_conversation_graph() -> StateGraph:
    """Build preset graph for conversation flow."""
    graph = StateGraph()
    # Add nodes: analyst, researcher, presenter
    # Add edges with routing logic
    return graph.compile()
```

### Evaluation/Critic (`application/evaluation/`)

**Purpose:** Evaluate graph execution quality

**When to create:** When adding new quality metrics

**Pattern:**
```python
# application/evaluation/critic.py
from agentx.domain.entities import Execution

class Critic:
    """Evaluate graph execution and produce quality score."""

    def evaluate(self, execution: Execution) -> float:
        """Score execution quality (0.0 to 1.0)."""
        # Check latency, accuracy, tool success rate
        return score
```

### Coordinator (`application/coordination/`)

**Purpose:** Decide continue/replan/mutate based on critic score

**When to create:** When implementing coordination logic

**Pattern:**
```python
# application/coordination/coordinator.py
from agentx.application.evaluation.critic import Critic

class Coordinator:
    """Decide next action based on critic evaluation."""

    def decide(self, execution: Execution, critic: Critic) -> str:
        """Return: 'continue', 'replan', or 'mutate'."""
        score = critic.evaluate(execution)
        if score > 0.8:
            return "continue"
        elif score > 0.5:
            return "replan"
        else:
            return "mutate"
```

### DSPy Signatures (`domain/signatures/`)

**Purpose:** Reusable DSPy signatures (input/output contracts)

**When to create:** When you have a reusable input/output pattern that multiple agents can use

**Example:**
```python
# domain/signatures/analysis.py
import dspy

class AnalysisSignature(dspy.Signature):
    """Signature for query analysis tasks."""
    query: str = dspy.InputField()
    context: str = dspy.InputField()

    goals: list[str] = dspy.OutputField()
    confidence: float = dspy.OutputField()
```

**Naming:** `{purpose}_signature.py` or group related signatures in one file

### DSPy Agents (`application/agents/`)

**Purpose:** DSPy agent implementations (stem cell + differentiated agents)

**When to create:** When you need a new agent type

**Pattern:**
```python
# application/agents/researcher.py
from agentx.domain.signatures.search import SearchSignature
from agentx.application.agents.stem_cell import StemCellAgent

class ResearcherAgent(StemCellAgent):
    """Research agent - differentiated stem cell."""

    def __init__(self, searxng_url: str):
        research_signature = dspy.Signature(
            "query, context -> answer, reasoning, citations",
            instructions="Research using available tools and cite sources."
        )
        super().__init__(signature=research_signature, enable_tools=True)

        # Add tools...
```

**Naming:** `{agent_type}.py` (lowercase, underscore-separated)

### DSPy Tools (`application/tools/<domain>/`)

**Purpose:** Wrapped functions that agents can call

**When to create:** When you have a function an agent needs to use

**Pattern:**
```python
# application/tools/web/search.py
from dspy import Tool

def searxng_search(query: str) -> str:
    """Search SearXNG and return results."""
    # Implementation...

# Create tool wrapper
searxng_search_tool = Tool(searxng_search, name="searxng_search")
```

**Organization:** Group by domain (web/, memory/, analysis/, etc.)

### Pydantic Models

**DSPy Models** (`application/models/`): Internal DSPy data structures
**API Models** (`presentation/models/`): Request/response DTOs for FastAPI

**Why separate:** DSPy models may change frequently; API models are public contract

### STT/TTS Clients (`infrastructure/voice/`)

**Purpose:** External voice service client libraries and adapters

**When to create:** When integrating a new STT/TTS service

**Existing SDK:** Use `libs/voice_client/` SDK for Kyutai integration

**Pattern:**
```python
# infrastructure/voice/voice_adapter.py
from voice_client import VoiceClient, ConversationEvent

class VoiceSDKAdapter:
    """Thin wrapper around voice_client SDK for AGENTX integration."""

    def __init__(self, stt_url: str, tts_url: str):
        self.stt_url = stt_url
        self.tts_url = tts_url

    async def handle_session(self, websocket, session_id: str, agent_callback):
        """Handle voice session using SDK's VoiceClient.converse_stream()."""
        async with VoiceClient(stt_url=self.stt_url, tts_url=self.tts_url) as voice:
            async for event in voice.converse_stream(audio_input, agent_callback):
                await websocket.send_json({"type": event.type, "data": event.data})
```

### API Routes (`presentation/api/v1/<domain>/routes.py`)

**Purpose:** FastAPI endpoint definitions

**When to create:** When adding new API endpoints

**Pattern:**
```python
# presentation/api/v1/agents/routes.py
from fastapi import APIRouter, Depends
from agentx.presentation.models.requests import AgentRequest
from agentx.presentation.models.responses import AgentResponse

router = APIRouter()

@router.post("/execute", response_model=AgentResponse)
async def execute_agent(request: AgentRequest):
    # Implementation...
```

**Organization:** One `routes.py` file per domain (agents, memory, voice, etc.)

### Central Configuration (`core/config.py`)

**Purpose:** Pydantic Settings for all environment variables

**Pattern:**
```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # All env vars here, grouped by domain

    # Server
    host: str = "0.0.0.0"
    port: int = 8015

    # LLM
    llm_provider: str = "ollama"
    llm_model: str = "gemma3:4b"

    # Voice
    voice_kyutati_stt_url: str = "ws://localhost:16000/stt"

    class Config:
        env_file = ".env"

settings = Settings()  # Singleton
```

### Lifespan Management (`main.py`)

**Purpose:** Application startup/shutdown hooks

**Pattern:**
```python
# main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    from agentx.core.dependencies import ensure_dspy_configured
    ensure_dspy_configured()

    # Initialize clients
    from agentx.infrastructure.voice.kyutai_client import KyutaiClient
    # ... initialization ...

    yield

    # Shutdown
    # ... cleanup ...
```

---

# Codebase Expansion Algorithm

## Adding a New Agent Type

1. **Create signature** (if new pattern needed) in `domain/signatures/{agent}_signature.py`
2. **Create agent** in `application/agents/{agent}.py` extending `StemCellAgent`
3. **Add tools** (if needed) in `application/tools/<domain>/`
4. **Create use case** (if orchestration needed) in `application/use_cases/{operation}.py`
5. **Add routes** (if API needed) in `presentation/api/v1/agents/routes.py`
6. **Add DTOs** (if API needed) in `presentation/models/{requests,responses}.py`

## Adding a New Tool

1. **Implement function** in `application/tools/<domain>/{tool}.py`
2. **Wrap with dspy.Tool** and export as `{tool_name}_tool`
3. **Register** in agent's `__init__` via `self.add_tool()`

## Adding External Service Integration

1. **Create client** in `infrastructure/<category>/{service}_client.py`
2. **Add config** to `core/config.py` (URLs, API keys)
3. **Add lifespan init** in `main.py` if connection pooling needed
4. **Create wrapper** in `application/tools/` if agents need to use it

---

# Differentiation Algorithm (Stem Cell Pattern)

## Core Principle

Start with `StemCellAgent` (pluripotent, minimal) and differentiate via:
1. **Signature change** - Most common: custom signature for specialized behavior
2. **Module overexpression** - Add DSPy modules/tools to stem cell
3. **Subclassing** - Create permanent differentiated cell type

## Pattern

```python
# 1. Start with stem cell (in application/agents/stem_cell.py)
class StemCellAgent(dspy.Module):
    def __init__(self, user_id: str, signature: Optional[dspy.Signature] = None):
        # Default pluripotent signature
        if signature is None:
            self.signature = dspy.Signature("context, question -> answer, reasoning")
        else:
            self.signature = signature
        self.reasoning = dspy.ChainOfThought(self.signature)
        # ... memory hooks, tool mounts ...

# 2. Differentiate via signature (in application/agents/analyst.py)
class AnalystAgent(StemCellAgent):
    def __init__(self):
        analyst_signature = dspy.Signature(
            "query, memory_context, knowledge_context -> "
            "context_summary, goals, is_sufficient, confidence"
        )
        super().__init__(signature=analyst_signature)

        # Overexpress: Add specialized modules
        self.data_judgment = dspy.ChainOfThought("query, data -> judgment")

# 3. All agents use global DSPy LM/RM + per-agent Mem0AI
# (No per-agent RM injection - DSPy handles this centrally)
```

## File Size Limits

- Max **100 lines** of executable code per file
- Max **50 lines** of overhead (imports, comments)
- Split files that exceed limits (use submodules)

## Import Rules (CLAUDE_POLICY.md)

- **ABSOLUTE IMPORTS ONLY** - No `from .` or `from ..`
- **Architectural boundaries** respected (domain imports from domain only, etc.)
- Passes `ruff check --fix` and `ruff format`

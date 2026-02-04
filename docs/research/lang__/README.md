# DSPy + LangGraph/DeepAgents Research Index

**Research Date:** 2025-02-04
**Goal:** Investigate hybrid architecture where DSPy handles agent internals and LangGraph handles orchestration

---

## Research Summary

This directory contains comprehensive research on integrating DSPy (for agent internals, signatures, modules, tools, ReAct agents with memory, GEPA training) with LangGraph/DeepAgents (for looping, routing, dynamic assembly of agent pipelines).

### Architecture Vision

```
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Layer                          │
│  (State Management, Routing, Orchestration, Checkpointing)  │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
┌────────────┐ ┌──────────┐ ┌──────────┐
│ DSPy Agent │ │ DSPy     │ │ DSPy     │
│  ReAct     │ │ Module   │ │ Retrieve │
│  + Mem0AI  │ │          │ │ (RAG)    │
└────────────┘ └──────────┘ └──────────┘
     │              │              │
     └──────────────┴──────────────┘
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
┌─────────────────┐  ┌─────────────────┐
│  Ollama LLM     │  │  GEPA Optimizer │
│  (gemma3:4b)    │  │  (Training)     │
└─────────────────┘  └─────────────────┘
```

### Key Principles

1. **DSPy Layer** (Agent Internals):
   - Signatures define input/output contracts
   - Modules encapsulate reasoning logic
   - Tools provide capabilities
   - ReAct agents with Mem0AI memory
   - GEPA optimizes prompts
   - `dspy.retrieve` for RAG

2. **LangGraph Layer** (Orchestration):
   - StateGraph manages conversation state
   - Conditional edges route between agents
   - Command objects for dynamic decisions
   - Checkpointing for persistence
   - Async streaming for user-facing agents

3. **Ollama Integration**:
   - Local LLM backend (`gemma3:4b`, `llama3.1`)
   - Structured outputs via JSON schema
   - No Pydantic serialization warnings

---

## Research Documents

| # | Document | Topics Covered |
|---|----------|----------------|
| 01 | [LangGraph Core Concepts](./01_langgraph_core_concepts.md) | StateGraph, nodes, edges, message passing, conditional routing, recursion limits |
| 02 | [DeepAgents Architecture](./02_deepagents_architecture.md) | Multi-agent orchestration, supervisor pattern, subgraphs, LangGraph Agent Protocol |
| 03 | [Ollama LangChain Integration](./03_ollama_langchain_integration.md) | ChatOllama config, async patterns, streaming, Pydantic issues |
| 04 | [Async Streaming Patterns](./04_async_streaming_patterns.md) | astream(), astream_events(), StreamWriter, streaming nodes |
| 05 | [Multi-Agent Routing](./05_multiagent_routing.md) | Conditional routing, supervisor pattern, dynamic assembly, subgraphs |
| 06 | [DSPy LangGraph Integration](./06_dspy_langgraph_integration.md) | Wrapping DSPy modules, signature conversion, tool integration |
| 07 | [Memory Management](./07_memory_management.md) | Mem0AI + LangGraph, conversation history, state synchronization |
| 08 | [GEPA LangGraph Training](./08_gepa_langgraph_training.md) | Separation of concerns, collecting training data, hot-swapping agents |
| 09 | [Pydantic Ollama Fixes](./09_pydantic_ollama_fixes.md) | Serialization errors, structured outputs, schema simplification |
| 10 | [DSPy Retrieve RAG](./10_dspy_retrieve_rag.md) | dspy.retrieve, Qdrant, ColBERTv2, hybrid RAG patterns |

---

## Quick Reference: AGENTX Architecture

### Agent Specifications

| Agent | Type | Streaming | Async | Purpose |
|-------|------|-----------|-------|---------|
| **Conversation Agent** | DSPy ReAct | ✅ Yes (tokens) | ✅ Yes | User-facing: STT/TTS/text |
| **RAG Agent** | DSPy Retrieve | ❌ No | ✅ Yes | Document QA |
| **Code Agent** | DSPy Module | ❌ No | ✅ Yes | Code generation |
| **Vision Agent** | DSPy MultiModal | ❌ No | ✅ Yes | Image understanding |
| **Analytics Agent** | DSPy Module | ❌ No | Sync | Data analysis |

### Layer Responsibilities

**DSPy Layer (Trainable):**
```python
# DSPy agent definition
class ConversationAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.react = dspy.ReAct(
            "question->answer",
            tools=[search_tool, calculator_tool],
            num_retries=3
        )

    def forward(self, question):
        return self.react(question=question)
```

**LangGraph Layer (Orchestration):**
```python
# LangGraph wraps DSPy agent
from langgraph.graph import StateGraph
from langgraph.types import Command

def conversation_node(state: AgentState) -> Command:
    result = dspy_agent(question=state["current_input"])
    # Dynamic routing based on intent
    if result.requires_search:
        return Command(
            update={"messages": [result.answer]},
            goto="search_agent"
        )
    return Command(goto=END)
```

### Memory Architecture

```python
# Three-tier memory system

# 1. LangGraph Checkpointing (conversation-level)
from langgraph.checkpoint.sqlite import SqliteSaver
checkpointer = SqliteSaver.from_conn_string("agentx.db")

# 2. Mem0AI (long-term episodic memory)
from mem0 import Memory
mem0_client = Memory()

# 3. DSPy ReAct (short-term working memory)
dspy.configure(
    lm=ollama_lm,
    rm=mem0_retriever  # RAG memory
)
```

### Training Pipeline (GEPA)

```python
# Training is DSPy's responsibility
from dspy.teleprompt import BootstrapFewShotWithRandomSearch

# 1. Collect examples from LangGraph logs
examples = collect_training_data_from_logs()

# 2. Train DSPy agent
optimizer = BootstrapFewShotWithRandomSearch(
    metric=answer_match,
    max_bootstrapped_demos=5
)

trained_agent = optimizer.compile(
    ConversationAgent(),
    trainset=examples
)

# 3. Hot-swap in LangGraph (routing unchanged)
```

---

## Streaming Architecture

### User-Facing Agent (Async + Streaming)

```python
from langgraph.types import StreamWriter

async def streaming_conversation_node(
    state: AgentState,
    config: RunnableConfig,
    writer: StreamWriter
):
    """Stream tokens for real-time user feedback."""

    # Stream DSPy output
    async for token in dspy_agent.astream(
        question=state["current_input"],
        stream_listeners=[
            dspy.streaming.StreamListener("answer")
        ]
    ):
        # Write to WebSocket for TTS
        await writer({"token": token})

    return {"messages": [full_response]}
```

### Non-Streaming Agents (Async/Sync)

```python
# Simple async node
async def rag_node(state: AgentState):
    result = await dspy_retriever.acall(query=state["query"])
    return {"context": result.passages}

# Simple sync node
def analytics_node(state: AgentState):
    result = dspy_analytics(data=state["data"])
    return {"insights": result}
```

---

## Ollama Configuration

### DSPy Configuration (No Warnings)

```python
import dspy

# Configure DSPy with Ollama
ollama_lm = dspy.LM(
    "ollama_chat/gemma3:4b",
    api_base="http://localhost:11434",
    api_key="",
    temperature=0.7
)

dspy.configure(lm=ollama_lm)
```

### LangGraph Configuration (No Pydantic Errors)

```python
from langchain_ollama import ChatOllama

# For structured output, use manual JSON parsing
llm = ChatOllama(
    model="gemma3:4b",
    temperature=0,
    format="",  # Let Ollama handle natively
)

# Or use Ollama's format parameter
from ollama import chat
response = chat(
    messages=[...],
    model="llama3.1",
    format=MySchema.model_json_schema(),
)
```

### Schema Best Practices

```python
from pydantic import BaseModel

# Minimal schema for Ollama
class SimpleResponse(BaseModel):
    text: str
    confidence: float

# NO: Field constraints, validators, Optional[]
class BadResponse(BaseModel):
    text: str = Field(..., min_length=1)  # ✗ Constraints
    value: Optional[int] = None  # ✗ Use | instead
```

---

## Implementation Checklist

### Phase 1: Core Setup
- [ ] Install DSPy, LangGraph, Ollama dependencies
- [ ] Configure Ollama with gemma3:4b model
- [ ] Create base StateGraph schemas
- [ ] Set up checkpointing (SqliteSaver)
- [ ] Configure Mem0AI for long-term memory

### Phase 2: DSPy Agents
- [ ] Define DSPy signatures for each agent type
- [ ] Implement ReAct agents with tools
- [ ] Configure dspy.retrieve for RAG
- [ ] Set up Mem0AI integration
- [ ] Create GEPA training pipeline

### Phase 3: LangGraph Orchestration
- [ ] Wrap DSPy agents as LangGraph nodes
- [ ] Implement conditional routing
- [ ] Add supervisor pattern for multi-agent
- [ ] Configure Command-based routing
- [ ] Set up async streaming for conversation agent

### Phase 4: Training & Optimization
- [ ] Collect training data from LangGraph logs
- [ ] Train agents with GEPA
- [ ] Implement hot-swapping pattern
- [ ] Add A/B testing capability
- [ ] Set up continuous evaluation

### Phase 5: Production
- [ ] Add error handling and retries
- [ ] Implement circuit breakers
- [ ] Set up monitoring and tracing
- [ ] Configure production checkpointing
- [ ] Add health check endpoints

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| DSPy Ollama connection fails | Check `ollama serve` is running, use `ollama_chat/` prefix |
| Pydantic serialization error | Store IDs in state, not objects; use `default_factory` |
| Structured output fails | Simplify schema, use manual JSON parsing |
| Async tools don't stream | Use `StreamWriter` in node signature |
| Memory not persisting | Check `thread_id` in config, use SqliteSaver |
| GEPA training not working | Verify training data format, check metric function |
| LangGraph routing stuck | Add recursion limit, check for loops |
| STT/TTS integration issues | See `C010-voice-client` OpenSpec change |

---

## Key References

### Official Documentation
- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [DeepAgents Overview](https://docs.langchain.com/oss/python/deepagents/overview)
- [DSPy Documentation](https://dspy.ai/)
- [Ollama Structured Outputs](https://ollama.com/blog/structured-outputs)
- [Mem0AI LangGraph Integration](https://docs.mem0.ai/v0x/integrations/langgraph)

### DSPy Tutorials (Local)
- `/home/riju279/Downloads/dspy-main/dspy-main/docs/tutorials/`
  - `streaming/` - Token streaming patterns
  - `async/` - Async patterns
  - `tool_use/` - Tool integration
  - `agents/` - ReAct agent patterns
  - `mem0_react_agent/` - Memory integration

### AGENTX Project Docs
- `CLAUDE.md` - Project overview and patterns
- `docs/engineering/HLD.md` - High-level design
- `docs/engineering/schemas.md` - Data schemas
- `docs/research/` - Comprehensive research archive

---

## Next Steps

1. **Read Core Documents**: Start with docs 01, 03, 06, 07
2. **Review Examples**: Check DSPy tutorials for working patterns
3. **Prototype Simple Agent**: Build a basic DSPy + LangGraph integration
4. **Add Streaming**: Implement async streaming for conversation agent
5. **Train with GEPA**: Collect data and optimize DSPy agents
6. **Scale to Multi-Agent**: Add LangGraph routing for multiple specialized agents

---

**Research Completed**: 2025-02-04
**Total Lines**: ~8,600 across 10 documents
**Status**: Ready for implementation planning

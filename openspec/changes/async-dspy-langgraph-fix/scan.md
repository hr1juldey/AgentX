# Scan Artifact: async-dspy-langgraph-fix

**Generated**: 2026-02-01
**Change**: async-dspy-langgraph-fix
**Schema**: spec-factory v1.0.0

---

## 1. LLD Synthesis

### 1.1 Relevant LLD Documents

| Document | Path | Relevance |
|----------|------|-----------|
| Domain Model LLD | `docs/engineering/lld/domain_model.md` | Defines AgentSessionEntity, enums, repositories |
| Agent Runtime LLD | `docs/engineering/lld/agent_runtime.md` | Defines DSPy signatures, tools, agents, LangGraph state machines |
| Incremental Release Plan | `docs/engineering/lld/incremental_release_plan.md` | Defines phased implementation with frozen APIs |

### 1.2 Locked Definitions from LLD

#### Entities

**AgentSessionEntity** (`domain/entities/agent_session.py`):
- `session_id: UUID`
- `user_id: str` (SHA-256 hash)
- `state: SessionState`
- `current_reasoning_step: int`
- `total_tool_calls: int`
- Business methods: `is_active()`, `pause()`, `resume()`, `close()`, `increment_reasoning_step()`, `increment_tool_calls()`

#### Enums

**SessionState**: `INITIALIZING`, `ACTIVE`, `PAUSED`, `CLOSED`
**AgentStatus**: `IDLE`, `THINKING`, `USING_TOOL`, `COMPLETED`, `FAILED`

---

## 2. Documentation Sources Scanned

### 2.1 LangGraph Documentation

**Downloaded locally to**: `/home/riju279/Documents/Code/XRIG/AgentX/tests/`

| Document | Local Path | Lines | Key Takeaways for This Change |
|----------|------------|-------|------------------------------|
| Choosing APIs | `tests/langgraph_choosing_apis.md` | 322 | Functional API vs Graph API decision matrix |
| Graph API | `tests/langgraph_graph_api.md` | 723 | StateGraph, nodes, edges, state, reducers |
| Use Graph API | `tests/langgraph_use_graph_api.md` | 2174 | Complete Graph API reference with examples |
| Workflows and Agents | `tests/langgraph_workflows_agents.md` | 1113 | Agent patterns, orchestrator-worker, parallel execution, routing |
| Subgraphs | `tests/langgraph_subgraphs.md` | 475 | Multi-agent patterns, state sharing between parent/child graphs |
| Memory | `tests/langgraph_memory.md` | 1399 | Checkpointer patterns, persistence, thread-level memory |
| Time Travel | `tests/langgraph_time_travel.md` | 225 | State inspection, checkpoint history, resume from interrupt |

**Total LangGraph Documentation**: 6,431 lines across 7 documents

**Key LangGraph Patterns Discovered**:

1. **Parallel Node Execution**: Multiple nodes can receive input from START and execute concurrently
   ```python
   workflow.add_edge(START, "call_llm_1")
   workflow.add_edge(START, "call_llm_2")
   workflow.add_edge(START, "call_llm_3")
   # All three execute in parallel
   ```

2. **Orchestrator-Worker with Send API**: Dynamic worker creation
   ```python
   def assign_workers(state):
       return [Send("llm_call", {"section": s}) for s in state["sections"]]
   ```

3. **State Reducers**: Using `Annotated[list, operator.add]` for parallel accumulation
   ```python
   class WorkerState(TypedDict):
       completed_sections: Annotated[list, operator.add]  # Parallel writes
   ```

4. **Async Node Functions**: LangGraph supports async node functions natively
   ```python
   async def llm_call(state: MessagesState):
       response = await model.ainvoke(state["messages"])
       return {"messages": response}
   ```

### 2.2 DSPy Documentation

**Source**: `/home/riju279/Downloads/dspy-main/dspy-main/docs/docs/tutorials/async/index.md`

**Key DSPy Async Patterns**:

1. **acall() method**: All DSPy modules have async variant
   ```python
   output = await predict.acall(question="...")
   ```

2. **Custom aforward() method**: Implement for custom modules
   ```python
   class MyModule(dspy.Module):
       async def aforward(self, question, **kwargs):
           answer = await self.predict1.acall(question=question)
           return await self.predict2.acall(answer=answer)
   ```

3. **Async Tools**: Tools can be async functions
   ```python
   async def foo(x):
       await asyncio.sleep(0.1)
       return x * 2

   tool = dspy.Tool(foo)
   await tool.acall(x=5)
   ```

4. **ReAct with Async Tools**: ReAct.acall() executes all tools asynchronously

**DSPy Best Practices**:
- Start with sync for prototyping, switch to async for production
- Use async for high-QPS services, I/O-bound operations
- Be aware of: complex error handling, subtle bugs, code complexity

### 2.3 Test Reports

**Source**: `/home/riju279/Documents/Code/XRIG/AgentX/tests/reports/SUMMARY.md`

**Key Findings**:

| Model | Warmup | Per Query | Best Speedup | Concurrency |
|-------|--------|-----------|--------------|-------------|
| qwen3:8b | ~27s | ~3-4s | 1.20x @ 4 concurrent | ASYNC wins all levels |
| qwen2.5-coder:14b | ~278s | ~1-2s | 1.74x @ 1 concurrent | ASYNC wins at 1,4; SYNC at 2,8 |

**Critical Insights**:
1. Pre-warming is essential (3-5 queries)
2. Simple queries work better than complex instructions
3. Larger models are faster per query but longer warmup
4. Max 4 concurrent for optimal performance

---

## 3. Codebase File Inventory

### 3.1 Backend Files (To Modify)

| File | Lines | Purpose | Current Pattern |
|------|-------|---------|-----------------|
| `agentx/agent/nodes/analyst.py` | 188 | Analyst node - Pass 1 analysis, Pass 2 quality judgment | 4 sequential DSPy calls in Pass 1 |
| `agentx/agent/nodes/researcher.py` | 119 | Researcher node - Search executor, data structurer, citation builder | 4 sequential DSPy calls |
| `agentx/agent/nodes/designer.py` | 160 | Designer node - UI widget selection with state awareness | Multiple sequential DSPy calls |
| `agentx/agent/nodes/contextualizer.py` | 134 | Contextualizer node - Rerank, filter, inject context | Sequential DSPy calls |

### 3.2 DSPy Tool Modules (16 modules - need `aforward()`)

**Analyst Tools** (5 modules):
- `agentx/agent/tools/analyst/context_analyzer.py` (~50 lines)
- `agentx/agent/tools/analyst/data_quality_checker.py` (~40 lines)
- `agentx/agent/tools/analyst/goal_detector.py` (~40 lines)
- `agentx/agent/tools/analyst/insight_extractor.py` (~40 lines)
- `agentx/agent/tools/analyst/search_terms.py` (~40 lines)

**Researcher Tools** (5 modules):
- `agentx/agent/tools/researcher/search_executor.py` (~60 lines)
- `agentx/agent/tools/researcher/web_scraper.py` (~80 lines)
- `agentx/agent/tools/researcher/citation_builder.py` (~50 lines)
- `agentx/agent/tools/researcher/data_structurer.py` (~50 lines)
- `agentx/agent/tools/researcher/findings_beautifier.py` (~50 lines)

**Designer Tools** (3 modules):
- `agentx/agent/tools/designer/color_scheme.py` (~40 lines)
- `agentx/agent/tools/designer/hierarchy.py` (~40 lines)
- `agentx/agent/tools/designer/pov_generator.py` (~50 lines)

**Contextualizer Tools** (3 modules):
- `agentx/agent/tools/contextualizer/contextualizer.py` (~50 lines)
- `agentx/agent/tools/contextualizer/filter.py` (~40 lines)
- `agentx/agent/tools/contextualizer/reranker.py` (~50 lines)

### 3.3 Configuration Files

| File | Lines | Purpose |
|------|-------|---------|
| `agentx/core/config.py` | 135 | Pydantic Settings - needs DSPY_PREWARM_ENABLED, DSPY_ASYNC_BATCH_SIZE |

### 3.4 Files to Create

| File | Purpose |
|------|---------|
| `agentx/infrastructure/dspy_prewarm.py` | Model pre-warming at startup (3-5 warmup queries) |

---

## 4. Patterns Discovered

### 4.1 Current Anti-Pattern (Blocking Sequential Calls)

**Example from analyst.py Pass 1**:
```python
# 4 sequential calls - each blocks for ~6-8s
context_result = context_analyzer(query=query)         # ~6-8s
insights_result = insight_extractor(query=query)       # ~6-8s
goal_result = goal_detector(query=query, insights=insights)  # ~6-8s
terms_result = search_term_extractor(query=query, insights=insights, domain=domain)  # ~6-8s
# Total: ~24-32s
```

**Problem**: Synchronous calls inside async node function block the event loop.

### 4.2 Target Pattern (Strategic Async Batching)

**Analyze Dependencies**:
- `context_analyzer(query)` - INDEPENDENT
- `insight_extractor(query)` - INDEPENDENT
- `goal_detector(query, insights)` - DEPENDS on insights
- `search_term_extractor(query, insights, domain)` - DEPENDS on insights AND domain

**Optimized Pattern**:
```python
import asyncio

# Batch independent calls (first 2)
context_result, insights_result = await asyncio.gather(
    context_analyzer.aforward(query=query),
    insight_extractor.aforward(query=query),
)

# Sequential dependent calls
domain = context_result["query_type"]
insights = insights_result["insights"]

goal_result = await goal_detector.aforward(query=query, insights=insights)
terms_result = await search_term_extractor.aforward(
    query=query, insights=insights, domain=domain
)
# Total: ~12-16s with 4 concurrent
```

### 4.3 LangGraph Parallel Node Pattern (Alternative Approach)

For completely independent operations, use LangGraph's parallel node execution instead of asyncio.gather:

```python
# Add multiple START edges for parallel execution
workflow.add_edge(START, "context_analyzer_node")
workflow.add_edge(START, "insight_extractor_node")
workflow.add_edge(START, "goal_detector_node")

# All three execute in parallel
# Then aggregate results in a "merge" node
```

### 4.4 Proper DSPy Signature Pattern

**Current Anti-Pattern** (string signatures - Pydantic warnings):
```python
class ContextAnalyzerModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.detect_type = dspy.Predict("query -> query_type")  # BAD
```

**Target Pattern** (proper Signature class):
```python
class QueryAnalysisSignature(dspy.Signature):
    """Proper DSPy signature - no Pydantic issues."""
    query = dspy.InputField(desc="The user's query")
    query_type = dspy.OutputField(desc="Type of query")
    domain = dspy.OutputField(desc="Domain of the query")
    urgency = dspy.OutputField(desc="Urgency level")

class ContextAnalyzerModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.analyze = dspy.Predict(QueryAnalysisSignature)

    def forward(self, query: str) -> dspy.Prediction:
        return self.analyze(query=query)

    async def aforward(self, query: str) -> dspy.Prediction:
        return await self.analyze.acall(query=query)
```

### 4.5 Pre-warming Pattern

**Based on test findings** - model must be loaded into RAM+VRAM before async helps:

```python
class DSPyPrewarmService:
    async def prewarm_model(self, num_queries: int = 5):
        """Send warmup queries to load model into RAM+VRAM."""
        module = SimpleQueryModule()
        warmup_queries = [
            "What is 2 + 2?",
            "Name a color.",
            "What day comes after Monday?",
            "How many sides does a triangle have?",
            "What is the opposite of hot?",
        ]

        for i, query in enumerate(warmup_queries[:num_queries]):
            start = time.perf_counter()
            await module.aforward(question=query)
            duration = (time.perf_counter() - start) * 1000
            logger.info(f"Prewarm {i+1}/{num_queries}: {duration:.0f}ms")
```

---

## 5. Implementation Strategy

### 5.1 Optimistic Batching Strategy

Based on test results showing **ASYNC wins at 4 concurrent (1.20x speedup)**:

1. **Batch independent calls** with `asyncio.gather()` - Max 4 concurrent
2. **Keep dependent calls sequential** - Even with `await`, must wait for dependencies
3. **Add aforward() to all 16 DSPy modules** - Mirror the `forward()` logic

### 5.2 Configuration Additions

```python
# agentx/core/config.py
class Settings(BaseSettings):
    # Existing settings...

    # DSPy optimization settings
    dspy_prewarm_enabled: bool = True
    dspy_prewarm_queries: int = 5
    dspy_async_batch_size: int = 4  # Max concurrent async calls
    dspy_use_simple_queries: bool = True  # Avoid complex instructions
```

### 5.3 Expected Performance Improvement

```
Current: 7 nodes × 6-8s sequential = 42-56s (timeout risk)
Optimized:
  - Pre-warming: ~27s one-time at startup (qwen3:8b)
  - Per query: ~2s after warmup
  - Batching: 4 concurrent = ~1.5-2s effective
  - Total: ~20-25s (safe margin under 60s timeout)
```

---

## 6. Key Files for This Change

### Files to Modify

```
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/nodes/analyst.py
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/nodes/researcher.py
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/nodes/designer.py
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/nodes/contextualizer.py
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/tools/analyst/*.py (5 files)
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/tools/researcher/*.py (5 files)
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/tools/designer/*.py (3 files)
/home/riju279/Documents/Code/XRIG/AgentX/agentx/agent/tools/contextualizer/*.py (3 files)
/home/riju279/Documents/Code/XRIG/AgentX/agentx/core/config.py
```

### Files to Create

```
/home/riju279/Documents/Code/XRIG/AgentX/agentx/infrastructure/dspy_prewarm.py
```

### Test Files (Reference)

```
/home/riju279/Documents/Code/XRIG/AgentX/tests/dspy_saturation_test.py
/home/riju279/Documents/Code/XRIG/AgentX/tests/dspy_proper_signature_test.py
/home/riju279/Documents/Code/XRIG/AgentX/tests/reports/SUMMARY.md
```

---

## 7. Reference Documentation Files

### LangGraph Documentation (Local)

**Core API References**:
- Choosing APIs: `/home/riju279/Documents/Code/XRIG/AgentX/tests/langgraph_choosing_apis.md` (322 lines)
- Graph API: `/home/riju279/Documents/Code/XRIG/AgentX/tests/langgraph_graph_api.md` (723 lines)
- Use Graph API: `/home/riju279/Documents/Code/XRIG/AgentX/tests/langgraph_use_graph_api.md` (2174 lines)

**Patterns and Features**:
- Workflows and Agents: `/home/riju279/Documents/Code/XRIG/AgentX/tests/langgraph_workflows_agents.md` (1113 lines)
- Subgraphs: `/home/riju279/Documents/Code/XRIG/AgentX/tests/langgraph_subgraphs.md` (475 lines)
- Memory: `/home/riju279/Documents/Code/XRIG/AgentX/tests/langgraph_memory.md` (1399 lines)
- Time Travel: `/home/riju279/Documents/Code/XRIG/AgentX/tests/langgraph_time_travel.md` (225 lines)

**Total**: 6,431 lines of LangGraph documentation

### DSPy Documentation (Local)

**Tutorials** (Jupyter notebooks - to be scanned during design phase):
- Streaming: `/home/riju279/Downloads/dspy-main/dspy-main/docs/docs/tutorials/streaming/index.md`
- Tool Use: `/home/riju279/Downloads/dspy-main/dspy-main/docs/docs/tutorials/tool_use/`
- Agents: `/home/riju279/Downloads/dspy-main/dspy-main/docs/docs/tutorials/agents/`
- mem0_react_agent: `/home/riju279/Downloads/dspy-main/dspy-main/docs/docs/tutorials/mem0_react_agent/`
- yahoo_finance_react: `/home/riju279/Downloads/dspy-main/dspy-main/docs/docs/tutorials/yahoo_finance_react/`
- custom_module: `/home/riju279/Downloads/dspy-main/dspy-main/docs/docs/tutorials/custom_module/`

**Programming Reference**:
- Async: `/home/riju279/Downloads/dspy-main/dspy-main/docs/docs/tutorials/async/index.md` (scanned)
- Tools: `/home/riju279/Downloads/dspy-main/dspy-main/docs/docs/learn/programming/tools.md`
- Signatures: `/home/riju279/Downloads/dspy-main/dspy-main/docs/docs/learn/programming/signatures.md`
- Modules: `/home/riju279/Downloads/dspy-main/dspy-main/docs/docs/learn/programming/modules.md`
- LM: `/home/riju279/Downloads/dspy-main/dspy-main/docs/docs/learn/programming/language_models.md`

### R014 Prototype (Working Reference)

**Location**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/`

**Key Files** (to be scanned during design phase):
- `api/dspy_signatures.py` - DSPy signature patterns
- `config/dspy.py` - DSPy configuration
- `services/pipeline/` - Pipeline service patterns
- `services/master_agent/` - Master agent patterns
- `services/tools/` - Tool patterns
- `application/use_cases/master_agent.py` - Master agent use case
- `application/use_cases/widget_generation.py` - Widget generation patterns
- `core/async_compat/` - Async compatibility layer

**Note**: R014 works but uses "high effort" and "stiff behavior" - useful for working patterns but needs optimization

### Archived OpenSpec Change (C003 - Broken Reference)

**Location**: `/home/riju279/Documents/Code/XRIG/AgentX/openspec/changes/archive/2026-01-31-c003-agent-pipeline/`

**Purpose**: Previous attempt at agent pipeline - "slightly broken due to langgraph"
- Useful to understand what went wrong
- Compare working vs broken patterns

### Test Reports
- Summary: `/home/riju279/Documents/Code/XRIG/AgentX/tests/reports/SUMMARY.md`
- qwen3:8b results: `/home/riju279/Documents/Code/XRIG/AgentX/tests/reports/saturation_test_qwen3_8b.md`
- qwen2.5-coder:14b results: `/home/riju279/Documents/Code/XRIG/AgentX/tests/reports/saturation_test_qwen2.5-coder_14b_20260201_172925.json`

---

**Next Artifact**: extract.md

# Proposal: DSPy Performance Optimization for LangGraph Pipeline

## Why

LangGraph agent execution times out at 60+ seconds because:
- 7 nodes each making sequential LLM calls (~6-8s per call = 42-56s total)
- **Specific bottleneck**: analyst.py Pass 1 alone has 4 sequential DSPy calls = ~24-32s
- Ollama processes requests sequentially (no concurrent execution)
- No model pre-warming (cold start adds significant latency)

**Test Results** (`tests/reports/SUMMARY.md`):
- qwen3:8b: 4 concurrent async calls achieve 1.20x speedup
- qwen2.5-coder:14b: 2x faster per query after warmup, but 10x longer warmup
- Pre-warming is critical: reduces per-query time from ~8s to ~2s
- Simple queries perform better than complex instructions

**Documentation Insights**:
- DSPy async: `acall()` and `aforward()` methods for all modules, but adds complexity (error handling, subtle bugs)
- LangGraph: Native parallel node execution via multiple START edges - alternative to `asyncio.gather()`
- Best practice: Start sync for prototyping, switch to async for high-QPS production services

## What Changes

- Add model pre-warming at startup (3-5 queries to load into RAM+VRAM)
- Add `aforward()` methods to DSPy tool modules with **proper Signature classes**
- Update LangGraph nodes to batch independent LLM calls using `asyncio.gather()` (or native parallel node execution)
- Keep sequential dependent calls synchronous (no forced async)
- Add settings: `DSPY_PREWARM_ENABLED`, `DSPY_PREWARM_QUERIES`, `DSPY_ASYNC_BATCH_SIZE`, `DSPY_USE_SIMPLE_QUERIES`
- **BACKWARDS COMPATIBLE**: All changes are additive, current sync behavior preserved

**Implementation Alternatives** (from LangGraph docs):
1. **asyncio.gather() inside nodes** - Batch DSPy calls within a single LangGraph node
2. **LangGraph parallel nodes** - Multiple nodes receiving from START execute concurrently
3. **Hybrid approach** - Parallel nodes for independent operations, asyncio.gather() for dependent batching

## Capabilities

### New Capabilities

- `dspy-performance-optimization`: Model pre-warming and strategic async batching for LangGraph pipeline performance

### Modified Capabilities
- None (implementation optimization only, no spec-level behavior changes)

## Impact

**Affected Code**:
- `agentx/agent/nodes/analyst.py` (188 lines) - Batch independent calls with `asyncio.gather()`
- `agentx/agent/nodes/researcher.py` (119 lines) - Batch independent calls with `asyncio.gather()`
- `agentx/agent/nodes/designer.py` (160 lines) - Batch independent calls with `asyncio.gather()`
- `agentx/agent/nodes/contextualizer.py` (134 lines) - May benefit from async batching
- `agentx/agent/tools/` - 16 modules get `aforward()` methods + proper Signature classes:
  - Analyst (5 modules): context_analyzer.py (~50 lines), data_quality_checker.py (~40), goal_detector.py (~40), insight_extractor.py (~40), search_terms.py (~40)
  - Researcher (5 modules): search_executor.py (~60), web_scraper.py (~80), citation_builder.py (~50), data_structurer.py (~50), findings_beautifier.py (~50)
  - Designer (3 modules): color_scheme.py (~40), hierarchy.py (~40), pov_generator.py (~50)
  - Contextualizer (3 modules): contextualizer.py (~50), filter.py (~40), reranker.py (~50)
- `agentx/infrastructure/dspy_prewarm.py` - NEW: Pre-warming service
- `agentx/core/config.py` (135 lines) - Add pre-warming and batch size settings
- `tests/reports/` - Performance test results and documentation

**API Changes**: None (internal only)

**Dependencies**: No new dependencies

**Systems**: Backend only; frontend unchanged

**Expected Improvement**: 60s → ~20-25s (within 60s timeout margin)

## References

**Documentation Sources** (6,431 lines of LangGraph + DSPy tutorials):
- LangGraph Graph API: `tests/langgraph_graph_api.md` (723 lines) - StateGraph, nodes, edges, reducers
- LangGraph Workflows & Agents: `tests/langgraph_workflows_agents.md` (1113 lines) - Parallel execution patterns
- DSPy Async Tutorial: `/home/riju279/Downloads/dspy-main/dspy-main/docs/docs/tutorials/async/index.md` - acall(), aforward(), async tools
- Full documentation index: See `scan.md` section 7

**Working Reference**:
- R014 UI Showcase: `prototypes/R014_ui_showcase/backend/` - Working DSPy+LangGraph implementation (uses high effort, stiff behavior)

**Archived Reference** (what to avoid):
- C003 Agent Pipeline: `openspec/changes/archive/2026-01-31-c003-agent-pipeline/` - Previous attempt, "slightly broken due to langgraph"

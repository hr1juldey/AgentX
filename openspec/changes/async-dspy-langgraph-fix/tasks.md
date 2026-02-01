# Tasks Artifact: async-dspy-langgraph-fix

**Generated**: 2026-02-02
**Change**: async-dspy-langgraph-fix
**Schema**: spec-factory v1.0.0

---

## 0. Spec Structure Overview (Overview/Implementation Split)

This change uses **33 specs organized in an overview/implementation split**:

**Overview Specs (9)** - High-level architecture that references granular specs:
- `query-complexity-assessment` → Dynamic query planning overview
- `dynamic-routing` → Send API routing overview
- `episodic-memory` → Agent memory (Store) overview
- `graph-memory` → Graph memory (Checkpointers) overview
- `stt-preprocessing` → STT input handling (self-contained)
- `transient-ux` → UX patterns overview
- `adaptive-widget-selection` → Widget selection overview
- `react-agent-hierarchy` → ReAct agent overview
- `dspy_performance` → DSPy benchmarks (self-contained)

**Granular Implementation Specs (24)** - Detailed implementation:
- **Planning** (2): query-planner, execution-plan-models
- **Routing** (3): send-api-workers, evaluator-optimizer, conditional-routing
- **Memory** (7): agent-memory-store, checkpointers-integration, state-accumulation, c005-temporal-metadata, colbert-embedder, mem0-consolidation, semantic-memory-search
- **Agents** (5): coordinator-agent, research-sub-agent, widget-sub-agent, synthesis-sub-agent, memory-sub-agent
- **Voice** (3): voice-state, voice-nodes, voice-cleanup
- **UX** (4): streaming-events, progress-tracking, skeleton-screens, progressive-disclosure-ux
- **Widgets** (3): content-pattern-detection, widget-mapping, progressive-disclosure-ux

**No Double Execution**: Overview specs provide high-level guidance and reference granular specs for implementation details.

**Implementation Phases Below**: Each phase implements the granular specs referenced by the overview specs.

---

## 1. Implementation Checklist

### 1.1 Phase 1: Graph Memory (Checkpointers) + Evaluator

**Goal**: Implement procedural routing memory with state accumulation and evaluator-optimizer pattern.

| Task | File | Est. Time | Status | Verification |
|------|------|-----------|--------|--------------|
| **Core Models** | | | | |
| Create AgentState with reducers | `agentx/domain/models/graph_state.py` | 30m | ⬜ | pyrefly check |
| Create ContinuationDecision model | `agentx/domain/models/routing.py` | 15m | ⬜ | pyrefly check |
| Create ResearchQuality model | `agentx/domain/models/routing.py` | 15m | ⬜ | pyrefly check |
| Create ExecutionPlan models | `agentx/domain/models/query_plan.py` | 30m | ⬜ | pyrefly check |
| **Infrastructure** | | | | |
| Create checkpointer config | `agentx/infrastructure/memory/checkpointer_config.py` | 20m | ⬜ | ruff, pyrefly |
| Add Postgres connection for checkpointer | `agentx/core/dependencies.py` | 15m | ⬜ | ruff check |
| **DSPy Tools** | | | | |
| Create QueryPlannerModule | `agentx/agent/tools/planner/query_planner.py` | 45m | ⬜ | ruff, pyrefly |
| Create EvaluateProgressModule | `agentx/agent/tools/evaluator/evaluate_progress.py` | 45m | ⬜ | ruff, pyrefly |
| **Graph Nodes** | | | | |
| Create query_planner_node | `agentx/agent/nodes/query_planner.py` | 30m | ⬜ | ruff, pyrefly |
| Create evaluator_node | `agentx/agent/nodes/evaluator.py` | 45m | ⬜ | ruff, pyrefly |
| Create direct_answer_node | `agentx/agent/nodes/direct_answer.py` | 20m | ⬜ | ruff, pyrefly |
| Create synthesizer_node | `agentx/agent/nodes/synthesizer.py` | 30m | ⬜ | ruff, pyrefly |
| **Graph Structure** | | | | |
| Create dynamic_agent_graph with StateGraph | `agentx/agent/graph/dynamic_agent_graph.py` | 45m | ⬜ | ruff, pyrefly |
| Add routing functions (route_by_plan, should_continue) | `agentx/agent/graph/dynamic_agent_graph.py` | 30m | ⬜ | ruff, pyrefly |
| Compile with checkpointer | `agentx/agent/graph/dynamic_agent_graph.py` | 15m | ⬜ | Manual test |
| **Time-Travel Debugging** | | | | |
| Create inspect_state utility | `agentx/application/debugging/time_travel.py` | 30m | ⬜ | ruff, pyrefly |
| Add debugging endpoint | `agentx/presentation/api/v1/debug.py` | 20m | ⬜ | ruff, pyrefly |

**Phase 1 Acceptance**:
- [ ] Graph state persists across iterations
- [ ] Evaluator uses structured output (ContinuationDecision)
- [ ] Max 5 iterations enforced
- [ ] Can inspect past states via get_state_history()
- [ ] Ruff and pyrefly checks pass

---

### 1.2 Phase 2: Agent Memory (Store) + Cache Lookup

**Goal**: Implement episodic memory for cached research results with C005 temporal metadata.

| Task | File | Est. Time | Status | Verification |
|------|------|-----------|--------|--------------|
| **Core Models** | | | | |
| Create EpisodicMemory model with C005 temporal metadata | `agentx/domain/models/episodic_memory.py` | 45m | ⬜ | pyrefly check |
| Create TemporalMetadata (C005 aligned) | `agentx/domain/models/episodic_memory.py` | 20m | ⬜ | pyrefly check |
| Create TemporalType enum (C005 aligned) | `agentx/domain/models/episodic_memory.py` | 10m | ⬜ | pyrefly check |
| Create OutcomeQuality enum | `agentx/domain/models/episodic_memory.py` | 10m | ⬜ | pyrefly check |
| **Infrastructure** | | | | |
| Create EpisodicMemoryStore adapter | `agentx/infrastructure/memory/langgraph_store_adapter.py` | 45m | ⬜ | ruff, pyrefly |
| Add PostgresStore to dependencies | `agentx/core/dependencies.py` | 15m | ⬜ | ruff check |
| **Integration** | | | | |
| Add _search_store() to QueryPlannerModule | `agentx/agent/tools/planner/query_planner.py` | 30m | ⬜ | ruff, pyrefly |
| Update query_planner_node to check cache | `agentx/agent/nodes/query_planner.py` | 20m | ⬜ | ruff, pyrefly |
| Mark cached tasks in ExecutionPlan | `agentx/domain/models/query_plan.py` | 10m | ⬜ | pyrefly check |
| Create research_worker_node with store_result() | `agentx/agent/nodes/research_worker.py` | 30m | ⬜ | ruff, pyrefly |
| **Memory Management** | | | | |
| Create ForgettingPolicy | `agentx/application/memory/forgetting_policy.py` | 30m | ⬜ | ruff, pyrefly |
| Create MemoryConsolidation | `agentx/application/memory/consolidation.py` | 30m | ⬜ | ruff, pyrefly |
| Add memory cleanup endpoint | `agentx/presentation/api/v1/memory.py` | 20m | ⬜ | ruff, pyrefly |
| **Graph Update** | | | | |
| Compile graph with store parameter | `agentx/agent/graph/dynamic_agent_graph.py` | 15m | ⬜ | Manual test |

**Phase 2 Acceptance**:
- [ ] Repeated query returns cached result (< 1s)
- [ ] Planner marks tasks as cached when found
- [ ] Semantic search finds relevant research
- [ ] Stored results include C005 temporal metadata
- [ ] Namespace pattern: ("research", query_hash)
- [ ] Access statistics tracked (access_count, last_accessed)
- [ ] User can delete their memories
- [ ] Ruff and pyrefly checks pass

---

### 1.3 Phase 3: Send API Dynamic Workers

**Goal**: Implement dynamic worker creation based on execution plan (not fixed nodes).

| Task | File | Est. Time | Status | Verification |
|------|------|-----------|--------|--------------|
| **Routing Functions** | | | | |
| Create route_by_plan() function | `agentx/agent/nodes/routing.py` | 30m | ⬜ | ruff, pyrefly |
| Create assign_workers() function | `agentx/agent/nodes/routing.py` | 30m | ⬜ | ruff, pyrefly |
| Create should_continue_research() function | `agentx/agent/nodes/routing.py` | 20m | ⬜ | ruff, pyrefly |
| **DSPy Tools** | | | | |
| Create SearchExecutorModule | `agentx/agent/tools/researcher/search_executor.py` | 30m | ⬜ | ruff, pyrefly |
| Create SummarizeExecutorModule | `agentx/agent/tools/researcher/summarize_executor.py` | 30m | ⬜ | ruff, pyrefly |
| Create CompareExecutorModule | `agentx/agent/tools/researcher/compare_executor.py` | 30m | ⬜ | ruff, pyrefly |
| **Graph Node** | | | | |
| Create research_worker_node | `agentx/agent/nodes/research_worker.py` | 30m | ⬜ | ruff, pyrefly |
| **Graph Update** | | | | |
| Add Send API conditional edge | `agentx/agent/graph/dynamic_agent_graph.py` | 20m | ⬜ | Manual test |
| Add research_worker node | `agentx/agent/graph/dynamic_agent_graph.py` | 10m | ⬜ | ruff check |
| Wire evaluator → assign_workers → research_worker → evaluator | `agentx/agent/graph/dynamic_agent_graph.py` | 20m | ⬜ | Manual test |

**Phase 3 Acceptance**:
- [ ] Workers created dynamically based on plan
- [ ] Zero tasks → direct_answer path
- [ ] Dependencies respected (deps must be visited first)
- [ ] Cycle detection prevents repeated tasks
- [ ] Send API returns list[Send] objects
- [ ] Ruff and pyrefly checks pass

---

### 1.4 Phase 4: Transient UX Streaming

**Goal**: Implement skeleton screens, streaming responses, and progress events for long-running tasks.

| Task | File | Est. Time | Status | Verification |
|------|------|-----------|--------|--------------|
| **Core Models** | | | | |
| Create streaming event models | `agentx/domain/models/streaming_events.py` | 30m | ⬜ | pyrefly check |
| Create TokenEvent, ProgressEvent, StatusEvent | `agentx/domain/models/streaming_events.py` | 20m | ⬜ | pyrefly check |
| Create CompleteEvent, BackgroundPromptEvent | `agentx/domain/models/streaming_events.py` | 15m | ⬜ | pyrefly check |
| **Progress Tracking** | | | | |
| Create ProgressTracker class | `agentx/agent/nodes/progress_tracker.py` | 30m | ⬜ | ruff, pyrefly |
| Update research_worker with progress | `agentx/agent/nodes/research_worker.py` | 20m | ⬜ | ruff, pyrefly |
| **Streaming** | | | | |
| Update synthesizer with streamify | `agentx/agent/nodes/synthesizer.py` | 30m | ⬜ | ruff, pyrefly |
| Emit TokenEvent for each token | `agentx/agent/nodes/synthesizer.py` | 20m | ⬜ | ruff, pyrefly |
| Emit CompleteEvent at end | `agentx/agent/nodes/synthesizer.py` | 10m | ⬜ | ruff, pyrefly |
| **WebSocket** | | | | |
| Create streaming WebSocket endpoint | `agentx/presentation/api/v1/streaming.py` | 30m | ⬜ | ruff, pyrefly |
| Send skeleton within 300ms | `agentx/presentation/api/v1/streaming.py` | 15m | ⬜ | Manual test |
| Emit events via WebSocket | `agentx/presentation/api/v1/streaming.py` | 20m | ⬜ | Manual test |
| **Frontend** | | | | |
| Create StreamingResponse component | `frontend/components/StreamingResponse.tsx` | 45m | ⬜ | tsc --noEmit |
| Create SkeletonScreen component | `frontend/components/SkeletonScreen.tsx` | 20m | ⬜ | tsc --noEmit |
| Create ProgressBar component | `frontend/components/ProgressBar.tsx` | 20m | ⬜ | tsc --noEmit |

**Phase 4 Acceptance**:
- [ ] Skeleton appears within 300ms
- [ ] First token arrives < 1s
- [ ] Progress updates every 1-2s
- [ ] Background prompt appears after 15s
- [ ] Streaming gracefully degrades if unavailable
- [ ] Ruff, pyrefly, tsc checks pass

---

### 1.5 Phase 5: STT Preprocessing

**Goal**: Implement STT input preprocessing for noisy speech (fillers, false starts, grammar normalization).

| Task | File | Est. Time | Status | Verification |
|------|------|-----------|--------|--------------|
| **Core Models** | | | | |
| Create InputPath enum (TEXT, STT) | `agentx/domain/models/stt_preprocessing.py` | 10m | ⬜ | pyrefly check |
| Create PreprocessedQuery model | `agentx/domain/models/stt_preprocessing.py` | 15m | ⬜ | pyrefly check |
| Create PreprocessingMetrics model | `agentx/domain/models/stt_preprocessing.py` | 10m | ⬜ | pyrefly check |
| **DSPy Tools** | | | | |
| Create PreprocessSTTSignature | `agentx/agent/tools/preprocessing/stt_preprocessor.py` | 15m | ⬜ | ruff, pyrefly |
| Create STTPreprocessorModule | `agentx/agent/tools/preprocessing/stt_preprocessor.py` | 30m | ⬜ | ruff, pyrefly |
| Create RuleBasedPreprocessor | `agentx/agent/tools/preprocessing/stt_preprocessor.py` | 30m | ⬜ | ruff, pyrefly |
| **Graph Node** | | | | |
| Create stt_preprocessor_node | `agentx/agent/nodes/stt_preprocessor.py` | 30m | ⬜ | ruff, pyrefly |
| Add input_path detection logic | `agentx/agent/nodes/stt_preprocessor.py` | 15m | ⬜ | ruff, pyrefly |
| **Graph Update** | | | | |
| Add conditional edge for input_path | `agentx/agent/graph/dynamic_agent_graph.py` | 15m | ⬜ | Manual test |
| Wire STT → preprocessor → query_planner | `agentx/agent/graph/dynamic_agent_graph.py` | 10m | ⬜ | Manual test |
| **Integration** | | | | |
| Update query_planner to use preprocessed_query | `agentx/agent/nodes/query_planner.py` | 10m | ⬜ | ruff, pyrefly |
| Add preprocessing metrics to state | `agentx/domain/models/graph_state.py` | 10m | ⬜ | pyrefly check |

**Phase 5 Acceptance**:
- [ ] TEXT input passes through unchanged
- [ ] STT input preprocessed into clean query
- [ ] Fillers removed ("um", "uh", "like")
- [ ] False starts handled
- [ ] Grammar normalized
- [ ] Preprocessing < 500ms
- [ ] Ruff and pyrefly checks pass

---

### 1.6 Phase 6: Integration Testing

**Goal**: End-to-end testing of all phases together.

| Task | Description | Est. Time | Status | Verification |
|------|-------------|-----------|--------|--------------|
| **Unit Tests** | | | | |
| Test query planner with cache | Mock Store, verify cache hit | 30m | ⬜ | pytest |
| Test evaluator with accumulated state | Mock state, verify decision | 30m | ⬜ | pytest |
| Test route_by_plan with 0 tasks | Verify direct_answer path | 20m | ⬜ | pytest |
| Test assign_workers Send creation | Verify list[Send] output | 20m | ⬜ | pytest |
| Test STT preprocessor | Verify filler removal | 20m | ⬜ | pytest |
| **Integration Tests** | | | | |
| Test simple query (0 tasks) | Full graph, verify direct answer | 30m | ⬜ | pytest |
| Test complex query (N tasks) | Full graph, verify worker creation | 30m | ⬜ | pytest |
| Test repeated query (cache hit) | Second run, verify cached result | 20m | ⬜ | pytest |
| Test max iterations limit | Force 6 iterations, verify stop | 20m | ⬜ | pytest |
| Test time-travel debugging | Get state history, verify checkpoints | 20m | ⬜ | pytest |
| **Performance Tests** | | | | |
| Test simple query latency | Should be < 5s | 15m | ⬜ | Manual |
| Test complex query latency | Should be < 60s | 30m | ⬜ | Manual |
| Test cache hit latency | Should be < 1s | 15m | ⬜ | Manual |
| Test preprocessing latency | Should be < 500ms | 15m | ⬜ | Manual |
| **UX Tests** | | | | |
| Test skeleton screen timing | Verify < 300ms | 15m | ⬜ | Manual |
| Test streaming delivery | Verify token-by-token | 20m | ⬜ | Manual |
| Test background prompt timing | Verify at 15s | 15m | ⬜ | Manual |
| **E2E Tests** | | | | |
| Test TEXT input flow | Full pipeline from text to response | 30m | ⬜ | Manual |
| Test STT input flow | Full pipeline from STT to response | 30m | ⬜ | Manual |
| Test voice integration | With kyutai server, full voice flow | 30m | ⬜ | Manual |

**Phase 6 Acceptance**:
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Performance targets met (simple < 5s, complex < 60s, cache < 1s)
- [ ] UX targets met (skeleton < 300ms, streaming works)
- [ ] Ruff, pyrefly, tsc checks pass
- [ ] No regressions in existing functionality

---

### 1.7 Phase 7: ReAct Agent Hierarchy

**Goal**: Implement Coordinator Agent that deploys specialized sub-agents with limited tools (3-5 per agent).

| Task | File | Est. Time | Status | Verification |
|------|------|-----------|--------|--------------|
| **Core Models** | | | | |
| Create CoordinatorSignature with class-based DSPy signature | `agentx/agent/react_agents/coordinator_agent.py` | 20m | ⬜ | ruff, pyrefly |
| Create BaseReActAgent with tool limit enforcement | `agentx/agent/react_agents/base_agent.py` | 30m | ⬜ | ruff, pyrefly |
| Define MAX_TOOLS_PER_AGENT constant | `agentx/agent/react_agents/base_agent.py` | 5m | ⬜ | ruff check |
| **Research Agent** | | | | |
| Create ResearchAgent (3 tools: search, scrape, cite) | `agentx/agent/react_agents/research_agent.py` | 30m | ⬜ | ruff, pyrefly |
| Create SearXNGSearch tool wrapper | `agentx/agent/tools/researcher/searxng_search.py` | 20m | ⬜ | ruff, pyrefly |
| Create WebScraper tool wrapper | `agentx/agent/tools/researcher/web_scraper.py` | 20m | ⬜ | ruff, pyrefly |
| Create CitationBuilder tool wrapper | `agentx/agent/tools/researcher/citation_builder.py` | 10m | ⬜ | ruff, pyrefly |
| **Widget Agent** | | | | |
| Create WidgetAgent (3 tools: select, render_card, show_chart) | `agentx/agent/react_agents/widget_agent.py` | 30m | ⬜ | ruff, pyrefly |
| Create WidgetSelector tool wrapper | `agentx/agent/tools/widgets/widget_selector.py` | 20m | ⬜ | ruff, pyrefly |
| Create CardRenderer tool wrapper | `agentx/agent/tools/widgets/card_renderer.py` | 15m | ⬜ | ruff, pyrefly |
| Create ChartRenderer tool wrapper | `agentx/agent/tools/widgets/chart_renderer.py` | 15m | ⬜ | ruff, pyrefly |
| **Synthesis Agent** | | | | |
| Create SynthesisAgent (3 tools: summarize, format, check_quality) | `agentx/agent/react_agents/synthesis_agent.py` | 30m | ⬜ | ruff, pyrefly |
| Create Summarizer tool wrapper | `agentx/agent/tools/synthesis/summarizer.py` | 15m | ⬜ | ruff, pyrefly |
| Create TextFormatter tool wrapper | `agentx/agent/tools/synthesis/text_formatter.py` | 10m | ⬜ | ruff, pyrefly |
| Create QualityChecker tool wrapper | `agentx/agent/tools/synthesis/quality_checker.py` | 15m | ⬜ | ruff, pyrefly |
| **Memory Agent** | | | | |
| Create MemoryAgent (3 tools: store, search, consolidate) | `agentx/agent/react_agents/memory_agent.py` | 30m | ⬜ | ruff, pyrefly |
| **Coordinator Integration** | | | | |
| Create CoordinatorAgent with sub-agent routing | `agentx/agent/react_agents/coordinator_agent.py` | 30m | ⬜ | ruff, pyrefly |
| Add coordinator reasoning output | `agentx/agent/react_agents/coordinator_agent.py` | 15m | ⬜ | ruff, pyrefly |
| Update research_worker_node to use Coordinator | `agentx/agent/nodes/research_worker.py` | 20m | ⬜ | ruff, pyrefly |

**Phase 7 Acceptance**:
- [ ] Each sub-agent has max 5 tools (preferably 3)
- [ ] BaseReActAgent raises ValueError if > 5 tools
- [ ] All DSPy signatures are class-based (no inline strings)
- [ ] All forward() methods return dspy.Prediction
- [ ] Coordinator provides reasoning for agent selection
- [ ] Sub-agents use max_iters=3
- [ ] Ruff and pyrefly checks pass

---

### 1.8 Phase 8: ColBERT Memory (Qdrant Semantic Search)

**Goal**: Implement Qdrant + ColBERTv2 for token-level semantic search with multivectors.

| Task | File | Est. Time | Status | Verification |
|------|------|-----------|--------|--------------|
| **Infrastructure** | | | | |
| Create ColBERTEmbedder class with lazy-loading | `agentx/infrastructure/external/colbert_embedder.py` | 45m | ⬜ | ruff, pyrefly |
| Add fastembed dependency | `pyproject.toml` | 5m | ⬜ | uv sync |
| Create Qdrant multivector collection config | `agentx/infrastructure/external/colbert_embedder.py` | 20m | ⬜ | ruff, pyrefly |
| **Embedding** | | | | |
| Implement embed_text() method (multivectors) | `agentx/infrastructure/external/colbert_embedder.py` | 20m | ⬜ | ruff, pyrefly |
| Implement query_embed() method (optimized) | `agentx/infrastructure/external/colbert_embedder.py` | 15m | ⬜ | ruff, pyrefly |
| Implement ensure_collection() with MultiVectorConfig | `agentx/infrastructure/external/colbert_embedder.py` | 20m | ⬜ | ruff, pyrefly |
| **Search** | | | | |
| Implement search() method with MaxSim operation | `agentx/infrastructure/external/colbert_embedder.py` | 25m | ⬜ | ruff, pyrefly |
| Add user_id filter support | `agentx/infrastructure/external/colbert_embedder.py` | 10m | ⬜ | ruff, pyrefly |
| **Integration** | | | | |
| Update MemoryManager to use ColBERT | `agentx/infrastructure/memory/langgraph_store_adapter.py` | 20m | ⬜ | ruff, pyrefly |
| Store research results in Qdrant with multivectors | `agentx/infrastructure/memory/langgraph_store_adapter.py` | 25m | ⬜ | ruff, pyrefly |
| Add semantic search to query planner cache check | `agentx/agent/tools/planner/query_planner.py` | 20m | ⬜ | ruff, pyrefly |
| **Configuration** | | | | |
| Add ColBERT settings to memory_config.py | `agentx/core/memory_config.py` | 10m | ⬜ | ruff check |
| Add Qdrant URL configuration | `agentx/core/config.py` | 5m | ⬜ | ruff check |

**Phase 8 Acceptance**:
- [ ] ColBERT model lazy-loads on first use
- [ ] Multivector embeddings (128-dim per token)
- [ ] Qdrant collection created with MultiVectorConfig
- [ ] Semantic search returns relevant results
- [ ] User isolation enforced (user_id filter)
- [ ] Research results stored in both Store and Qdrant
- [ ] Ruff and pyrefly checks pass

---

### 1.9 Phase 9: Adaptive Widget Selection

**Goal**: Implement content-driven widget selection (not arbitrary dump) with adaptive count.

| Task | File | Est. Time | Status | Verification |
|------|------|-----------|--------|--------------|
| **Core Models** | | | | |
| Create WidgetSpecification model | `agentx/domain/models/widget_selection.py` | 15m | ⬜ | pyrefly check |
| Create WidgetType enum (DATA_TABLE, TIMELINE, MAP, etc.) | `agentx/domain/models/widget_selection.py` | 10m | ⬜ | pyrefly check |
| Create ContentPattern enum (COMPARISON, TEMPORAL, GEOGRAPHIC) | `agentx/domain/models/widget_selection.py` | 10m | ⬜ | pyrefly check |
| Create SelectWidgetsSignature (class-based) | `agentx/agent/tools/widgets/widget_selector.py` | 15m | ⬜ | ruff, pyrefly |
| **DSPy Tool** | | | | |
| Create WidgetSelectorModule with pattern → widget mapping | `agentx/agent/tools/widgets/widget_selector.py` | 30m | ⬜ | ruff, pyrefly |
| Implement adaptive count logic (0 tasks → 0 widgets, 6+ tasks → 6-7) | `agentx/agent/tools/widgets/widget_selector.py` | 20m | ⬜ | ruff, pyrefly |
| **Integration** | | | | |
| Update WidgetAgent to pass accumulated_findings | `agentx/agent/react_agents/widget_agent.py` | 15m | ⬜ | ruff, pyrefly |
| Add widget selection to synthesizer_node | `agentx/agent/nodes/synthesizer.py` | 20m | ⬜ | ruff, pyrefly |
| Add selected_widgets to AgentState | `agentx/domain/models/graph_state.py` | 10m | ⬜ | pyrefly check |
| **Frontend** | | | | |
| Create ProgressiveDisclosure component | `frontend/components/ProgressiveDisclosure.tsx` | 30m | ⬜ | tsc --noEmit |
| Create DataTable component | `frontend/components/widgets/DataTable.tsx` | 30m | ⬜ | tsc --noEmit |
| Create Timeline component | `frontend/components/widgets/Timeline.tsx` | 30m | ⬜ | tsc --noEmit |
| Create Map component | `frontend/components/widgets/Map.tsx` | 30m | ⬜ | tsc --noEmit |

**Phase 9 Acceptance**:
- [ ] Widgets selected based on accumulated_findings
- [ ] Pattern → Widget mapping works (comparison → DATA_TABLE, etc.)
- [ ] Widget count adapts to task count (0-7 widgets)
- [ ] Simple queries get text-only (0 widgets)
- [ ] Complex queries get relevant widgets
- [ ] Progressive disclosure shows 3 initially, "Show More" for rest
- [ ] Ruff, pyrefly, tsc checks pass

---

### 1.10 Phase 10: Mem0 Consolidation

**Goal**: Implement Mem0AI integration for advanced memory consolidation with quality filtering.

| Task | File | Est. Time | Status | Verification |
|------|------|-----------|--------|--------------|
| **Infrastructure** | | | | |
| Create Mem0MemoryAdapter class | `agentx/infrastructure/memory/mem0_adapter.py` | 30m | ⬜ | ruff, pyrefly |
| Add mem0ai dependency | `pyproject.toml` | 5m | ⬜ | uv sync |
| Configure Mem0 with Qdrant backend | `agentx/infrastructure/memory/mem0_adapter.py` | 15m | ⬜ | ruff, pyrefly |
| **Quality Filtering** | | | | |
| Implement confidence filter (>= 0.6) | `agentx/infrastructure/memory/mem0_adapter.py` | 15m | ⬜ | ruff, pyrefly |
| Implement length filter (>= 50 chars) | `agentx/infrastructure/memory/mem0_adapter.py` | 10m | ⬜ | ruff, pyrefly |
| Implement duplicate detection | `agentx/infrastructure/memory/mem0_adapter.py` | 15m | ⬜ | ruff, pyrefly |
| **Consolidation** | | | | |
| Implement consolidate_if_needed() method | `agentx/infrastructure/memory/mem0_adapter.py` | 20m | ⬜ | ruff, pyrefly |
| Create ConsolidateMemoryUseCase | `agentx/application/use_cases/manage_memory.py` | 25m | ⬜ | ruff, pyrefly |
| Add consolidation threshold (100 memories) | `agentx/infrastructure/memory/mem0_adapter.py` | 10m | ⬜ | ruff check |
| **Integration** | | | | |
| Update research_worker_node to store via Mem0 | `agentx/agent/nodes/research_worker.py` | 15m | ⬜ | ruff, pyrefly |
| Add consolidation endpoint | `agentx/presentation/api/v1/memory.py` | 15m | ⬜ | ruff, pyrefly |

**Phase 10 Acceptance**:
- [ ] Low-confidence results (< 0.6) not stored
- [ ] Trivial results (< 50 chars) not stored
- [ ] Duplicates detected and skipped
- [ ] Consolidation triggers at 100 memories
- [ ] Consolidated summaries stored back
- [ ] Qdrant used as Mem0 backend
- [ ] Ruff and pyrefly checks pass

---

### 1.11 Phase 11: Voice Subgraph

**Goal**: Implement LangGraph voice subgraph with guaranteed cleanup for TTS/STT sessions.

| Task | File | Est. Time | Status | Verification |
|------|------|-----------|--------|--------------|
| **Core Models** | | | | |
| Create VoiceState TypedDict | `agentx/domain/models/voice_state.py` | 20m | ⬜ | pyrefly check |
| Define voice session states (connect, listen, transcribe, etc.) | `agentx/domain/models/voice_state.py` | 10m | ⬜ | pyrefly check |
| **Voice Nodes** | | | | |
| Create connect_kyutai_node | `agentx/agent/nodes/voice/voice_nodes.py` | 30m | ⬜ | ruff, pyrefly |
| Create listen_audio_node with VAD | `agentx/agent/nodes/voice/voice_nodes.py` | 30m | ⬜ | ruff, pyrefly |
| Create transcribe_node | `agentx/agent/nodes/voice/voice_nodes.py` | 20m | ⬜ | ruff, pyrefly |
| Create process_agent_node (invokes main graph) | `agentx/agent/nodes/voice/voice_nodes.py` | 25m | ⬜ | ruff, pyrefly |
| Create synthesize_node with interrupt check | `agentx/agent/nodes/voice/voice_nodes.py` | 25m | ⬜ | ruff, pyrefly |
| Create stream_audio_node | `agentx/agent/nodes/voice/voice_nodes.py` | 15m | ⬜ | ruff, pyrefly |
| Create check_interrupt_node | `agentx/agent/nodes/voice/voice_nodes.py` | 15m | ⬜ | ruff, pyrefly |
| **Cleanup Node** | | | | |
| Create cleanup_node (CRITICAL - must always run) | `agentx/agent/nodes/voice/voice_nodes.py` | 25m | ⬜ | ruff, pyrefly |
| Implement WebSocket closing (STT, TTS) | `agentx/agent/nodes/voice/voice_nodes.py` | 15m | ⬜ | ruff, pyrefly |
| Implement session state clearing | `agentx/agent/nodes/voice/voice_nodes.py` | 10m | ⬜ | ruff, pyrefly |
| **Voice Subgraph** | | | | |
| Create build_voice_subgraph() function | `agentx/agent/nodes/voice/voice_subgraph.py` | 30m | ⬜ | ruff, pyrefly |
| Wire ALL paths to cleanup node | `agentx/agent/nodes/voice/voice_subgraph.py` | 20m | ⬜ | ruff, pyrefly |
| Add cleanup → END edge | `agentx/agent/nodes/voice/voice_subgraph.py` | 5m | ⬜ | ruff check |
| **Integration** | | | | |
| Create voice_input_node for main graph | `agentx/agent/nodes/voice/voice_integration.py` | 25m | ⬜ | ruff, pyrefly |
| Add voice subgraph to main graph | `agentx/agent/graph/dynamic_agent_graph.py` | 15m | ⬜ | ruff, pyrefly |

**Phase 11 Acceptance**:
- [ ] VoiceState TypedDict defined
- [ ] ALL conditional edges lead to cleanup node
- [ ] Cleanup closes STT WebSocket
- [ ] Cleanup closes TTS WebSocket
- [ ] Cleanup clears session state
- [ ] User interrupt flows to cleanup
- [ ] Connection error flows to cleanup
- [ ] Normal completion flows to cleanup
- [ ] Ruff and pyrefly checks pass

---

### 1.12 Phase 12: Progressive Disclosure

**Goal**: Implement progressive disclosure for widgets (3 visible, "Show More" button).

| Task | File | Est. Time | Status | Verification |
|------|------|-----------|--------|--------------|
| **Frontend Components** | | | | |
| Create ProgressiveDisclosure component | `frontend/components/ProgressiveDisclosure.tsx` | 30m | ⬜ | tsc --noEmit |
| Create ShowMoreButton component | `frontend/components/ShowMoreButton.tsx` | 15m | ⬜ | tsc --noEmit |
| Create WidgetCard wrapper component | `frontend/components/WidgetCard.tsx` | 20m | ⬜ | tsc --noEmit |
| **Backend Support** | | | | |
| Add priority field to WidgetSpecification | `agentx/domain/models/widget_selection.py` | 10m | ⬜ | pyrefly check |
| Sort widgets by priority in synthesizer | `agentx/agent/nodes/synthesizer.py` | 15m | ⬜ | ruff, pyrefly |
| Emit WidgetRevealEvent for each widget | `agentx/agent/nodes/synthesizer.py` | 20m | ⬜ | ruff, pyrefly |
| **Integration** | | | | |
| Update WebSocket to stream widgets | `agentx/presentation/api/v1/streaming.py` | 20m | ⬜ | ruff, pyrefly |
| Update StreamingResponse to handle widgets | `frontend/components/StreamingResponse.tsx` | 25m | ⬜ | tsc --noEmit |

**Phase 12 Acceptance**:
- [ ] Progressive disclosure shows 3 widgets initially
- [ ] "Show More" button appears when > 3 widgets
- [ ] Clicking "Show More" reveals all widgets
- [ ] Widgets sorted by priority (highest first)
- [ ] WidgetRevealEvent emitted for each widget
- [ ] Ruff, pyrefly, tsc checks pass

---

### 1.13 Phase 13: Final Integration and Testing

**Goal**: End-to-end integration testing of all 13 phases together.

| Task | Description | Est. Time | Status | Verification |
|------|-------------|-----------|--------|--------------|
| **Full Stack Integration** | | | | |
| Test TEXT input flow through all phases | Full pipeline | 30m | ⬜ | Manual |
| Test STT input flow through all phases | Full pipeline with voice | 30m | ⬜ | Manual |
| Test voice subgraph cleanup guarantee | Force error, verify cleanup | 30m | ⬜ | Manual |
| Test ReAct hierarchy routing | Complex query, verify coordinator | 30m | ⬜ | Manual |
| **Three Memory Verification** | | | | |
| Test graph memory (Checkpointers) | Verify state persistence | 20m | ⬜ | Manual |
| Test agent memory (Store) | Verify cache hit | 15m | ⬜ | Manual |
| Test semantic memory (Qdrant+ColBERT) | Verify semantic search | 20m | ⬜ | Manual |
| Verify memory separation | Check no confusion between types | 15m | ⬜ | Manual |
| **Widget Verification** | | | | |
| Test adaptive widget selection | Vary task count, verify widget count | 20m | ⬜ | Manual |
| Test progressive disclosure | Verify 3 visible, Show More works | 15m | ⬜ | Manual |
| Verify widgets use research findings | Check accumulated_findings passed | 15m | ⬜ | Manual |
| **DSPy Best Practices Verification** | | | | |
| Scan for inline signatures | grep for inline strings | 15m | ⬜ | Should find 0 |
| Scan for dict returns in DSPy modules | grep for "return {" | 15m | ⬜ | Should find 0 in tools/ |
| Verify all DSPy returns are Prediction | Check all forward() methods | 20m | ⬜ | Manual |
| **Performance Verification** | | | | |
| Test simple query latency | Should be < 5s | 15m | ⬜ | Manual |
| Test complex query latency | Should be < 60s | 30m | ⬜ | Manual |
| Test cache hit latency | Should be < 1s | 15m | ⬜ | Manual |
| Test voice cleanup guarantee | All paths cleanup < 1s | 15m | ⬜ | Manual |
| **Code Quality Final Check** | | | | |
| Run ruff check --fix on all files | All pass | 15m | ⬜ | ruff |
| Run ruff format on all files | All pass | 10m | ⬜ | ruff |
| Run pyrefly check --summarize-errors | All pass | 20m | ⬜ | pyrefly |
| Check file sizes (< 150 lines) | All pass | 10m | ⬜ | wc -l |
| Check imports (no relative) | All pass | 10m | ⬜ | grep |

**Phase 13 Acceptance**:
- [ ] All 12 previous phases working together
- [ ] Three memory types verified separated
- [ ] Voice cleanup guaranteed (all paths tested)
- [ ] ReAct hierarchy working (coordinator deploys sub-agents)
- [ ] Adaptive widgets working (content-driven)
- [ ] Progressive disclosure working (3 + Show More)
- [ ] All DSPy best practices verified (0 inline signatures, 0 dict returns)
- [ ] Performance targets met
- [ ] Ruff, pyrefly, tsc checks pass
- [ ] File sizes within limits
- [ ] No relative imports

---

## 2. Verification Steps

### 2.1 Code Quality (Run After Each Phase)

```bash
# Lint and format
ruff check agentx/ --fix
ruff format agentx/

# Type checking
pyrefly check agentx/ --summarize-errors

# Frontend type check
cd frontend
npx tsc --noEmit
```

### 2.2 File Size Check

```bash
# Verify no file exceeds 150 lines (100 executable + 50 overhead)
find agentx/ -name "*.py" -exec wc -l {} + | awk '$1 > 150 {print $0}'
```

### 2.3 Import Check

```bash
# Verify no relative imports
grep -r "from \.\." agentx/  # Should return nothing
grep -r "from \." agentx/ | grep -v "from \.\.\." | grep -v "# type:"  # Should return nothing
```

### 2.4 Memory Types Verification

```bash
# Verify graph memory uses Checkpointers
grep -r "PostgresSaver\|InMemorySaver\|checkpointer" agentx/infrastructure/memory/

# Verify agent memory uses Store
grep -r "PostgresStore\|InMemoryStore\|\.asearch\|\.aput" agentx/infrastructure/memory/

# Verify no confusion (Checkpointers for graph, Store for agent)
```

---

## 3. Acceptance Criteria

### 3.1 Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| Simple queries get direct answer | Query: "What is 2+2?" | No research, direct answer < 5s |
| Complex queries create workers | Query: "Compare iPhone 15 vs Pixel 8" | Dynamic workers created |
| Cached results reused | Run same query twice | Second run < 1s |
| Evaluator uses structured output | Check evaluator output | ContinuationDecision object |
| Max iterations enforced | Force low-quality research | Stops at 5 iterations |
| State accumulates | Check state after each iteration | findings grow each time |
| Time-travel works | Call get_state_history() | List of checkpoints |
| STT preprocessing works | Send "um what is capital" | Clean output |
| Skeleton appears fast | Load query page | Skeleton < 300ms |
| Streaming works | Watch response | Token-by-token delivery |

### 3.2 Non-Functional Criteria

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| Zero relative imports | `grep -r "from \."` | 0 matches |
| All files < 150 lines | `wc -l` check | All pass |
| Ruff clean | `ruff check` | 0 errors |
| Pyrefly clean | `pyrefly check` | 0 errors |
| C005 alignment | Check temporal metadata | All fields present |
| Memory separation | Check implementation | Checkpointers ≠ Store |

### 3.3 R014 Comparison

| Aspect | R014 | New Design | Test |
|--------|------|------------|------|
| Pipeline | Fixed 8 phases | Dynamic 0-N tasks | Query with varying complexity |
| Routing | Text parsing | Structured decision | Check evaluator output |
| Memory | None | Graph + Agent | Check cache on second query |
| State | Forgotten | Accumulated | Check state history |
| UX | None | Streaming | Watch progress during long query |

---

## 4. Definition of Done

A **phase** is complete when:

- [ ] All tasks in phase are done
- [ ] `ruff check --fix` passes with 0 errors
- [ ] `ruff format` applied
- [ ] `pyrefly check --summarize-errors` passes
- [ ] File size check passes
- [ ] Import check passes
- [ ] Unit tests for phase pass
- [ ] Manual test passes (if applicable)

The **entire change** is complete when:

- [ ] All 6 phases are complete
- [ ] All acceptance criteria are met
- [ ] Performance targets met (simple < 5s, complex < 60s, cache < 1s)
- [ ] No regressions in existing functionality
- [ ] Documentation updated (CLAUDE.md, README)
- [ ] Two memory types properly separated and verified

---

## 5. Rollback Plan

If implementation fails at any point:

### Phase 1 Rollback (Graph Memory)

```bash
# Remove new files
git clean -fd agentx/domain/models/graph_state.py
git clean -fd agentx/domain/models/routing.py
git clean -fd agentx/domain/models/query_plan.py
git clean -fd agentx/infrastructure/memory/checkpointer_config.py
git clean -fd agentx/agent/tools/planner/
git clean -fd agentx/agent/tools/evaluator/
git clean -fd agentx/agent/nodes/query_planner.py
git clean -fd agentx/agent/nodes/evaluator.py
git clean -fd agentx/agent/nodes/direct_answer.py
git clean -fd agentx/agent/nodes/synthesizer.py
git clean -fd agentx/agent/graph/dynamic_agent_graph.py
```

### Phase 2 Rollback (Agent Memory)

```bash
# Remove new files
git clean -fd agentx/domain/models/episodic_memory.py
git clean -fd agentx/infrastructure/memory/langgraph_store_adapter.py
git clean -fd agentx/application/memory/
git clean -fd agentx/presentation/api/v1/memory.py
```

### Phase 3 Rollback (Send API)

```bash
# Remove new files
git clean -fd agentx/agent/nodes/routing.py
git clean -fd agentx/agent/nodes/research_worker.py
git clean -fd agentx/agent/tools/researcher/
```

### Phase 4 Rollback (Transient UX)

```bash
# Remove new files
git clean -fd agentx/domain/models/streaming_events.py
git clean -fd agentx/agent/nodes/progress_tracker.py
git clean -fd agentx/presentation/api/v1/streaming.py
git clean -fd frontend/components/StreamingResponse.tsx
git clean -fd frontend/components/SkeletonScreen.tsx
git clean -fd frontend/components/ProgressBar.tsx
```

### Phase 5 Rollback (STT Preprocessing)

```bash
# Remove new files
git clean -fd agentx/domain/models/stt_preprocessing.py
git clean -fd agentx/agent/tools/preprocessing/
git clean -fd agentx/agent/nodes/stt_preprocessor.py
```

### Recovery Actions

1. **Identify failure point**: Check logs for last successful phase
2. **Isolate broken code**: Comment out problematic additions
3. **Verify baseline**: Ensure existing functionality works
4. **Fix and retry**: Address issue, re-run verification

---

## 6. Test Commands Reference

### Unit Tests

```bash
# Run all tests
pytest tests/unit/

# Run specific test file
pytest tests/unit/test_query_planner.py -v
pytest tests/unit/test_evaluator.py -v
pytest tests/unit/test_stt_preprocessor.py -v

# Run with coverage
pytest --cov=agentx.agent.tools.planner --cov-report=html
pytest --cov=agentx.infrastructure.memory --cov-report=html
```

### Integration Tests

```bash
# Test simple query flow
pytest tests/integration/test_simple_query_flow.py -v

# Test complex query flow
pytest tests/integration/test_complex_query_flow.py -v

# Test cache hit
pytest tests/integration/test_cache_hit.py -v

# Test time-travel
pytest tests/integration/test_time_travel.py -v
```

### Performance Tests

```bash
# Simple query benchmark
pytest tests/benchmark/simple_query_benchmark.py -v
# Expected: < 5s

# Complex query benchmark
pytest tests/benchmark/complex_query_benchmark.py -v
# Expected: < 60s

# Cache hit benchmark
pytest tests/benchmark/cache_hit_benchmark.py -v
# Expected: < 1s
```

### Manual Tests

```bash
# Start backend
uv run --active uvicorn agentx.main:app --host 0.0.0.0 --port 8015 --reload

# Start frontend
cd frontend && npm run dev

# Test in browser:
# 1. Simple query: "What is 2+2?"
# 2. Complex query: "Compare iPhone 15 vs Pixel 8"
# 3. Repeat complex query (should cache)
# 4. Check time-travel at /api/v1/debug/state/{thread_id}
```

---

## 7. Dependencies Unlocked

This change unlocks:

| Change | Unlocked Feature |
|--------|-----------------|
| **Future: Advanced memory consolidation** | With C005 alignment, can add fact invalidation, TTL-based forgetting |
| **Future: Multi-agent parallelization** | Send API pattern enables parallel worker execution |
| **Future: Advanced streaming** | DSPy streaming pattern enables real-time UI updates |
| **Future: Voice-first interface** | STT preprocessing enables better voice interaction |
| **Future: Adaptive widget selection** | Query complexity assessment enables dynamic UI generation |

---

## 8. Rollout Notes

### Phase Sequencing

Phases are designed to be **independent but cumulative**:

1. **Phase 1** (Graph Memory) - Can be deployed alone, adds state-driven routing
2. **Phase 2** (Agent Memory) - Requires Phase 1 for state, adds caching
3. **Phase 3** (Send API) - Requires Phase 1 for routing, adds dynamic workers
4. **Phase 4** (Transient UX) - Independent, adds UX improvements
5. **Phase 5** (STT Preprocessing) - Independent, adds voice support
6. **Phase 6** (Integration) - Requires all phases for full testing

### Deployment Strategy

- **Staging**: Deploy all phases to staging environment
- **Canary**: Enable Phase 1-3 for 10% of users
- **Gradual**: Increase canary to 50%, then 100%
- **Monitor**: Check performance metrics, cache hit rates, UX feedback

### Monitoring Metrics

| Metric | Target | Alert |
|--------|--------|-------|
| Simple query latency | < 5s | > 10s |
| Complex query latency | < 60s | > 120s |
| Cache hit rate | > 30% | < 10% |
| Skeleton appearance | < 300ms | > 1s |
| Evaluator decision time | < 2s | > 5s |

---

**Total Estimated Time**: ~60-70 hours (spread across 13 phases)

**Recommended Sprint Allocation**: 2-3 weeks with testing

**Spec Coverage**: 33 specs (9 overview + 24 granular)

---

**End of spec-factory pipeline**

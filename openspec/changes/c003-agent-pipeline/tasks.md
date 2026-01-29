# Tasks Artifact: c003-agent-pipeline

**Generated**: 2026-01-29
**Change**: c003-agent-pipeline
**Schema**: spec-factory v1
**Source**: R014 Postmortem `/home/riju279/Documents/Code/XRIG/AgentX/docs/learnings/R014_postmortem/`

---

## Summary

This tasks.md contains **actual R014 porting tasks** based on the postmortem cataloging of 265 files, 69 signatures, 134 DSPy modules, and 50+ tools.

**Total Tasks**: ~150 tasks across 7 phases
**Estimated Files**: 80-100 Python files
**Estimated LOC**: 8,000-10,000 lines

---

## Phase 1: Critical Infrastructure (FOUNDATION)

### 1.1 Type Conversion Utilities (CRITICAL)

| Task | File | Lines | Status | Notes |
|------|------|-------|--------|-------|
| Port _to_float function | `agent/agent/tools/common/type_utils.py` | 50 | ✓ | From R014: 3 fallbacks (direct, regex, keyword) |
| Port _to_bool function | `agent/agent/tools/common/type_utils.py` | 30 | ✓ | From R014: Boolean parsing with fallbacks |
| Add unit tests | `tests/agent/tools/test_type_utils.py` | 80 | ✓ | Test all fallback paths (16 tests pass) |

**R014 Source**: `services/tools/common/type_utils.py`

**Why Critical**: LLMs return text, not numbers/booleans. All DSPy agents depend on these.

---

### 1.2 Chunking Infrastructure (CRITICAL)

| Task | File | Lines | Status | Notes |
|------|------|-------|--------|-------|
| Create chunking constants | `agent/agent/tools/common/chunking.py` | 30 | ✓ | MAX_CHUNK_SIZE=500, OVERLAP=100, ITERATIONS=3 |
| Create chunking helper | `agent/agent/tools/common/chunking.py` | 50 | ✓ | chunk_text() function |
| Add unit tests | `tests/agent/tools/test_chunking.py` | 60 | ✓ | Test edge cases (empty, single chunk, multi-chunk) - 25 tests pass |

**R014 Source**: `services/tools/analyst/insight_extractor.py`, `services/core/chunking.py`

**Why Critical**: Prevents LLM context window corruption. Proven pattern (4/4 tests pass).

---

### 1.3 Safe DSPy Extraction Pattern (CRITICAL)

| Task | File | Lines | Status | Notes |
|------|------|-------|--------|-------|
| Create extraction helper | `agent/agent/tools/common/dspy_helpers.py` | 40 | ✓ | safe_extract() with hasattr + .get() |
| Add to DSPy agent base | `agent/agent/agents/base.py` | 30 | ⬜ | Mixin or base class with safe_extract |
| Add unit tests | `tests/agent/tools/test_dspy_helpers.py` | 50 | ✓ | Test with DSPy Prediction objects (18 tests pass) |

**R014 Source**: Multiple agent files (pattern documented in postmortem)

**Why Critical**: DSPy returns special objects, not plain dicts. Prevents crashes.

---

### 1.4 LangGraph State & Graph (CRITICAL)

| Task | File | Lines | Status | Notes |
|------|------|-------|--------|-------|
| Create AgentState | `agent/agent/state.py` | 50 | ✓ | TypedDict with ui_message_reducer |
| Create create_graph() | `agent/agent/graph.py` | 100 | ✓ | StateGraph (3-node base, 8-node in Phase 2) |
| Add nodes stub file | `agent/agent/nodes/__init__.py` | 20 | ✓ | Placeholder imports |

**R014 Source**: `services/master_agent/master_agent.py` (callback pattern)

**Key Change**: Callbacks → LangGraph state pattern (fixes duplicate widgets bug)

---

## Phase 2: 7-Pipeline Agents (CRITICAL) ✓

### 2.1 Analyst Agent (Dual-Pass)

| Task | File | Lines | Status | Notes |
|------|------|-------|--------|-------|
| Create analyst signatures | `agent/agent/dspy_signatures/analyst/query_analysis.py` | 80 | ✓ | 8 signatures for query analysis |
| Create insight extractor | `agent/agent/tools/analyst/insight_extractor.py` | 80 | ✓ | With chunking (proven pattern) |
| Create search term extractor | `agent/agent/tools/analyst/search_terms.py` | 60 | ✓ | Few-shot learning |
| Create goal detector | `agent/agent/tools/analyst/goal_detector.py` | 50 | ✓ | GoalDetectorModule |
| Create context analyzer | `agent/agent/tools/analyst/context_analyzer.py` | 70 | ✓ | 3 parallel Predict calls |
| Create data quality checker | `agent/agent/tools/analyst/data_quality_checker.py` | 50 | ✓ | For Pass 2 |
| Create analyst node | `agent/agent/nodes/analyst.py` | 100 | ✓ | Pass 1 + Pass 2 logic |
| Create analyst agent | `agent/agent/agents/analyst.py` | 80 | ✓ | Wraps analyst node |

**R014 Source**: `services/pipeline/analyst.py` (dual-pass pattern)

**Total**: 8 files, ~670 lines

---

### 2.2 Researcher Agent

| Task | File | Lines | Status | Notes |
|------|------|-------|--------|-------|
| Create researcher signatures | `agent/agent/dspy_signatures/researcher/search.py` | 80 | ✓ | 4 signatures for search and structuring |
| Create data structurer | `agent/agent/tools/researcher/data_structurer.py` | 80 | ✓ | Explicit signatures with named fields |
| Create citation builder | `agent/agent/tools/researcher/citation_builder.py` | 100 | ✓ | With relevance scoring |
| Create findings beautifier | `agent/agent/tools/researcher/findings_beautifier.py` | 60 | ✓ | FindingsBeautifierModule |
| Create search executor | `agent/agent/tools/researcher/search_executor.py` | 80 | ✓ | SearXNG integration (async wrapper) |
| Create web scraper | `agent/agent/tools/researcher/web_scraper.py` | 60 | ✓ | scrape_url, extract_main_content |
| Create researcher node | `agent/agent/nodes/researcher.py` | 100 | ✓ | Coordinates all tools |
| Create researcher agent | `agent/agent/agents/researcher.py` | 80 | ✓ | Wraps researcher node |

**R014 Source**: `services/pipeline/researcher.py`

**Total**: 8 files, ~720 lines

---

### 2.3 Contextualizer Agent

| Task | File | Lines | Status | Notes |
|------|------|-------|--------|-------|
| Create contextualizer signatures | `agent/agent/dspy_signatures/contextualizer/reranking.py` | 60 | ✓ | 4 signatures for reranking and filtering |
| Create reranker | `agent/agent/tools/contextualizer/reranker.py` | 60 | ✓ | RelevanceScorerModule |
| Create filter | `agent/agent/tools/contextualizer/filter.py` | 50 | ✓ | ContextFilterModule |
| Create contextualizer | `agent/agent/tools/contextualizer/contextualizer.py` | 60 | ✓ | ContextInjectorModule |
| Create contextualizer node | `agent/agent/nodes/contextualizer.py` | 80 | ✓ | Rerank → filter → inject |
| Create contextualizer agent | `agent/agent/agents/contextualizer.py` | 70 | ✓ | Wraps contextualizer node |

**R014 Source**: `services/pipeline/contextualizer.py`

**Total**: 6 files, ~380 lines

---

### 2.4 Designer Agent (STATE AWARE!)

| Task | File | Lines | Status | Notes |
|------|------|-------|--------|-------|
| Create designer signatures | `agent/agent/dspy_signatures/designer/pov.py` | 60 | ✓ | 3 signatures: DesignPOV, DesignColors, DesignHierarchy |
| Create POV generator | `agent/agent/tools/designer/pov_generator.py` | 60 | ✓ | POVGeneratorModule |
| Create color scheme | `agent/agent/tools/designer/color_scheme.py` | 60 | ✓ | ColorSchemeModule |
| Create hierarchy designer | `agent/agent/tools/designer/hierarchy.py` | 60 | ✓ | HierarchyDesignerModule |
| Create designer node | `agent/agent/nodes/designer.py` | 100 | ✓ | **STATE AWARE**: Checks state.ui before emitting |
| Create designer agent | `agent/agent/agents/designer.py` | 70 | ✓ | Wraps designer node |

**R014 Source**: `services/pipeline/designer.py`

**Critical Fix**: Designer now has state awareness (fixes R014 duplicate widget bug)

**Total**: 6 files, ~410 lines

---

### 2.5 Widget Selector Agent

| Task | File | Lines | Status | Notes |
|------|------|-------|--------|-------|
| Create widget selector signatures | `agent/agent/dspy_signatures/widgets/selection.py` | 80 | ✓ | 2 signatures: SelectWidget, ValidateWidgetChoice |
| Create widget matcher | `agent/agent/agents/widget_matcher.py` | 80 | ✓ | WidgetMatcherModule (few-shot) |
| Create rule-based selector | `agent/agent/agents/rule_based_selector.py` | 60 | ✓ | RuleBasedWidgetSelector |
| Create widget selector node | `agent/agent/nodes/widget_selector.py` | 100 | ✓ | Hybrid rule + LLM logic |
| Create widget selector agent | `agent/agent/agents/widget_selector.py` | 70 | ✓ | Wraps widget selector node |

**R014 Source**: `services/pipeline/widget_selector.py`

**Pattern**: Rule-based for fast path, LLM for complex

**Total**: 5 files, ~390 lines

---

### 2.6 Sequencer & Presenter Agents

| Task | File | Lines | Status | Notes |
|------|------|-------|--------|-------|
| Create delivery planner | `agent/agent/agents/delivery_planner.py` | 80 | ✓ | Staggered delivery (0s, 2s, 3.5s, → 5s) |
| Create sequencer signatures | `agent/agent/dspy_signatures/pipeline/sequencer.py` | 40 | ✓ | 2 signatures: SequenceWidgets, CalculatePacing |
| Create sequencer node | `agent/agent/nodes/sequencer.py` | 80 | ✓ | Order + pace widgets |
| Create sequencer agent | `agent/agent/agents/sequencer.py` | 60 | ✓ | Wraps sequencer node |
| Create presenter signatures | `agent/agent/dspy_signatures/pipeline/presenter.py` | 40 | ✓ | 2 signatures: PresentFindings, QualityCheck |
| Create presenter node | `agent/agent/nodes/presenter.py` | 70 | ✓ | Final polish + QA |
| Create presenter agent | `agent/agent/agents/presenter.py` | 60 | ✓ | Wraps presenter node |

**R014 Source**: `services/pipeline/sequencer.py`, `services/pipeline/presenter.py`

**Total**: 7 files, ~430 lines

---

### 2.7 Complete LangGraph Integration

| Task | File | Lines | Status | Notes |
|------|------|-------|--------|-------|
| Wire all nodes in graph.py | `agent/agent/graph.py` | 100 | ✓ | 8 nodes: analyst_p1 → researcher → contextualizer → analyst_p2 → designer → widget_selector → sequencer → presenter |
| Add conditional edges | `agent/agent/graph.py` | 40 | ✓ | Branching logic if needed |
| Test graph compilation | `tests/agent/test_graph.py` | 50 | ✓ | Verify StateGraph compiles |
| Test state transitions | `tests/agent/test_state_transitions.py` | 80 | ✓ | Verify all 8 transitions |

**Total**: 4 files, ~270 lines

---

## Phase 3: Widget Spawner System (HIGH)

### 3.1 Widget Generators (12 types)

| Task | File | Lines | Status | Notes |
|------|------|-------|--------|-------|
| Create single widget agent | `agent/agent/widget_spawner/single_widget_agent.py` | 80 | ⬜ | Individual widget generation |
| Create multi widget agent | `agent/agent/widget_spawner/multi_widget_agent.py` | 80 | ⬜ | Multi-widget coordination |
| Create intelligent agent | `agent/agent/widget_spawner/intelligent_agent.py` | 80 | ⬜ | Smart UI generation |
| Create chart generator | `agent/agent/widget_spawner/generators/chart_generator.py` | 80 | ⬜ | Chart widget generation |
| Create form generator | `agent/agent/widget_spawner/generators/form_generator.py` | 80 | ⬜ | Form widget generation |
| Create gallery generator | `agent/agent/widget_spawner/generators/gallery_generator.py` | 70 | ⬜ | Gallery widget generation |
| Create progress generator | `agent/agent/widget_spawner/generators/progress_generator.py` | 60 | ⬜ | Progress widget generation |
| Create confirmation generator | `agent/agent/widget_spawner/generators/confirmation_generator.py` | 60 | ⬜ | Confirmation dialog generation |
| Create action generator | `agent/agent/widget_spawner/generators/action_generator.py` | 50 | ⬜ | Action button generation |
| Create voice generator | `agent/agent/widget_spawner/generators/voice_generator.py` | 60 | ⬜ | Voice widget generation |
| Create image generator | `agent/agent/widget_spawner/generators/image_generator.py` | 50 | ⬜ | Image widget generation |
| Create citation card generator | `agent/agent/widget_spawner/generators/citation_card_generator.py` | 70 | ⬜ | Citation card generation |
| Create search result generator | `agent/agent/widget_spawner/generators/search_result_generator.py` | 80 | ⬜ | Search result widget |
| Create hop progress generator | `agent/agent/widget_spawner/generators/hop_progress_generator.py` | 60 | ⬜ | Multi-hop RAG progress |

**R014 Source**: `services/widget_spawner/` (32 files)

**Total**: 14 files, ~920 lines

---

## Phase 4: Multi-Hop Search System (HIGH)

### 4.1 Multi-Hop Agents

| Task | File | Lines | Status | Notes |
|------|------|-------|--------|-------|
| Create multi-hop signatures | `agent/agent/dspy_signatures/multihop/planning.py` | 80 | ⬜ | HopPlanning, HopExecution, HopAssessment, Reflection |
| Create multi-hop agent | `agent/agent/multihop/agents/multihop_agent.py` | 100 | ⬜ | Main ReAct agent |
| Create async execution | `agent/agent/multihop/agents/async_execution.py` | 80 | ⬜ | Async hop execution |
| Create sync forward | `agent/agent/multihop/agents/sync_forward.py` | 80 | ⬜ | Sync forward with reflection |

**R014 Source**: `services/multihop_search/agents/` (20 files)

---

### 4.2 Multi-Hop Tools

| Task | File | Lines | Status | Notes |
|------|------|-------|--------|-------|
| Create hop planner | `agent/agent/multihop/tools/hop_planner.py` | 80 | ⬜ | Plan search hops |
| Create hop executor | `agent/agent/multihop/tools/hop_executor.py` | 80 | ⬜ | Execute individual hops |
| Create hop assessment | `agent/agent/multihop/tools/hop_assessment.py` | 60 | ⬜ | Assess hop relevance |
| Create reflection | `agent/agent/multihop/tools/reflection.py` | 60 | ⬜ | Reflect on results |

**R014 Source**: `services/multihop_search/tools/`

**Total**: 8 files, ~620 lines

---

## Phase 5: Calendar & Additional Tools (MEDIUM)

### 5.1 Calendar Tools

| Task | File | Lines | Status | Notes |
|------|------|-------|--------|-------|
| Create calendar agent | `agent/agent/tools/calendar/calendar_agent.py` | 100 | ⬜ | CalendarAgent (ReAct) |
| Create get_current_date | `agent/agent/tools/calendar/date_tools.py` | 40 | ⬜ | Date utility |
| Create calculate_date_offset | `agent/agent/tools/calendar/date_tools.py` | 40 | ⬜ | Offset utility |
| Create day_of_week | `agent/agent/tools/calendar/date_tools.py` | 30 | ⬜ | Day of week utility |
| Create date_difference | `agent/agent/tools/calendar/date_tools.py` | 40 | ⬜ | Date diff utility |
| Create weekend_check | `agent/agent/tools/calendar/date_tools.py` | 30 | ⬜ | Weekend check utility |

**R014 Source**: `services/tools/calendar/calendar_agent.py`

**Total**: 6 files, ~280 lines

---

### 5.2 Additional Specialist Tools

| Task | File | Lines | Status | Notes |
|------|------|-------|--------|-------|
| Create decision tree executor | `agent/agent/tools/common/decision_tree.py` | 80 | ⬜ | DecisionTreeExecutor |
| Create async wrapper | `agent/agent/tools/common/async_wrapper.py` | 60 | ⬜ | For blocking dependencies |
| Create safe_eval | `agent/agent/tools/common/safe_eval.py` | 40 | ⬜ | Safe calculator evaluation |
| Create widget registry | `agent/agent/tools/ui/widget_registry.py` | 60 | ⬜ | Widget type registry |

**Total**: 4 files, ~240 lines

---

## Phase 6: Application Layer (REQUIRED)

### 6.1 Use Cases

| Task | File | Lines | Status | Notes |
|------|------|-------|--------|-------|
| Create ExecuteAgentQueryUseCase | `agentx/application/use_cases/execute_agent_query.py` | 100 | ⬜ | Non-streaming query execution |
| Create StreamUIUpdateUseCase | `agentx/application/use_cases/stream_ui_update.py` | 80 | ⬜ | Streaming query execution |
| Create CreateSessionUseCase | `agentx/application/use_cases/create_session.py` | 60 | ⬜ | Session creation |
| Create ManageSessionUseCase | `agentx/application/use_cases/manage_session.py` | 80 | ⬜ | Pause/resume/close session |

**Total**: 4 files, ~320 lines

---

### 6.2 DTOs

| Task | File | Lines | Status | Notes |
|------|------|-------|--------|-------|
| Create agent DTOs | `agentx/application/dtos/agent_dtos.py` | 100 | ⬜ | ExecuteAgentQueryCommand, ExecuteAgentQueryResponse |
| Create streaming DTOs | `agentx/application/dtos/streaming_dtos.py` | 80 | ⬜ | StreamChunk, ReasoningStep, ToolCall |
| Create session DTOs | `agentx/application/dtos/session_dtos.py` | 60 | ⬜ | Session-related DTOs |

**Total**: 3 files, ~240 lines

---

### 6.3 Services

| Task | File | Lines | Status | Notes |
|------|------|-------|--------|-------|
| Create AgentOrchestrator | `agentx/application/services/agent_orchestrator.py` | 120 | ⬜ | Coordinates LangGraph + agents |
| Create UIService | `agentx/application/services/ui_service.py` | 100 | ⬜ | UI state management |
| Create MemoryService | `agentx/infrastructure/external/memory_service.py` | 180 | ⬜ | Memory consolidation (from C005) |

**Total**: 3 files, ~400 lines

---

## Phase 7: API Layer (REQUIRED)

### 7.1 Routes

| Task | File | Lines | Status | Notes |
|------|------|-------|--------|-------|
| Create agent routes | `agentx/presentation/api/v1/agent_routes.py` | 120 | ⬜ | /api/v1/agent/query, /api/v1/agent/stream |
| Create session routes | `agentx/presentation/api/v1/session_routes.py` | 80 | ⬜ | /api/v1/session/* endpoints |
| Create health check | `agentx/presentation/api/v1/health.py` | 30 | ⬜ | /health endpoint |

**Total**: 3 files, ~230 lines

---

### 7.2 WebSocket Manager

| Task | File | Lines | Status | Notes |
|------|------|-------|--------|-------|
| Create WebSocket manager | `agentx/infrastructure/external/websocket_manager.py` | 100 | ⬜ | WebSocketManager for streaming |

**Total**: 1 file, ~100 lines

---

## Phase 8: Frontend Types (REQUIRED)

### 8.1 Type Definitions

| Task | File | Lines | Status | Notes |
|------|------|-------|--------|-------|
| Create agent types | `frontend/src/types/agent.ts` | 150 | ⬜ | Zod schemas matching Pydantic |
| Create WebSocket types | `frontend/src/types/websocket.ts` | 100 | ⬜ | Zod schemas for WebSocket messages |
| Create descriptor types | `frontend/src/types/descriptors.ts` | 80 | ⬜ | UI descriptor schemas |

**Total**: 3 files, ~330 lines

---

## Summary Statistics

### File Counts

| Phase | Files | Lines (est.) | Status |
|-------|-------|--------------|--------|
| Phase 1: Infrastructure | 11 | ~340 | ⬜ |
| Phase 2: 7-Pipeline Agents | 46 | ~3,720 | ⬜ |
| Phase 3: Widget Spawner | 14 | ~920 | ⬜ |
| Phase 4: Multi-Hop Search | 8 | ~620 | ⬜ |
| Phase 5: Calendar + Tools | 10 | ~520 | ⬜ |
| Phase 6: Application Layer | 10 | ~960 | ⬜ |
| Phase 7: API Layer | 4 | ~330 | ⬜ |
| Phase 8: Frontend Types | 3 | ~330 | ⬜ |
| **Total** | **106** | **~7,740** | ⬜ |

---

## Verification Steps

### Code Quality

```bash
# Run all quality checks
cd /home/riju279/Documents/Code/XRIG/AgentX/agentx
ruff check . --fix
ruff format .
pyrefly check . --summarize-errors

# Frontend type check
cd /home/riju279/Documents/Code/XRIG/AgentX/frontend
npx tsc --noEmit
```

---

### R014 Alignment Checks

```bash
# Verify signature count matches R014
find agentx/agent/dspy_signatures/ -name "*.py" -exec grep "class.*Signature" {} + | wc -l
# Should return: 69

# Verify tools count matches R014
find agentx/agent/tools/ -name "*.py" -exec grep "^def " {} + | wc -l
# Should return: 50+

# Verify 7-pipeline nodes exist
grep -E "analyst_node|researcher_node|contextualizer_node|designer_node|widget_selector_node|sequencer_node|presenter_node" agentx/agent/graph.py
# Should return: 8 matches (analyst_p1, analyst_p2)
```

---

## Definition of Done

C003-agent-pipeline is **complete** when:

- [ ] All 69 DSPy signatures ported from R014
- [ ] All 50+ tools ported from R014
- [ ] 7-pipeline orchestration implemented (8 nodes in LangGraph)
- [ ] Designer agent has state awareness (fixes duplicate widgets)
- [ ] Multi-hop search system ported
- [ ] Widget spawner system ported (12+ generators)
- [ ] Type conversion utilities implemented (_to_float, _to_bool)
- [ ] Chunking infrastructure implemented (proven pattern)
- [ ] Safe DSPy extraction pattern used throughout
- [ ] All use cases created (ExecuteAgentQuery, StreamUIUpdate)
- [ ] All DTOs created with Pydantic → Zod alignment
- [ ] Frontend Zod schemas match backend Pydantic
- [ ] Zero field name mismatches with R014
- [ ] Zero relative imports (absolute only)
- [ ] All files under 150 lines
- [ ] All quality checks pass (ruff, pyrefly, tsc)
- [ ] LangGraph compiles and executes all 8 nodes
- [ ] Integration tests pass

---

## Rollback Plan

If implementation fails:

1. **Identify failure point**:
   ```bash
   # Check which test failed
   pytest tests/integration/test_agent_pipeline.py -v
   ```

2. **Rollback steps**:
   ```bash
   # Remove created files
   rm -rf agentx/agent/
   rm -rf agentx/application/use_cases/execute_agent_query.py
   rm -rf agentx/application/use_cases/stream_ui_update.py
   rm -rf agentx/presentation/api/v1/agent_routes.py
   rm -rf frontend/src/types/agent.ts frontend/src/types/websocket.ts
   ```

3. **Recovery actions**:
   - Re-run from Phase 1 (Infrastructure)
   - Port each R014 file one at a time
   - Verify each file against R014 before proceeding
   - Run integration tests incrementally

---

## Dependencies Unlocked

This change unlocks:

| Change | Unlocked Feature |
|--------|-----------------|
| **C004-voice-streaming** | Can use agent pipeline for voice interaction (STT → Agent → TTS) |
| **C005-memory-rag** | Can extend RAG agent with consolidation logic |
| **C006-release-plan** | Agent pipeline required for full system integration |
| **C007-frontend** | Server-driven UI needs agent pipeline |

---

## Comparison: Before vs After

### Before (Generic Template)

| Metric | Count |
|--------|-------|
| Signatures | 13 (generic) |
| Tools | ~5 (basic) |
| Agents | 3 (generic) |
| Files | ~28 |

### After (R014 Reality)

| Metric | Count |
|--------|-------|
| Signatures | **69** (from R014) |
| Tools | **50+** (from R014) |
| Agents | **8** (7-pipeline + multi-hop) |
| Files | **106** |

**This is what's needed to make AgentX actually work.**

---

**End of tasks artifact**

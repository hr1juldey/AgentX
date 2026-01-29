# Extract Artifact: c003-agent-pipeline

**Generated**: 2026-01-29
**Change**: c003-agent-pipeline
**Schema**: spec-factory v1
**Source**: R014 Postmortem `/home/riju279/Documents/Code/XRIG/AgentX/docs/learnings/R014_postmortem/`

---

## 1. R014 Implementation Inventory

### 1.1 File Statistics (from Postmortem)

| Category | R014 Count | Real AgentX Target | Status |
|----------|-----------|-------------------|--------|
| **Total Python Files** | 265 | ~80-100 | ⬜ TBD |
| **DSPy Signatures** | 69 | 69 | ⬜ Need to port |
| **DSPy Module Instances** | 134 | 134 | ⬜ Need to port |
| **Tools** | 50+ | 50+ | ⬜ Need to port |
| **Pipeline Agents** | 31 | 7-8 | ⬜ Need to port |

### 1.2 R014 Service Breakdown (from Postmortem)

| Service Category | R014 Files | Port Status |
|------------------|-----------|-------------|
| **Pipeline Agents** | 31 files | ⬜ Need to extract |
| **Widget Spawner** | 32 files | ⬜ Need to extract |
| **Master Agent** | 26 files | ⬜ Need to extract |
| **Multihop Search** | 20 files | ⬜ Need to extract |
| **Tools** | 125 files | ⬜ Need to extract |
| **Hydrators** | 7 files | ❌ Legacy (skip) |
| **Core Services** | 3 files | ⬜ Need to extract |

---

## 2. R014 → AgentX Migration Strategy

### 2.1 Critical Decision: Callback Pattern → LangGraph State Pattern

**R014 Pattern** (Callback-based):
```python
# R014: Nested callbacks for widget delivery
master_agent, delivery_plan_type = use_case.setup_master_agent_with_pipeline(
    widget_callback=send_widget,      # Nested callback
    qa_callback=send_qa_progress,     # Another callback
    progress_callback=send_progress,  # Yet another callback
)
```

**Problems** (from R014 postmortem):
- Designer agent has NO awareness of existing UI state
- Sends duplicate widgets repeatedly
- Hard to test (callback hell)
- No traceability (what UI was shown when?)

**AgentX Pattern** (LangGraph state-based):
```python
# AgentX: State-based UI tracking
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]  # State awareness!
    session_id: str | None
    reasoning_steps: int

# Designer agent checks state before emitting
async def designer_node(state: AgentState):
    existing_widgets = [msg.name for msg in state.get("ui", [])]  # State awareness!
    # Select widget that COMPLEMENTS existing widgets
    push_ui_message(widget_type, widget_props, message=message)
```

**Benefits**:
- ✅ Designer has full UI state awareness (fixes R014 duplicate widget problem)
- ✅ Traceable (LangSmith shows full state history)
- ✅ Testable (state-based, not callback-based)
- ✅ Industry standard (LangSmith/LangChain pattern)

---

## 3. R014 Patterns to Port (from Postmortem)

### 3.1 REQUIRED Patterns (Critical)

| # | Pattern | R014 File | AgentX Location | Priority |
|---|---------|-----------|-----------------|----------|
| 1 | **7-Pipeline Orchestration** | `services/master_agent/master_agent.py` | `agent/agents/master_agent.py` | **CRITICAL** |
| 2 | **Type Conversion Utils** | `services/tools/common/type_utils.py` | `agent/tools/common/type_utils.py` | **CRITICAL** |
| 3 | **Chunking + Iteration** | `services/tools/analyst/insight_extractor.py` | `agent/tools/analyst/chunking.py` | **CRITICAL** |
| 4 | **Safe DSPy Extraction** | Multiple files | All DSPy agents | **CRITICAL** |
| 5 | **Staggered Delivery** | `services/master_agent/delivery_planner.py` | `agent/agents/delivery_planner.py` | **REQUIRED** |
| 6 | **Hybrid Rule + LLM** | `services/pipeline/widget_selector.py` | `agent/agents/widget_selector.py` | **REQUIRED** |
| 7 | **Dual-Pass Analyst** | `services/pipeline/analyst.py` | `agent/agents/analyst.py` | **HIGH** |
| 8 | **Few-Shot Semantic** | `services/tools/selectors/widget_matcher.py` | `agent/agents/widget_matcher.py` | **HIGH** |

### 3.2 7-Pipeline Orchestration (R014 → AgentX)

**R014 Pipeline**:
```
ANALYST (Pass 1) → RESEARCHER → CONTEXTUALIZER → ANALYST (Pass 2)
→ DESIGNER → WIDGET SELECTOR → SEQUENCER → PRESENTER
```

**AgentX Adaptation** (LangGraph nodes):
```python
# agent/graph.py
from agentx.agent.nodes import (
    analyst_node,           # Pass 1: Context analysis
    researcher_node,        # Web search + data structuring
    contextualizer_node,    # Rerank → filter → contextualize
    analyst_pass2_node,     # Pass 2: Data quality judgment
    designer_node,          # POV + colors + hierarchy (STATE AWARE!)
    widget_selector_node,   # Hybrid rule + LLM selection
    sequencer_node,         # Order + pace widgets
    presenter_node,         # Final polish + QA
)

def create_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    graph.add_node("analyst_p1", analyst_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("contextualizer", contextualizer_node)
    graph.add_node("analyst_p2", analyst_pass2_node)
    graph.add_node("designer", designer_node)
    graph.add_node("widget_selector", widget_selector_node)
    graph.add_node("sequencer", sequencer_node)
    graph.add_node("presenter", presenter_node)

    graph.set_entry_point("analyst_p1")
    graph.add_edge("analyst_p1", "researcher")
    graph.add_edge("researcher", "contextualizer")
    graph.add_edge("contextualizer", "analyst_p2")
    graph.add_edge("analyst_p2", "designer")
    graph.add_edge("designer", "widget_selector")
    graph.add_edge("widget_selector", "sequencer")
    graph.add_edge("sequencer", "presenter")
    graph.add_edge("presenter", END)
    return graph
```

### 3.3 R014 DSPy Signatures Inventory (69 Total)

**From `services/` extraction**:

#### Analyst Signatures (8 signatures)
```
services/pipeline/analyst.py:
- AnalyzeQueryContext
- ExtractInsights
- DetectGoals
- ExtractSearchTerms

services/tools/analyst/query_analyzer.py:
- Decision tree analysis (chunking pattern)

services/tools/analyst/insight_extractor.py:
- ExtractInsightsChunk (with chunking)

services/tools/analyst/search_terms.py:
- ExtractSearchTerms (few-shot)

services/tools/analyst/goal_detector.py:
- DetectUserGoals
```

#### Researcher Signatures (12 signatures)
```
services/pipeline/researcher.py:
- ExecuteSearch
- StructureData
- BeautifyFindings

services/tools/researcher/search_executor.py:
- SearXNGSearch

services/tools/researcher/data_structurer.py:
- StructureDataChunk (explicit fields)

services/tools/researcher/citation_builder.py:
- AssessCitation (with _parse_relevance_score)

services/tools/researcher/findings_beautifier.py:
- BeautifySummary
```

#### Contextualizer Signatures (10 signatures)
```
services/pipeline/contextualizer.py:
- ReorderContext
- FilterContext
- InjectContext

services/tools/contextualizer/reranker.py:
- ScoreRelevance

services/tools/contextualizer/filter.py:
- ShouldInclude

services/tools/contextualizer/contextualizer.py:
- AddContext
```

#### Designer Signatures (8 signatures)
```
services/pipeline/designer.py:
- DesignPOV
- DesignColors
- DesignHierarchy

services/tools/designer/pov_generator.py:
- GeneratePOV

services/tools/designer/color_scheme.py:
- SelectColors

services/tools/designer/hierarchy.py:
- DesignHierarchy
```

#### Widget Selector Signatures (15 signatures)
```
services/pipeline/widget_selector.py:
- SelectWidget (hybrid rule + LLM)

services/tools/selectors/widget_matcher.py:
- SelectWidgetSignature (few-shot semantic)

services/widget_spawner/ (32 files, 15+ signatures):
- SingleWidgetAgent
- MultiWidgetAgent
- IntelligentWidgetAgent
- ChartGenerator
- FormGenerator
- GalleryGenerator
- etc.
```

#### Sequencer & Presenter Signatures (6 signatures)
```
services/pipeline/sequencer.py:
- SequenceWidgets
- CalculatePacing

services/pipeline/presenter.py:
- PresentFindings
- QualityCheck
```

#### Multi-Hop Search Signatures (10+ signatures)
```
services/multihop_search/agents/multihop_agent.py:
- HopPlanning
- HopExecution
- HopAssessment
- Reflection
```

### 3.4 R014 Tools Inventory (50+ Tools)

**From `services/tools/` extraction**:

#### Analyst Tools (8 tools)
```python
# services/tools/analyst/
- query_analyzer.py: DecisionTreeAnalyzer
- insight_extractor.py: InsightExtractorModule (with chunking)
- search_terms.py: SearchTermExtractorModule
- goal_detector.py: GoalDetectorModule
- context_analyzer.py: ContextAnalyzerModule (3 parallel calls)
- data_quality_checker.py: DataQualityCheckerModule
```

#### Researcher Tools (12 tools)
```python
# services/tools/researcher/
- search_executor.py: searxng_search, searxng_search_async
- data_structurer.py: DataStructurerModule (explicit signatures)
- citation_builder.py: CitationBuilderModule (with _parse_relevance_score)
- findings_beautifier.py: FindingsBeautifierModule
- web_scraper.py: scrape_url, extract_main_content
```

#### Contextualizer Tools (6 tools)
```python
# services/tools/contextualizer/
- reranker.py: RelevanceScorerModule
- filter.py: ContextFilterModule
- contextualizer.py: ContextInjectorModule
```

#### Designer Tools (8 tools)
```python
# services/tools/designer/
- pov_generator.py: POVGeneratorModule
- color_scheme.py: ColorSchemeModule
- hierarchy.py: HierarchyDesignerModule
- typography.py: TypographySelectorModule
```

#### Widget Selector Tools (10+ tools)
```python
# services/tools/selectors/
- widget_matcher.py: WidgetMatcherModule (few-shot semantic)
- rule_based_selector.py: RuleBasedWidgetSelector
```

#### Calendar Tools (5 tools)
```python
# services/tools/calendar/
- calendar_agent.py: CalendarAgent (ReAct)
- get_current_date, calculate_date_offset, etc.
```

#### UI Widget Tools (12+ tools)
```python
# services/tools/ui/
- render_markdown_block
- render_card
- render_form
- render_progress
- request_confirmation
- update_progress
- show_chart
- show_gallery
- etc.
```

#### Common Utilities (3 critical files)
```python
# services/tools/common/
- type_utils.py: _to_float, _to_bool (CRITICAL - LLM returns text)
- chunking.py: MAX_CHUNK_SIZE, OVERLAP, ITERATIONS constants
- decision_tree.py: DecisionTreeExecutor
```

### 3.5 Multi-Hop Search System (20 files)

**From `services/multihop_search/`**:
```
services/multihop_search/
├── agents/
│   ├── multihop_agent.py         # Main ReAct agent
│   ├── async_execution.py        # Async hop execution
│   └── sync_forward.py           # Sync forward with reflection
├── tools/
│   ├── hop_planner.py            # Plan search hops
│   ├── hop_executor.py           # Execute individual hops
│   ├── hop_assessment.py         # Assess hop relevance
│   └── reflection.py             # Reflect on results
└── signatures/
    ├── HopPlanningSignature
    ├── HopExecutionSignature
    ├── HopAssessmentSignature
    └── ReflectionSignature
```

### 3.6 Widget Spawner System (32 files)

**From `services/widget_spawner/`**:
```
services/widget_spawner/
├── single_widget_agent.py         # Individual widget generation
├── multi_widget_agent.py          # Multi-widget coordination
├── intelligent_agent.py           # Smart UI generation
└── generators/
    ├── chart_generator.py         # Chart widgets
    ├── form_generator.py          # Form widgets
    ├── gallery_generator.py       # Gallery widgets
    ├── progress_generator.py      # Progress widgets
    ├── confirmation_generator.py  # Confirmation dialogs
    └── ...
```

---

## 4. R014 Working DSPy Patterns (from Postmortem)

### 4.1 Pattern 1: Chunking + Iteration for Large Inputs

**Module**: InsightExtractorModule
**Status**: ✅ 4/4 tests pass
**Token Efficiency**: 3x 40-token calls = 120 total vs 1x 200-token call

```python
MAX_CHUNK_SIZE = 500
OVERLAP = 100
ITERATIONS = 3

class InsightExtractorModule(dspy.Module):
    def forward(self, query: str, document_text: str) -> dspy.Prediction:
        if len(document_text) <= MAX_CHUNK_SIZE:
            return self._extract_single(document_text)
        return self._extract_iterative(document_text)

    def _extract_iterative(self, text: str) -> dspy.Prediction:
        insights = []
        for i in range(ITERATIONS):
            start = i * (MAX_CHUNK_SIZE - OVERLAP)
            end = start + MAX_CHUNK_SIZE
            chunk = text[start:end]
            result = self.extract_chunk(chunk=chunk)
            insights.extend(result.insights.split("\n"))
        return dspy.Prediction(insights=insights)
```

**Port to**: `agentx/agent/tools/analyst/insight_extractor.py`

### 4.2 Pattern 2: Numeric Score Parsing with Fallbacks

**Module**: CitationBuilderModule
**Status**: ✅ 3/3 tests pass

```python
def _parse_relevance_score(score_str: str) -> float:
    """Parse relevance score from LLM output with multiple fallbacks."""

    # Fallback 1: Direct float parsing
    try:
        return float(score_str.strip())
    except (ValueError, TypeError):
        pass

    # Fallback 2: Regex extraction
    import re
    match = re.search(r'(\d+\.?\d*)', str(score_str))
    if match:
        value = float(match.group(1))
        if value > 1.0:
            return value / 100.0
        return value

    # Fallback 3: Keyword mapping
    lower = str(score_str).lower().strip()
    mappings = {
        "high": 0.8, "very high": 0.9, "excellent": 0.95,
        "medium": 0.5, "moderate": 0.5,
        "low": 0.2, "very low": 0.1, "poor": 0.1,
    }
    return mappings.get(lower, 0.5)
```

**Port to**: `agentx/agent/tools/common/type_utils.py`

### 4.3 Pattern 3: Explicit Signatures with ChainOfThought

**Module**: DataStructurerModule
**Status**: ✅ 3/3 tests pass

```python
class StructureDataChunk(dspy.Signature):
    """Structure raw data into key facts, trends, and comparisons.

    Output format:
    - key_facts: Numbered list 1-5
    - trends: Numbered list 1-3
    - comparisons: Numbered list 1-2
    """
    data_chunk = dspy.InputField(desc="Data to structure (max 500 chars)")
    key_facts = dspy.OutputField(desc="Key facts from data, numbered 1-5")
    trends = dspy.OutputField(desc="Trends from data, numbered 1-3")
    comparisons = dspy.OutputField(desc="Comparisons from data, numbered 1-2")

# Use ChainOfThought for better reasoning
self.structure = dspy.ChainOfThought(StructureDataChunk)
```

**Port to**: All R014 signatures

### 4.4 Pattern 4: Few-Shot Semantic Learning

**Module**: WidgetMatcherModule
**Status**: ✅ 8/8 tests pass

```python
class SelectWidgetSignature(dspy.Signature):
    """Select appropriate widgets based on query intent and data characteristics.

    SEMANTIC PATTERNS (learn from these examples):

    Example 1:
    Query: "Show real-time stock prices"
    Data: numerical_time_series
    Selected: chart
    Reasoning: Stock prices are time-series data that change continuously.

    Example 2:
    Query: "What's the weather like?"
    Data: current_conditions
    Selected: card

    Example 3:
    Query: "Find articles about Python"
    Data: text_documents
    Selected: gallery

    NOTE: These are EXAMPLES to learn from, not hard-coded rules.
    """
    query = dspy.InputField(desc="User's natural language query")
    data_type = dspy.InputField(desc="Type of data available")
    selected_widgets = dspy.OutputField(desc="JSON array of widget names")
    rationale = dspy.OutputField(desc="Reasoning for widget selection")
```

**Port to**: `agentx/agent/agents/widget_matcher.py`

### 4.5 Pattern 5: ReAct Instead of CodeAct

**Module**: CalendarAgent
**Status**: ✅ 5/5 tests pass (was 0/5 with CodeAct)

```python
# After: ReAct (more flexible)
self.react = dspy.ReAct(
    signature=CalendarQuery,
    tools=[get_current_date, calculate_date_offset, ...],
    max_iters=3,
)
```

**Port to**: All ReAct agents in AgentX

### 4.6 Pattern 6: Safe DSPy Result Extraction

**Pattern**: Always use hasattr + .get() for DSPy results

```python
result = self.some_module(input=data)
safe_result = result if hasattr(result, "get") else {}
value = safe_result.get("key", default_value)
```

**Port to**: All DSPy agent `forward()` methods

---

## 5. Staggered Widget Delivery Pattern

**R014 File**: `services/master_agent/delivery_planner.py`

**Pattern**: Deliver widgets progressively (0s, 2s, 3.5s, approaching 5s)

```python
@dataclass
class DeliveryPlan:
    widgets: list  # UIDescriptors
    delays: list[float]  # Seconds for each widget
    total_duration: float  # Total time

# Pacing Formula:
# Widget 1: 0s (immediate)
# Widget 2: ~2s
# Widget 3: ~3.5s
# Widget N: Approaches 5s
```

**Port to**: `agentx/agent/agents/delivery_planner.py`

**Benefits**:
- Less overwhelming for user
- Consultant-style presentation
- Progressive disclosure
- Better UX perception

---

## 6. Hybrid Rule-Based + LLM Selection Pattern

**R014 File**: `services/pipeline/widget_selector.py`

**Pattern**: Rules for common cases, LLM for complex

```python
# Rule-Based (Fast):
if multiple_urls:
    return ["gallery"]
elif single_url:
    return ["image", "markdown"]

# LLM-Based (Context-Aware):
else:
    return WidgetMatcherModule(query=query, data_type=data_type)

# Fallback:
if data_error:
    return ["markdown"]
elif visual_error:
    return ["card"]
```

**Port to**: `agentx/agent/agents/widget_selector.py`

---

## 7. Specification Drafts (Updated for R014 Reality)

### 7.1 C003-001: Port 7-Pipeline Orchestration

**Purpose**: Port R014's 7-pipeline master agent to LangGraph

**R014 Source**: `services/master_agent/master_agent.py` (26 files)

**AgentX Target**:
```
agentx/agent/
├── agents/
│   ├── master_agent.py         # Main orchestrator (LangGraph version)
│   ├── analyst.py              # Dual-pass analyst
│   ├── researcher.py           # Web search + data structuring
│   ├── contextualizer.py       # Rerank → filter → contextualize
│   ├── designer.py             # POV + colors + hierarchy (STATE AWARE!)
│   ├── widget_selector.py      # Hybrid rule + LLM
│   ├── sequencer.py            # Order + pace widgets
│   └── presenter.py            # Final polish + QA
├── graph.py                    # LangGraph StateGraph
└── state.py                    # AgentState with ui_message_reducer
```

**Key Changes from R014**:
- ✅ Callback pattern → LangGraph state pattern
- ✅ Nested callbacks → `ui_message_reducer`
- ✅ Designer gets state awareness (fixes duplicate widgets)
- ✅ Full traceability via LangSmith

### 7.2 C003-002: Port 69 DSPy Signatures

**Purpose**: Port all R014 DSPy signatures to AgentX

**R014 Source**: 19 signature files across services/

**AgentX Target**:
```
agentx/agent/dspy_signatures/
├── analyst/
│   ├── query_analysis.py       # 4 signatures
│   ├── insight_extraction.py   # 2 signatures
│   ├── search_terms.py         # 1 signature
│   └── goal_detection.py       # 1 signature
├── researcher/
│   ├── search.py               # 3 signatures
│   ├── data_structuring.py     # 2 signatures
│   ├── citations.py            # 2 signatures
│   └── beautification.py       # 2 signatures
├── contextualizer/
│   ├── reranking.py            # 2 signatures
│   ├── filtering.py            # 2 signatures
│   └── injection.py            # 2 signatures
├── designer/
│   ├── pov.py                  # 2 signatures
│   ├── colors.py               # 2 signatures
│   └── hierarchy.py            # 2 signatures
├── widgets/
│   ├── selection.py            # 15+ signatures
│   ├── generation.py           # 12+ signatures
│   └── spawner.py              # 5+ signatures
└── multihop/
    ├── planning.py             # 3 signatures
    ├── execution.py            # 3 signatures
    └── reflection.py           # 2 signatures
```

**Total**: 69 signatures across 20+ files

### 7.3 C003-003: Port 50+ Tools

**Purpose**: Port all R014 tools to AgentX

**R014 Source**: 125 tool files in services/tools/

**AgentX Target**:
```
agentx/agent/tools/
├── common/
│   ├── type_utils.py           # _to_float, _to_bool (CRITICAL)
│   ├── chunking.py             # MAX_CHUNK_SIZE, OVERLAP, ITERATIONS
│   └── decision_tree.py        # DecisionTreeExecutor
├── analyst/
│   ├── query_analyzer.py       # DecisionTreeAnalyzer
│   ├── insight_extractor.py    # InsightExtractorModule (with chunking)
│   ├── search_terms.py         # SearchTermExtractorModule
│   ├── goal_detector.py        # GoalDetectorModule
│   ├── context_analyzer.py     # ContextAnalyzerModule
│   └── data_quality_checker.py # DataQualityCheckerModule
├── researcher/
│   ├── search_executor.py      # searxng_search, searxng_search_async
│   ├── data_structurer.py      # DataStructurerModule
│   ├── citation_builder.py     # CitationBuilderModule
│   ├── findings_beautifier.py  # FindingsBeautifierModule
│   ├── web_scraper.py          # scrape_url, extract_main_content
│   └── reranker.py             # RelevanceScorerModule
├── designer/
│   ├── pov_generator.py        # POVGeneratorModule
│   ├── color_scheme.py         # ColorSchemeModule
│   └── hierarchy.py            # HierarchyDesignerModule
├── widgets/
│   ├── widget_matcher.py       # WidgetMatcherModule (few-shot)
│   ├── rule_based_selector.py  # RuleBasedWidgetSelector
│   ├── chart_generator.py      # Chart widgets
│   ├── form_generator.py       # Form widgets
│   ├── gallery_generator.py    # Gallery widgets
│   └── ...
├── calendar/
│   └── calendar_agent.py       # CalendarAgent (ReAct)
└── multihop/
    ├── hop_planner.py          # Plan search hops
    ├── hop_executor.py         # Execute individual hops
    ├── hop_assessment.py       # Assess hop relevance
    └── reflection.py           # Reflect on results
```

**Total**: 50+ tools across 30+ files

### 7.4 C003-004: Port Widget Spawner System

**Purpose**: Port R014's widget generation system

**R014 Source**: 32 files in services/widget_spawner/

**AgentX Target**:
```
agentx/agent/widget_spawner/
├── single_widget_agent.py      # Individual widget generation
├── multi_widget_agent.py       # Multi-widget coordination
├── intelligent_agent.py        # Smart UI generation
└── generators/
    ├── chart_generator.py      # Chart widgets
    ├── form_generator.py       # Form widgets
    ├── gallery_generator.py    # Gallery widgets
    ├── progress_generator.py   # Progress widgets
    ├── confirmation_generator.py # Confirmation dialogs
    └── ...
```

**Total**: 12+ generator types

### 7.5 C003-005: Port Multi-Hop Search

**Purpose**: Port R014's multi-hop search with reflection

**R014 Source**: 20 files in services/multihop_search/

**AgentX Target**:
```
agentx/agent/multihop/
├── agents/
│   ├── multihop_agent.py       # Main ReAct agent
│   ├── async_execution.py      # Async hop execution
│   └── sync_forward.py         # Sync forward with reflection
├── tools/
│   ├── hop_planner.py          # Plan search hops
│   ├── hop_executor.py         # Execute individual hops
│   ├── hop_assessment.py       # Assess hop relevance
│   └── reflection.py           # Reflect on results
└── signatures/
    ├── HopPlanningSignature
    ├── HopExecutionSignature
    ├── HopAssessmentSignature
    └── ReflectionSignature
```

**Total**: 10+ signatures, 4 tools, 3 agents

---

## 8. Dependencies on Other Specs

| Spec | Dependency Type | Rationale |
|------|-----------------|-----------|
| **C001-folder-structure** | **BLOCKING** | Defines file structure for agent/, tools/, agents/ |
| **C002-data-contracts** | **BLOCKING** | Provides UI descriptors used by widget generators |
| **C004-voice-streaming** | None | Independent |
| **C005-memory-rag** | None | Overlaps multi-hop search |
| **C006-release-plan** | Requires C003 | Release plan depends on agent pipeline |
| **C007-frontend** | Requires C003 | Server-driven UI needs agent pipeline |
| **C008-organic-ui** | None | Visual layer only |
| **C009-ui-polish** | None | Visual polish only |

---

## 9. Critical Rules (from R014 Postmortem)

1. **ALWAYS assume text outputs** - Convert with fallbacks (_to_float, _to_bool)
2. **ALWAYS chunk large inputs** - Prevents corruption (MAX_CHUNK_SIZE=500, OVERLAP=100)
3. **ALWAYS use ReAct** - For small LLMs with tools (CodeAct fails)
4. **ALWAYS use few-shot examples** - For classification/selection tasks
5. **ALWAYS use explicit signatures** - Named output fields (no generic "data -> structured_data")
6. **ALWAYS track connection state** - WebSocket robustness
7. **NEVER trust types** - LLMs return strings
8. **NEVER use relative imports** - Absolute imports only (CLAUDE_POLICY.md)

---

## 10. Next Steps

This extract.md now contains:
- ✅ R014 file inventory (265 files, 69 signatures, 134 modules, 50+ tools)
- ✅ 7-pipeline orchestration pattern
- ✅ 69 DSPy signatures breakdown
- ✅ 50+ tools inventory
- ✅ Multi-hop search system
- ✅ Widget spawner system
- ✅ 7 working DSPy patterns (tested, 97% pass rate)
- ✅ Migration strategy (callbacks → LangGraph state)

**Next artifacts to update**:
1. **tasks.md** - Replace generic tasks with actual R014 porting tasks
2. **specs/** - Add C003-001 through C003-005 specs for major components
3. **design.md** - Update with LangGraph + R014 patterns architecture

---

**Next Artifact**: validate.md

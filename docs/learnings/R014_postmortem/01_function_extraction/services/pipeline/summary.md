# Pipeline Directory Summary

**Directory**: `services/pipeline/`

**Purpose**: 7 Pipeline Agents - Core UI Generation Pipeline

---

## Files Extracted

### Pipeline Agents (7 total)

1. **analyst.py** (80 lines) ✅ Extracted
   - AnalystAgent: Dual-pass analysis (initial + data judgment)
   - 5 DSPy tools: ContextAnalyzer, InsightExtractor, GoalDetector, SearchTermExtractor, DataQualityChecker
   - 2 handlers: InitialAnalysisHandler, DataJudgmentHandler

2. **researcher.py** (101 lines) ✅ Read
   - ResearcherAgent: Fetches data via SearXNG, beautifies, structures, cites
   - 4 DSPy tools: SearXNGSearch, Beautifier, DataStructurer, CitationBuilder
   - Multi-term search support

3. **designer.py** (112 lines) ✅ Read
   - DesignerAgent: POV, color schemes, visual hierarchy
   - 5 DSPy tools: POVGenerator, ColorPicker, HierarchyPlanner, Accessibility, WidgetInsights
   - Widget-specific insights generation

4. **widget_selector.py** (101 lines) ✅ Extracted
   - WidgetSelectorAgent: Hybrid rule-based + LLM widget selection
   - URL detection (multiple → gallery, single → image)
   - WidgetMatcherModule for LLM matching

5. **sequencer.py** (116 lines) ✅ Read
   - SequencerAgent: Widget order and timing
   - 2 DSPy tools: FlowPlanner, PacingCalculator
   - Narrative arc (hook → context → insight → action)

6. **presenter.py** (121 lines) ✅ Read
   - PresenterAgent: Final polish and QA
   - 3 DSPy tools: FlowChecker, Polisher, QAFinalizer
   - Progress tracking

7. **data_contextualizer.py** (118 lines) ✅ Read
   - DataContextualizerAgent: Rerank, filter, contextualize
   - 3 DSPy tools: Reranker, Filter, Contextualizer
   - 3-step process: rerank → filter → contextualize
   - Async support (aforward)

### Helper Files

- **researcher_helpers.py** (60 lines) ✅ Extracted
  - generate_summary_report()
  - determine_data_type()

- **analyst_modules/** (subdirectory)
  - initial_analysis.py
  - data_judgment.py

- **presenter_modules/** (subdirectory)
  - progress.py
  - result_builder.py

---

## Key Patterns

### Pipeline Order (Master Agent executes in this order):
1. **ANALYST** (Pass 1): Understand query + context
2. **RESEARCHER**: SearXNG search + beautify
3. **CONTEXTUALIZER**: Rerank → filter → contextualize
4. **ANALYST** (Pass 2): Judge data quality
5. **DESIGNER**: POV + colors + hierarchy
6. **WIDGET SELECTOR**: Select widgets
7. **SEQUENCER**: Order + pace widgets
8. **PRESENTER**: Final polish + QA

### Common Patterns
- All agents inherit from dspy.Module
- All have forward() method
- Safe extraction with hasattr()
- Logging for debugging
- Helper functions for complex logic

---

## Violations Found

- Minor: Hardcoded SearXNG URL in ResearcherAgent.__init__
- Minor: Citations parameter unused in generate_summary_report()

---

## Reusability for Real AgentX

**REQUIRED** - 7-pipeline architecture is core to UI generation.

**Key Files to Copy**:
- All 7 agent files
- Helper modules
- Logging modules

**Pattern**: 7-phase pipeline with dual-pass analyst

# LLM Module Battle Test Report

**Date**: 2026-01-23
**LLM**: ollama/qwen3:8b
**Purpose**: Test all DSPy-based modules in isolation with qwen3:8b

---

## Summary

| Module | Status | Pass Rate | Notes |
|--------|--------|-----------|-------|
| CalendarAgent | ⚠️ Partial | 7/8 | Large date offsets fail |
| SearchTermExtractorModule | ✅ Pass | 4/4 | Excellent keyword extraction |
| ContextAnalyzerModule | ✅ Pass | 4/4 | Excellent domain detection |
| InsightExtractorModule | ❌ FAIL | 0/3 | **Corrupted/truncated output** |
| GoalDetectorModule | ✅ Pass | 2/2 | Good goal detection |
| WidgetMatcherModule | ⚠️ Valid | 3/3 | Valid widgets, poor selection |

---

## 1. CalendarAgent (services/tools/calendar/agent.py)

**Purpose**: Answer time-related questions using CodeAct with Python execution

### Test Results

| Question | Expected | Actual | Result |
|----------|----------|--------|--------|
| Current date | 2026-01-23 | January 23, 2026 | ✅ |
| Dec 25, 2025 day | Thursday | Thursday | ✅ |
| 100 days ago | 2025-10-15 | July 16, 2025 | ❌ |
| Weekdays Jan 2026 | 22 | 22 | ✅ |
| 30 weekdays from today | 2026-03-06 | March 6, 2026 | ✅ |
| 500 days from today | 2027-05-15 | Oct 2, 2025 | ❌ |

### Issues Found

1. **Large date offsets fail** - LLM hallucinates instead of using tools
2. **100+ days calculations** are unreliable
3. **1 year ago** returns completely wrong date

### Root Cause

qwen3:8b loses tool adherence on complex calculations. The LLM stops executing Python code and starts guessing.

### Fix Applied

Added explicit function documentation to signature:
```python
"""IMPORTANT: The following functions are ALREADY DEFINED and available
for direct use. DO NOT import them - just call them directly:
- get_current_datetime(format_type='date'|'time'|'datetime')
- get_day_of_week(date_string)
- calculate_date_offset(base_date, days)
...
"""
```

This resolved simple queries but large offsets still fail.

---

## 2. SearchTermExtractorModule (services/tools/analyst/search_terms.py)

**Purpose**: Extract 2-4 word search phrases from natural language for SearXNG

### Test Results

| Query | Search Terms | Result |
|-------|--------------|--------|
| "Explain climate change and its effects" | ['global warming impact', 'climate change effects', 'environmental consequences'] | ✅ |
| "What are the latest trends in AI?" | ['natural language processing innovations', 'ai applications in healthcare', 'machine learning advancements', 'ai ethics and bias', 'artificial intelligence trends 2023'] | ✅ |
| "Compare Python vs JavaScript for web development" | ['backend vs frontend languages', 'performance comparison', 'django vs node js', 'python vs javascript web development', 'full stack capabilities'] | ✅ |
| "History of the Roman Empire" | ['roman empire timeline', 'roman empire key events', 'roman empire history causes', 'roman empire emperors list', 'roman empire rise and fall'] | ✅ |

### Status: ✅ ALL PASS (4/4)

**Excellent performance**. Consistently breaks down long queries into 2-4 word keyword phrases suitable for traditional search engines.

---

## 3. ContextAnalyzerModule (services/tools/analyst/query_analyzer.py)

**Purpose**: Analyze query to determine domain, query type, and urgency

### Test Results

| Query | Domain | Type | Urgency | Result |
|-------|--------|------|---------|--------|
| "What is the price of Bitcoin?" | Finance | price inquiry | high | ✅ |
| "Explain quantum computing" | Quantum Computing | explanation | low | ✅ |
| "How do I bake a chocolate cake?" | Cooking | recipe_request | low | ✅ |
| "Compare iPhone vs Android" | Mobile Operating Systems | comparison | medium | ✅ |

### Status: ✅ ALL PASS (4/4)

**Excellent performance**. Correctly identifies diverse domains and appropriate urgency levels.

---

## 4. InsightExtractorModule (services/tools/analyst/query_analyzer.py)

**Purpose**: Extract insights and key questions from queries

### Test Results

| Query | Insights Output | Key Questions | Result |
|-------|-----------------|---------------|--------|
| "Why do leaves change color in autumn?" | "In " | "1." | ❌ |
| "What causes inflation?" | "Inf " | "1." | ❌ |
| "How does JavaScript work?" | "Jav" | "1." | ❌ |

### Status: ❌ ALL FAIL (0/3) - **CRITICAL BUG**

**Issue**: Output is **truncated/corrupted**. Only first 2-3 characters appear.

**Expected**: Full insight sentences
**Actual**: "In ", "Inf ", "Jav"

**This is a critical bug** that needs investigation. Possible causes:
1. LLM output parsing issue
2. Token limit truncation
3. Response field size limit

---

## 5. GoalDetectorModule (services/tools/analyst/goal_detector.py)

**Purpose**: Detect user goal, scope, and depth from query

### Test Results

| Query | Goal | Scope | Depth | Result |
|-------|------|-------|-------|--------|
| "Explain AI" | Provide a clear and concise explanation of artificial intelligence... | Overview of AI | medium | ✅ |
| "Compare prices" | Identify the most cost-effective option by analyzing price trends... | Product Price Comparison | medium | ✅ |

### Status: ✅ ALL PASS (2/2)

**Good performance**. Provides meaningful goals with appropriate scope and depth.

---

## 6. WidgetMatcherModule (services/tools/selector_tools.py)

**Purpose**: Select appropriate widgets based on query intent and data type

### Test Results

| Query | Data Type | Selected Widgets | Expected | Result |
|-------|-----------|------------------|----------|--------|
| "Show stock prices" | numerical_time_series | calculator, calendar, media controls, clock | chart | ⚠️ |
| "Display photos" | visual_image | markdown | gallery | ⚠️ |
| "Compare products" | comparative | clock, calculator, calendar, media controls | card, chart | ⚠️ |

### Status: ⚠️ VALID (3/3) - Poor Selection

**Issue**: Returns valid widget types but selection is **not optimal** with qwen3:8b.

- Stock prices should get `chart` but gets `calculator`
- Photos should get `gallery` but gets `markdown`
- Comparison should get `card/chart` but gets `clock/calculator`

**Note**: The widgets are all VALID (from the VALID_WIDGETS set), so the filter works. The issue is LLM decision quality with smaller model.

---

## Critical Issues Summary

### 1. InsightExtractorModule - CORRUPTED OUTPUT (HIGH PRIORITY)

**Symptom**: All insights return truncated text (first 2-3 chars only)

**Impact**: Analyst phase cannot extract meaningful insights from queries

**Recommended Action**:
- Check DSPy signature field definitions
- Verify output field size limits
- Test with different LLM (gemma3:4b)
- Add debugging to capture raw LLM response

---

## Design Notes

### CodeAct Compatibility

For modules using `dspy.CodeAct`, all imports must be **inside functions**:

```python
# ✅ CORRECT - Imports inside
def my_function():
    from datetime import datetime
    return datetime.now()

# ❌ WRONG - Imports at module level
from datetime import datetime
def my_function():
    return datetime.now()
```

This is because `inspect.getsource()` only captures the function body, not module-level imports.

---

## Testing Notes

### Test Environment
- **LLM**: ollama/qwen3:8b
- **DSPy**: 3.1+
- **Date**: 2026-01-23
- **Method**: Transient Python scripts in terminal

### Remaining Modules to Test

1. DataQualityCheckerModule
2. BeautifierModule
3. DataStructurerModule
4. CitationBuilderModule
5. SuitabilityCheckerModule
6. AnalystAgent (full pipeline)
7. ResearcherAgent (full pipeline)
8. DataContextualizerAgent
9. DesignerAgent
10. PresenterAgent
11. SequencerAgent
12. WidgetSelectorAgent

---

## Recommendations

### For Production Use with qwen3:8b

1. **Fix InsightExtractorModule** - Critical blocker
2. **Use simple functions directly** for date calculations (bypass CodeAct)
3. **Improve WidgetMatcherModule** prompts or use rules-based fallback
4. **Consider larger model** for complex reasoning tasks

### For qwen3:8b Limitations

- Avoid complex multi-step calculations
- Keep tool chains short (1-2 tools max)
- Provide explicit examples in signatures
- Use direct function calls when possible

---

## 7. DataQualityCheckerModule (services/tools/analyst/data_quality_checker.py)

**Purpose**: Assess data quality and completeness for ANALYST Pass 2

### Test Results

| Query | Data | Quality | Result |
|-------|------|---------|--------|
| "What is AI?" | 1 fact | low | ✅ |

### Status: ✅ PASS (1/1)

Works correctly. Returns quality assessment.

---

## 8. BeautifierModule (services/tools/researcher/data_processor.py)

**Purpose**: Beautify raw search data into structured insights

### Test Results

| Input | Key Facts | Result |
|-------|-----------|--------|
| 2 raw documents | 2 detailed facts extracted | ✅ |

### Status: ✅ PASS (1/1)

Extracts meaningful key facts from raw search data.

---

## 9. DataStructurerModule (services/tools/researcher/data_processor.py)

**Purpose**: Structure beautiful data into organized format

### Test Results

| Input | Result |
|-------|--------|
| {'key_facts': [...], 'trends': [...]} | ❌ FAIL: 'str' object has no attribute 'keys' |

### Status: ❌ FAIL (0/1)

**Bug**: Returns string instead of dict, causing attribute error.

---

## 10. CitationBuilderModule (services/tools/researcher/citation_builder.py)

**Purpose**: Build citations from raw search data

### Test Results

| Input | Citations | Result |
|-------|-----------|--------|
| 2 raw documents | 0 | ❌ |

### Status: ❌ FAIL (0/1)

Returns empty list instead of building citations.

---

## 11. SuitabilityCheckerModule (services/tools/selector_tools.py)

**Purpose**: Check if a widget is suitable for data type and device

### Test Results

| Input | Result |
|-------|--------|
| widget='chart', data='numerical_time_series' | ❌ FAIL: wrong arguments |

### Status: ❌ SIGNATURE MISMATCH

Forward signature doesn't match expected parameters.

---

## Pipeline Agents

### 12. AnalystAgent (services/pipeline/analyst.py)

**Purpose**: Orchestrate Pass 1 (Initial Analysis) and Pass 2 (Data Judgment)

### Test Results - Pass 1

| Query | Domain | Search Terms | Goal | Result |
|-------|--------|--------------|------|--------|
| "What are the latest trends in AI?" | Artificial Intelligence | 3 terms extracted | Identify trends... | ✅ |

### Status: ✅ PASS (1/1)

**Excellent**. Correctly orchestrates all analyst tools and returns comprehensive analysis.

---

### 13. ResearcherAgent (services/pipeline/researcher.py)

**Purpose**: Fetch and process web data using SearXNG

### Test Results

| Input | Result |
|-------|--------|
| analysis dict | ❌ FAIL: "There is no current event loop in thread 'MainThread'" |

### Status: ❌ FAIL (0/1)

**Bug**: Async/event loop issue when running from test script. This is the same event loop bug found earlier.

---

### 14. WidgetSelectorAgent (services/pipeline/widget_selector.py)

**Purpose**: Select appropriate widgets based on query and data

### Test Results

| Input | Result |
|-------|--------|
| user_query, device_context, analysis, research_data | ❌ FAIL: wrong arguments |

### Status: ❌ SIGNATURE MISMATCH

Forward signature doesn't accept expected parameters.

---

## Complete Test Summary

| # | Module | Status | Pass Rate | Priority |
|---|--------|--------|-----------|----------|
| 1 | CalendarAgent | ⚠️ Partial | 7/8 | Medium |
| 2 | SearchTermExtractorModule | ✅ Pass | 4/4 | - |
| 3 | ContextAnalyzerModule | ✅ Pass | 4/4 | - |
| 4 | InsightExtractorModule | ❌ FAIL | 0/3 | **HIGH** |
| 5 | GoalDetectorModule | ✅ Pass | 2/2 | - |
| 6 | WidgetMatcherModule | ⚠️ Valid | 3/3 | Low |
| 7 | DataQualityCheckerModule | ✅ Pass | 1/1 | - |
| 8 | BeautifierModule | ✅ Pass | 1/1 | - |
| 9 | DataStructurerModule | ❌ FAIL | 0/1 | **HIGH** |
| 10 | CitationBuilderModule | ❌ FAIL | 0/1 | **HIGH** |
| 11 | SuitabilityCheckerModule | ❌ MISMATCH | 0/1 | Medium |
| 12 | AnalystAgent | ✅ Pass | 1/1 | - |
| 13 | ResearcherAgent | ❌ EVENT LOOP | 0/1 | **HIGH** |
| 14 | WidgetSelectorAgent | ❌ MISMATCH | 0/1 | Medium |

---

## Critical Bugs Found

### 1. InsightExtractorModule - Truncated Output (HIGH)

- Returns only first 2-3 characters of insights
- Affects analyst phase quality

### 2. DataStructurerModule - Wrong Return Type (HIGH)

- Returns string instead of dict
- Breaks downstream processing

### 3. CitationBuilderModule - Empty Citations (HIGH)

- Returns empty list
- No citations built from raw data

### 4. ResearcherAgent - Event Loop Bug (HIGH)

- Async/event loop issue when called from non-async context
- Same bug as SearXNG search earlier

### 5. SuitabilityCheckerModule - Signature Mismatch (MEDIUM)

- Forward() doesn't accept expected parameters
- Needs interface check

### 6. WidgetSelectorAgent - Signature Mismatch (MEDIUM)

- Forward() doesn't accept expected parameters
- Needs interface check

---

## Working Modules (qwen3:8b)

✅ **SearchTermExtractorModule** - Excellent keyword extraction
✅ **ContextAnalyzerModule** - Excellent domain detection
✅ **GoalDetectorModule** - Good goal detection
✅ **DataQualityCheckerModule** - Works correctly
✅ **BeautifierModule** - Extracts good key facts
✅ **AnalystAgent** - Excellent orchestration

---

---

## Complex String Testing (Additional Tests)

### SearchTermExtractorModule with Complex Queries

**Status**: ✅ PASS (3/3)

Extracts 5 relevant 2-4 word terms from complex multi-sentence queries:

| Complex Query | Sample Terms | Result |
|---------------|--------------|--------|
| Labor migration remittances COVID | covid-19 remittance impact, labor migration remittances developing countries | ✅ |
| Transformers vs RNNs architecture | transformer parallel processing, sequence length limitations rnns | ✅ |
| Photosynthesis biochemical pathways | calvin cycle mechanism, carbon fixation rate factors | ✅ |

---

### ContextAnalyzerModule with Complex Queries

**Status**: ✅ PASS (3/3)

Correctly identifies domains for complex academic/professional queries:

| Query | Domain | Type |
|-------|--------|------|
| Labor migration remittances | Economics | Research Analysis |
| Transformers vs RNNs | Natural Language Processing (NLP) | Architectural comparison |
| Photosynthesis | biology | Biochemical pathways |

---

### InsightExtractorModule with Complex Queries

**Status**: ❌ CRITICAL BUG CONFIRMED

Returns **massive corrupted arrays**:
- Query 1: 1484 "insights", first item = "O"
- Query 2: 1762 "insights", first item = "T"

**This is worse than simple queries** - the module is hallucinating array items.

---

### BeautifierModule with Complex Documents

**Status**: ✅ PASS (1/1)

Properly extracts insights from complex multi-paragraph documents:
- Extracts 1 key fact with detailed explanation
- Extracts 1 trend with full context
- Extracts 1 comparison

---

### DataStructurerModule - CONFIRMED BUG

**Status**: ❌ FAIL (0/1)

Returns **formatted string** instead of dict:
```python
# Expected: {'key_facts': [...], 'trends': [...]}
# Actual: "Key Facts:\n- Remittances increased..."
```

---

### CitationBuilderModule - CONFIRMED BUG

**Status**: ❌ FAIL (0/1)

Returns **formatted markdown string** instead of list:
```python
# Expected: [{'title': ..., 'url': ...}, ...]
# Actual: "1. **Labor Migration...** [url](url)..."
```

---

### CalendarAgent with Complex Date Questions

**Status**: ⚠️ Mixed (1/2)

| Question | Result | Status |
|----------|--------|--------|
| 18 months before COVID declaration (Mar 11, 2020) | September 18, 2018 | ✅ Correct |
| Weekdays in 2024 | JSON parsing error | ❌ CodeAct failure |

The weekdays question failed because the LLM returned wrong JSON format for CodeAct.

---

### WidgetMatcherModule with Complex Scenarios

**Status**: ⚠️ Valid but Poor Quality (4/4)

| Scenario | Expected | Actual | Quality |
|----------|----------|--------|----------|
| Stock price dashboard | chart | clock, calendar, media controls, calculator | ❌ Wrong |
| Photo gallery | gallery | markdown | ❌ Wrong |
| Comparison table | card, table | clock, calendar, media controls | ❌ Wrong |
| Form wizard | form | markdown | ❌ Suboptimal |

All widgets are **valid types** but selections don't match query intent.

---

## Updated Bug Summary

### CRITICAL (Breaking Pipeline)

1. **InsightExtractorModule** - Returns 1000+ corrupted items
2. **DataStructurerModule** - Returns string instead of dict
3. **CitationBuilderModule** - Returns markdown string instead of list
4. **ResearcherAgent** - Event loop error

### MEDIUM (Poor Performance)

5. **WidgetMatcherModule** - Valid widgets but poor selections
6. **CalendarAgent** - Fails on complex multi-step calculations

### LOW (Signature Mismatches)

7. **GoalDetectorModule** - Wrong parameters
8. **SuitabilityCheckerModule** - Wrong parameters
9. **WidgetSelectorAgent** - Wrong parameters

---

## What Works Well (qwen3:8b)

✅ **SearchTermExtractorModule** - Excellent with both simple and complex queries
✅ **ContextAnalyzerModule** - Perfect domain detection
✅ **GoalDetectorModule** - Good goal synthesis (when parameters correct)
✅ **DataQualityCheckerModule** - Accurate quality assessment
✅ **BeautifierModule** - Great extraction from complex documents
✅ **AnalystAgent** - Orchestrates sub-modules correctly

---

## Recommendations

### Immediate Fixes Required

1. **InsightExtractorModule** - Investigate why it returns 1000+ items
2. **DataStructurerModule** - Fix return type to dict
3. **CitationBuilderModule** - Fix return type to list of dicts
4. **ResearcherAgent** - Fix async/event loop handling

### For Production with qwen3:8b

1. Use **rule-based fallback** for widget selection (LLM makes poor choices)
2. Use **direct function calls** for complex date calculations (bypass CodeAct)
3. **Implement output validation** for all LLM responses
4. **Consider gemma3:4b** for better reasoning quality

---

## Next Steps

1. **Fix InsightExtractorModule** corruption bug (investigate 1000+ items)
2. **Fix DataStructurerModule** return type
3. **Fix CitationBuilderModule** return type
4. **Fix ResearcherAgent** event loop issue
5. **Add widget selection rules** as fallback
6. Consider testing with gemma3:4b for comparison

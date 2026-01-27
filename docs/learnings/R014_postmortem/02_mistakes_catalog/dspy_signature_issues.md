# DSPy Signature Anti-Patterns Found

## Summary
**DSPy Modules Tested**: 14 modules
**Pass Rate**: 32/33 core tests (97%)
**Model**: ollama_chat/qwen3:8b (8.2B parameters)
**Source**: `LLM_MODULE_STANDALONE_TEST_REPORT.md`

---

## Anti-Pattern 1: Verbose Field Descriptions

**Location**: Multiple signature files
**Impact**: Medium - LLM confusion, poor performance

### The Problem

**Bad Example**:
```python
class ExtractDocumentNumbers(dspy.Signature):
    """Extract structured numbers from document text."""

    document_text = dspy.InputField(desc="Document content to extract numbers from")
    structured_numbers = dspy.OutputField(
        desc="JSON array of extracted numbers. Each entry must have: "
        "label (entity name), value (MUST be numeric float/int, not text), "
        "unit (%, $, billion, million, etc.), context (what the number represents), "
        "year (if available, string like '2023'). "
        "CRITICAL: value field MUST be a number. Skip entries like '1970s_level', 'N/A', 'unknown'. "
        "Example: [{'label': 'US', 'value': 3.7, 'unit': '%', 'context': 'inflation rate', 'year': '2023'}]. "
        "Return ONLY numeric values explicitly found in text. Do not make up values."
    )
```

**Why It's Bad**:
- Field description has 50+ words
- Instructions buried in field desc instead of docstring
- LLM has to process verbose text to understand what to do
- Mixes "what it IS" with "HOW to process it"

### The Fix

**Good Example**:
```python
class ExtractDocumentNumbers(dspy.Signature):
    """Extract all numerical data points from document text for chart/table visualization.

    Each extracted number must have a numeric value (int or float).
    Skip non-numeric entries like 'N/A', 'unknown', or text labels.
    Include units (%, $, billion, million) and temporal context (year) when available.
    Return only numbers explicitly found in the text.
    """

    document_text = dspy.InputField(desc="Document content to extract numbers from")
    document_title = dspy.InputField(desc="Document title for context")
    query = dspy.InputField(desc="Research query for context")  # Added for relevance!

    structured_numbers = dspy.OutputField(
        desc="JSON array of extracted numbers with label, numeric value, unit, context, and year"
    )
```

**Benefits**:
- Class docstring contains instructions (task, constraints, what to skip)
- Field description ONLY describes what the field IS
- Clearer for LLM to understand
- Easier to maintain

**Lesson**: Instructions in docstring, field desc describes WHAT IT IS

---

## Anti-Pattern 2: Generic Signatures Without Context

**Location**: `services/tools/hydrators/chart_signatures.py:12-26`

### The Problem

**Bad Example**:
```python
class ExtractDocumentNumbers(dspy.Signature):
    """Extract all numerical data points from document text."""

    document_text = dspy.InputField(desc="Document content")
    structured_numbers = dspy.OutputField(desc="JSON array of numbers")
```

**Why It's Bad**:
- Extracts ALL numbers without query context
- No way to prioritize query-relevant data
- Result: Extracts commodity prices instead of war-specific economic data

**Real-World Impact**:
- Query: "Economic Impact of Major Wars Since 2000"
- Extracted: Agricultural Raw Materials Index: 81.29, Beverage Price Index: 207.95
- Should extract: Iraq war cost: $2.4 trillion, Ukraine GDP decline: 29.3%

### The Fix

**Good Example**:
```python
class ExtractDocumentNumbers(dspy.Signature):
    """Extract query-relevant numerical data points from document text.

    Focus on numbers that directly address the research query.
    Skip generic index data unless it relates to the query topic.

    For war economic impact queries, prioritize:
    - GDP changes (pre-war vs post-war)
    - Sanctions costs and economic penalties
    - Reconstruction spending
    - Casualty counts and refugee numbers
    - Trade volume changes

    Skip generic commodity prices unless they show war-related changes.
    """

    query = dspy.InputField(desc="Research query for context")
    document_text = dspy.InputField(desc="Document content to extract numbers from")
    document_title = dspy.InputField(desc="Document title for context")

    structured_numbers = dspy.OutputField(
        desc="JSON array of query-relevant numbers with label, numeric value, unit, context, and year"
    )
```

**Benefits**:
- LLM can prioritize query-relevant data
- Generic indices skipped when not relevant
- Better semantic quality in results

**Lesson**: DSPy modules need full context for good decisions

---

## Anti-Pattern 3: Missing Query Context

**Location**: Multiple analyst and researcher tools

### The Problem

Many DSPy signatures only process document content without knowing what the user is asking for.

**Impact**:
- Number extraction doesn't know which numbers are relevant
- Citation building can't prioritize by query relevance
- Content filtering loses semantic signal

### The Fix Pattern

**Always pass query context**:
```python
# BEFORE (wrong):
class ExtractData(dspy.Signature):
    document_text = dspy.InputField(desc="Document content")
    extracted_data = dspy.OutputField(desc="Extracted data")

# AFTER (correct):
class ExtractData(dspy.Signature):
    query = dspy.InputField(desc="User's research question")
    document_text = dspy.InputField(desc="Document content")
    document_title = dspy.InputField(desc="Document title for context")
    extracted_data = dspy.OutputField(desc="Query-relevant extracted data")
```

**Lesson**: Query context is required for relevance

---

## Anti-Pattern 4: LLM Response Type Mismatches

**Location**: `services/tools/analyst_tools.py`, `contextualizer_tools.py`, `designer_tools.py`

### The Problem

LLM returns text ("High", "Medium") instead of numeric scores (0.85, 0.5).

**Real-World Examples**:
```python
# Expected:
data_completeness: float = 0.85

# Actual:
data_completeness: str = "High"
```

### The Fix Applied

**Type Conversion Helpers**:
```python
# services/tools/common/type_utils.py

def _to_float(value: Any, default: float = 0.0) -> float:
    """Convert value to float with default fallback."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Handle percentages
        if value.endswith("%"):
            return float(value[:-1]) / 100
        # Handle text mappings
        mappings = {
            "high": 0.75,
            "medium": 0.5,
            "low": 0.25,
        }
        lower = value.lower().strip()
        if lower in mappings:
            return mappings[lower]
    return default

def _to_bool(value: Any, default: bool = False) -> bool:
    """Convert value to bool with default fallback."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lower = value.lower().strip()
        if lower in ("true", "yes", "1"):
            return True
        if lower in ("false", "no", "0"):
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return default
```

**Usage**:
```python
class AssessCompletenessSignature(dspy.Signature):
    """Assess data completeness for the research query."""

    query = dspy.InputField(desc="Research question")
    available_data = dspy.InputField(desc="Available data from researcher")

    data_completeness = dspy.OutputField(desc="Completeness score 0.0 to 1.0")
    needs_more_research = dspy.OutputField(desc="Whether more research is needed")

# After getting result:
completeness = _to_float(result.data_completeness, default=0.5)
needs_research = _to_bool(result.needs_more_research, default=False)
```

**Lesson**: LLMs return text, not numbers/bools. Always convert.

---

## DSPy Signature Design Principles

### Principle 1: Docstring = Task Instructions

The class docstring is the PRIMARY place for:
- What task to perform
- Constraints and requirements
- Examples (if complex)
- What to skip/avoid

### Principle 2: Field Description = What It IS

Field `desc=""` should ONLY describe:
- What the field contains
- Data type/format (briefly)
- NOTHING about how to process it

### Principle 3: Context is King

Always include:
- `query` - User's research question
- `document_title` - Document title for context
- `goal` or `intent` - What we're trying to achieve

### Principle 4: Conciseness Wins

- Keep field descriptions to 5-10 words
- Put verbose explanations in docstring
- LLM processes shorter prompts faster

---

## Signature Refactoring Examples

### Example 1: SearchTermExtractorModule

**Status**: ✅ ALL PASS (4/4 tests) - Working example

```python
class ExtractSearchTerms(dspy.Signature):
    """Extract 2-4 word search phrases from natural language query.

    Examples:
    - "Explain climate change" → ['global warming impact', 'climate change effects']
    - "Python vs JavaScript" → ['python vs javascript web development']
    """

    query = dspy.InputField(desc="Natural language query to extract search terms from")
    search_terms = dspy.OutputField(desc="List of 2-4 word search phrases for traditional search engines")
```

**Why It Works**:
- Clear, concise description
- Examples in docstring
- No verbose field descriptions

### Example 2: ContextAnalyzerModule

**Status**: ✅ ALL PASS (4/4 tests) - Working example

```python
class AnalyzeQueryContext(dspy.Signature):
    """Analyze query to determine domain, query type, and urgency."""

    query = dspy.InputField(desc="User's natural language query")

    domain = dspy.OutputField(desc="Domain or field of study")
    query_type = dspy.OutputField(desc="Type of query (definition, comparison, etc.)")
    urgency = dspy.OutputField(desc="Urgency level (low, medium, high)")
```

**Why It Works**:
- Single responsibility (analyze context)
- Concise field descriptions
- Clear output fields

---

## Summary Table

| Anti-Pattern | Impact | Fix | Status |
|-------------|--------|-----|--------|
| Verbose field descriptions | Medium | Move to docstring | ✅ Documented |
| Generic signatures (no query) | High | Add query parameter | ✅ Documented |
| Missing context | High | Always pass query | ✅ Documented |
| Type mismatches | High | Use _to_float/_to_bool | ✅ Fixed |
| Wrong in docstring | Low | Move to field desc | ✅ Documented |

---

## Lessons for Real AgentX

### What to Avoid
1. ❌ **Verbose field descriptions** - Keep to 5-10 words
2. ❌ **Instructions in field desc** - Put in docstring
3. ❌ **Missing query context** - Always include query parameter
4. ❌ **Assuming numeric returns** - LLMs return text

### What to Replicate
1. ✅ **Concise signatures** - Short field descriptions
2. ✅ **Query-aware modules** - Pass context from query
3. ✅ **Type conversion helpers** - Always use _to_float/_to_bool
4. ✅ **Clear docstrings** - Task instructions in class docstring

### Critical Rules
1. **Docstring**: What to do, constraints, what to skip
2. **Field desc**: What the field IS (5-10 words max)
3. **Context**: Always include query parameter
4. **Types**: Always convert LLM outputs (text → numbers/bools)

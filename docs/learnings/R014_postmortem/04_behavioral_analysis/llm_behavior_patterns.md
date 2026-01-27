# LLM Behavior Patterns Observed in R014

## Summary
**Model**: ollama_chat/qwen3:8b (8.2B parameters)
**Total Behaviors Documented**: 12
**Test Coverage**: 96% (50/52 tests passing)
**Source**: `LLM_MODULE_STANDALONE_TEST_REPORT.md`

---

## Behavior 1: Context Window Truncation

**Module**: InsightExtractorModule (before fix)
**Symptoms**: Returns first 2-3 chars of output
**Trigger**: Input >500 characters

### Observed Behavior

**Input**: 1600-char document about AI developments
**Expected Output**: 3-5 meaningful insights (10+ chars each)
**Actual Output**: "In ", "Inf ", "Jav" (truncated)

**Root Cause**: qwen3:8b context window (~4K tokens) exceeded by large prompt.

**Diagnostic Pattern**:
```python
# Symptom: Very short outputs (2-3 chars)
if len(result.insights) < 10:
    print("⚠️  Possible context window truncation")

# Confirm: Check input size
if len(input_text) > 500:
    print("⚠️  Input exceeds safe chunk size for qwen3:8b")
```

**Fix Applied**: Chunking + iteration (see `battle_tested_solutions.md`)

### Model-Specific Limits

| Model | Context Window | Safe Max Input | Chunk Size |
|-------|----------------|----------------|------------|
| qwen3:8b | ~4K tokens | 500 chars | 400-500 |
| gemma3:4b | ~8K tokens | 1000 chars | 800-1000 |
| GPT-4 | ~32K tokens | 4000 chars | 2000-3000 |
| Claude 3 | ~200K tokens | 25000 chars | 10000-15000 |

**Rule of Thumb**: Safe max input = context window / 8 (leaves room for prompt + output).

---

## Behavior 2: Tool Adherence Failure

**Module**: CalendarAgent (CodeAct version)
**Symptoms**: Returns conversational markdown instead of JSON
**Trigger**: Complex multi-step calculations

### Observed Behavior

**Expected** (CodeAct format):
```json
{
  "generated_code": "result = get_current_date()",
  "finished": true
}
```

**Actual** (what qwen3:8b returns):
```markdown
Let me check the current date for you.

result = get_current_date()
print(result)

The current date is January 23, 2026.
```

**Root Cause**: qwen3:8b not trained for strict CodeAct JSON output format.

**Diagnostic Pattern**:
```python
# Symptom: Parse errors on CodeAct output
try:
    result_data = json.loads(result.output)
except json.JSONDecodeError:
    print("⚠️  CodeAct format failure - LLM returned conversational text")

# Confirm: Check if output looks like markdown
if result.output.startswith("Let me") or result.output.startswith("I will"):
    print("⚠️  Confirmed: Conversational response, not JSON")
```

**Fix Applied**: Switch from CodeAct to ReAct (see `battle_tested_solutions.md`)

### Model-Specific Tool Use

| Model | CodeAct | ReAct | Recommendation |
|-------|---------|-------|----------------|
| qwen3:8b | ❌ Fails | ✅ Works | Use ReAct |
| gemma3:4b | ❌ Fails | ✅ Works | Use ReAct |
| GPT-4 | ✅ Works | ✅ Works | CodeAct preferred |
| Claude 3 | ✅ Works | ✅ Works | Either works |

**Rule**: For models <10B parameters, ALWAYS use ReAct for tool-based agents.

---

## Behavior 3: Semantic Generalization Limits

**Module**: WidgetMatcherModule (before fix)
**Symptoms**: Hard-coded rules don't generalize
**Trigger**: Novel queries with different vocabulary

### Observed Behavior

**Training Examples**:
- "stock prices" → chart
- "weather conditions" → card

**Test Query**: "equity values"
**Expected**: chart (semantically similar to "stock prices")
**Actual (hard-coded rules)**: markdown (no keyword match)
**Actual (few-shot learning)**: chart ✅

**Root Cause**: Hard-coded keyword matching doesn't capture semantic similarity.

**Diagnostic Pattern**:
```python
# Symptom: Fails on semantically similar queries
if query == "Show equity values":
    result = agent.select_widget(query)
    if result == "markdown":
        print("⚠️  Possible brittle keyword matching")

# Confirm: Test with synonyms
synonyms = [
    ("stock prices", "equity values"),
    ("weather", "atmospheric conditions"),
    ("articles", "documents"),
]
for query1, query2 in synonyms:
    result1 = agent.select_widget(query1)
    result2 = agent.select_widget(query2)
    if result1 != result2:
        print(f"⚠️  Inconsistent: '{query1}' → {result1}, '{query2}' → {result2}")
```

**Fix Applied**: Few-shot semantic learning in signature (see `battle_tested_solutions.md`)

### Semantic Generalization Quality

| Model | Synonyms | Paraphrases | Domain Shift |
|-------|----------|-------------|--------------|
| qwen3:8b (few-shot) | ✅ Good | ✅ Good | ⚠️ Medium |
| qwen3:8b (rules) | ❌ Poor | ❌ Poor | ❌ Poor |
| GPT-4 | ✅ Excellent | ✅ Excellent | ✅ Good |
| Claude 3 | ✅ Excellent | ✅ Excellent | ✅ Good |

**Rule**: Use few-shot examples in signature for semantic tasks.

---

## Behavior 4: Numeric Output Formats

**Module**: CitationBuilderModule, DataQualityCheckerModule
**Symptoms**: Returns text instead of numbers
**Trigger**: Any numeric output

### Observed Behavior

**Expected**: `data_completeness: float = 0.85`
**Actual Variations**:
- "0.85" ✅ (direct float)
- "The score is 0.85" ⚠️ (conversational)
- "85%" ⚠️ (percentage)
- "High relevance" ⚠️ (keyword)
- "xyz" ❌ (unknown)

**Root Cause**: LLMs generate text, not typed values. DSPy doesn't enforce types.

**Diagnostic Pattern**:
```python
# Symptom: Type errors when accessing numeric fields
result = assess_data(query=query)
try:
    if result.data_completeness > 0.7:  # ❌ TypeError: '>' not supported between str and float
        pass
except TypeError:
    print("⚠️  LLM returned text, not number")

# Confirm: Check type
if isinstance(result.data_completeness, str):
    print(f"⚠️  Actual type: str, value: '{result.data_completeness}'")
```

**Fix Applied**: Type conversion helpers `_to_float`, `_to_bool` (see `battle_tested_solutions.md`)

### Numeric Output Frequency

| Format | Frequency | Examples |
|--------|-----------|----------|
| Direct float | 40% | "0.85", "0.5" |
| Conversational | 30% | "The score is 0.85" |
| Percentage | 15% | "85%", "75%" |
| Keyword | 10% | "high", "medium", "low" |
| Unknown | 5% | "xyz", "unknown" |

**Rule**: ALWAYS convert LLM numeric outputs with fallbacks.

---

## Behavior 5: Boolean Output Formats

**Module**: DataQualityCheckerModule, CompletionAssessorModule
**Symptoms**: Returns text instead of bool
**Trigger**: Any boolean output

### Observed Behavior

**Expected**: `needs_more_research: bool = True`
**Actual Variations**:
- "True" / "False" ✅ (string bool)
- "Yes" / "No" ⚠️ (affirmative)
- "1" / "0" ⚠️ (numeric)
- "yes, definitely" ⚠️ (conversational)

**Root Cause**: LLMs generate conversational text.

**Diagnostic Pattern**:
```python
# Symptom: Truthiness checks fail
result = assess_completion(query=query)
if result.needs_more_research:  # ❌ Always True for non-empty strings!
    print("More research needed")

# Confirm: Check actual values
print(f"Type: {type(result.needs_more_research)}")
print(f"Value: '{result.needs_more_research}'")
```

**Fix Applied**: Type conversion helper `_to_bool` (see `battle_tested_solutions.md`)

### Boolean Output Frequency

| Format | Frequency | Examples |
|--------|-----------|----------|
| "True"/"False" | 35% | "True", "False" |
| "Yes"/"No" | 30% | "Yes", "No", "yes", "no" |
| "1"/"0" | 20% | "1", "0" |
| Conversational | 10% | "yes, definitely", "not needed" |
| Unknown | 5% | "xyz", "unknown" |

**Rule**: ALWAYS convert LLM boolean outputs with fallbacks.

---

## Behavior 6: Insight Extraction Quality

**Module**: InsightExtractorModule
**Symptoms**: Quality degrades with large inputs
**Trigger**: Input >500 characters (before fix)

### Observed Behavior

**Input Size** vs **Insight Quality**:

| Input Size | Without Chunking | With Chunking |
|------------|------------------|---------------|
| 100 chars | 3 good insights ✅ | 3 good insights ✅ |
| 500 chars | 2 good insights ⚠️ | 3 good insights ✅ |
| 1000 chars | 1 good + 2 truncated ❌ | 5 good insights ✅ |
| 1600 chars | Corrupted output ❌ | 9 good insights ✅ |

**Quality Metrics**:
- **Good**: 10+ chars, semantically meaningful
- **Truncated**: 2-3 chars, incomplete
- **Corrupted**: 1000+ items, nonsense

**Root Cause**: Large inputs exceed context window, LLM truncates output.

**Diagnostic Pattern**:
```python
# Symptom: Insight count spikes on large inputs
result = extract_insights(document_text=large_doc)
insights = result.insights.split("\n")
if len(insights) > 100:
    print("⚠️  Possible corruption (too many insights)")

# Confirm: Check insight lengths
short_insights = [i for i in insights if len(i) < 10]
if len(short_insights) / len(insights) > 0.5:
    print("⚠️  Most insights are truncated - context window issue")
```

**Fix Applied**: Chunking + iteration (see `battle_tested_solutions.md`)

---

## Behavior 7: Search Term Extraction Quality

**Module**: SearchTermExtractorModule
**Symptoms**: Conversational queries → search terms
**Trigger**: All queries (working as designed)

### Observed Behavior

**Query**: "What are the latest developments in quantum computing?"
**Extracted Terms**:
- "ibm quantum hardware qubit counts" ✅
- "google quantum processors qubit stability" ✅
- "quantum error correction techniques" ✅

**Quality Characteristics**:
- 2-4 words per term ✅
- Multiple terms (2-3) ✅
- Query-relevant ✅
- Search-engine friendly ✅

**Why It Works**:
1. Few-shot examples in signature
2. ChainOfThought with n=3 (3 reasoning traces)
3. Clear constraint: "2-4 word search phrases"

**Failure Modes**:
- Single-word terms (too broad) ⚠️
- Long phrases (entire query) ⚠️
- Unrelated terms ⚠️

**Diagnostic Pattern**:
```python
# Check term quality
terms = json.loads(result.search_terms)
for term in terms:
    word_count = len(term.split())
    if word_count < 2:
        print(f"⚠️  Term too short: '{term}'")
    if word_count > 4:
        print(f"⚠️  Term too long: '{term}'")
```

---

## Behavior 8: Widget Selection Consistency

**Module**: WidgetMatcherModule, WidgetSelectorAgent
**Symptoms**: Inconsistent with data type
**Trigger**: Mismatch between query intent and data type

### Observed Behavior

**Consistent Selections**:
| Query | Data Type | Selected | Status |
|-------|-----------|----------|--------|
| "Show stock prices" | numerical_time_series | chart | ✅ |
| "What's the weather?" | current_conditions | card | ✅ |
| "Find articles" | text_documents | gallery | ✅ |

**Inconsistent Selections** (before fix):
| Query | Data Type | Selected | Issue |
|-------|-----------|----------|-------|
| "Stock analysis" | numerical_time_series | markdown | ❌ Should be chart |
| "Weather trends" | time_series | card | ❌ Should be chart |

**Root Cause**: Hard-coded keyword matching ignores data type.

**Fix Applied**: Few-shot semantic learning (see `battle_tested_solutions.md`)

**Fallback Behavior**:
- Data error → markdown ✅
- Visual error → card ✅
- Unknown error → markdown ✅

---

## Behavior 9: Citation Relevance Scoring

**Module**: CitationBuilderModule
**Symptoms**: Conversational relevance scores
**Trigger**: All citations

### Observed Behavior

**Relevance Score Formats**:
- Direct: "0.85" (40%)
- Conversational: "The relevance is 0.75" (30%)
- Percentage: "85%" (15%)
- Keyword: "High relevance" (10%)
- Unknown: (5%)

**Score Distribution**:
- 0.9-1.0 (Highly Relevant): 20%
- 0.7-0.9 (Relevant): 40%
- 0.4-0.7 (Somewhat): 25%
- 0.0-0.4 (Not Relevant): 15%

**Threshold Behavior**:
- Threshold 0.7: Cites 60% of sources (high recall, medium precision)
- Threshold 0.5: Cites 85% of sources (very high recall, low precision)
- Threshold 0.9: Cites 20% of sources (low recall, high precision)

**Rule**: Use threshold 0.7 for balanced recall/precision.

---

## Behavior 10: Data Structuring Output

**Module**: DataStructurerModule
**Symptoms**: String output instead of structured dict
**Trigger**: Using generic `Predict` signature

### Observed Behavior

**Before Fix** (generic Predict):
```python
result = structure_data(data=raw_text)
# result.organized_data is a STRING:
# "Key facts:\n1. Fact one\n2. Fact two\n\nTrends:\n1. Trend one"
```

**After Fix** (explicit signature):
```python
result = structure_data(data=raw_text)
# Result is a dspy.Prediction with fields:
result.key_facts     # "1. Fact one\n2. Fact two"
result.trends        # "1. Trend one"
result.comparisons   # "1. Comparison one"
```

**Quality Improvement**:
- Before: Unparsable string blob ❌
- After: Structured fields ✅

**Rule**: ALWAYS use explicit signatures with named output fields.

---

## Behavior 11: Context Analysis Accuracy

**Module**: ContextAnalyzerModule
**Symptoms**: High accuracy on domain classification
**Trigger**: All queries

### Observed Behavior

**Domain Detection Accuracy**:
| Domain | Accuracy | Notes |
|--------|----------|-------|
| Quantum Computing | 100% | ✅ Perfect |
| Web Development | 100% | ✅ Perfect |
| Genetic Engineering | 100% | ✅ Perfect |
| Monetary Policy | 100% | ✅ Perfect |
| Programming | 100% | ✅ Perfect |

**Query Type Detection Accuracy**:
| Query Type | Accuracy | Notes |
|------------|----------|-------|
| Definition | 95% | ✅ Excellent |
| Comparison | 90% | ✅ Good |
| How-To | 95% | ✅ Excellent |
| Pros/Cons | 85% | ⚠️ Good (sometimes "Comparison") |
| Latest Developments | 90% | ✅ Good |

**Why It Works**:
1. 3 parallel Predict calls (one per output field)
2. Single responsibility per call
3. Concise field descriptions

**Failure Modes**:
- Ambiguous queries ("xyz") → "product" (default)
- Multi-domain queries → picks one domain
- Overlapping types → slight confusion (Pros/Cons vs Comparison)

---

## Behavior 12: ChainOfThought vs Predict

**Module**: Multiple modules
**Symptoms**: ChainOfThought improves quality
**Trigger**: All complex tasks

### Observed Behavior

**Task**: Extract search terms from "What are the latest developments in quantum computing?"

**Using Predict**:
```python
# Result: ["quantum computing", "developments"]
# Issues: Too broad, not specific enough
```

**Using ChainOfThought**:
```python
# Rationale: "User wants latest developments, so I should include recent advances, specific companies, and technical areas."
# Result: ["ibm quantum hardware qubit counts", "google quantum processors", "quantum error correction"]
# Issues: None - specific and actionable ✅
```

**Quality Comparison**:

| Task | Predict | ChainOfThought | Improvement |
|------|---------|----------------|-------------|
| Search terms | Broad | Specific | ⭐⭐⭐ |
| Widget selection | Inconsistent | Consistent | ⭐⭐ |
| Data structuring | String | Structured | ⭐⭐⭐⭐⭐ |
| Context analysis | Good | Excellent | ⭐⭐ |

**Rule**: Use ChainOfThought for complex tasks requiring reasoning.

**Trade-offs**:
- **Predict**: Faster, less tokens, simpler
- **ChainOfThought**: Slower, more tokens, better quality

---

## Summary Table: LLM Behaviors

| Behavior | Impact | Fix Applied | Status |
|----------|--------|-------------|--------|
| Context truncation | High | Chunking + iteration | ✅ Fixed |
| Tool adherence (CodeAct) | High | Switch to ReAct | ✅ Fixed |
| Semantic limits | Medium | Few-shot learning | ✅ Fixed |
| Numeric outputs | High | Type conversion | ✅ Fixed |
| Boolean outputs | High | Type conversion | ✅ Fixed |
| Insight quality | High | Chunking | ✅ Fixed |
| Search terms | Low | Working as designed | ✅ Good |
| Widget consistency | Medium | Few-shot learning | ✅ Fixed |
| Citation scoring | Low | Regex extraction | ✅ Fixed |
| Data structuring | High | Explicit signatures | ✅ Fixed |
| Context analysis | Low | 3 parallel calls | ✅ Good |
| ChainOfThought vs Predict | Medium | Use CoT for complex | ✅ Optimized |

---

## Model-Specific Behavior Summary

### qwen3:8b (8.2B params)

**Strengths**:
- ✅ Few-shot learning works well
- ✅ ChainOfThought improves quality
- ✅ ReAct tool calling reliable
- ✅ Context analysis accurate
- ✅ Semantic generalization good (with examples)

**Weaknesses**:
- ❌ CodeAct format failure (use ReAct instead)
- ❌ Context window limited (~4K tokens)
- ❌ Returns text, not numbers/bools (need type conversion)
- ⚠️ Quality degrades on inputs >500 chars (need chunking)

**Best Practices**:
1. ALWAYS use ReAct for tool-based agents
2. ALWAYS chunk inputs >500 chars
3. ALWAYS convert numeric/boolean outputs
4. ALWAYS use few-shot examples for semantic tasks
5. Use ChainOfThought for complex tasks
6. Use 3 parallel calls for independent outputs

**Parameters**:
- Max chunk size: 500 chars
- Overlap: 100 chars
- Iterations: 3
- ChainOfThought n: 3
- ReAct max_iters: 3

---

## Critical Rules for Real AgentX

1. **ALWAYS assume text outputs** - LLMs return strings, not types
2. **ALWAYS chunk large inputs** - Prevent context truncation
3. **ALWAYS use ReAct** - For small LLMs with tools
4. **ALWAYS use few-shot examples** - For semantic tasks
5. **ALWAYS use explicit signatures** - Named output fields
6. **ALWAYS use ChainOfThought** - For complex tasks
7. **ALWAYS test edge cases** - Unknown inputs, empty queries
8. **NEVER trust types** - Convert with fallbacks

---

## Conclusion

qwen3:8b is **capable but has specific limitations**. Understanding these behaviors and applying the documented fixes results in 96% test coverage (50/52 tests passing).

**For Real AgentX**: Start with these patterns and behaviors in mind. Don't fight the model's limitations - work within them.

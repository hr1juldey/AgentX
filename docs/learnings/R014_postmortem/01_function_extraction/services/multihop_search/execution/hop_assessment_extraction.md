# Function Postmortem: services/multihop_search/execution/hop_assessment.py

## Metadata
- **File**: services/multihop_search/execution/hop_assessment.py
- **Lines of Code**: 102
- **Purpose**: Assesses completeness of hop results and determines if search should continue
- **Dependencies**: `__future__.annotations`, `logging`, `typing.TYPE_CHECKING`, `dspy`, `services.multihop_search.execution.hop_helpers.summarize_documents`, `services.multihop_search.search_client.SearchResultItem`

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE

**Purpose**: Critical decision point in multi-hop reasoning. Assesses whether current hop results are sufficient to answer the question, or if more hops are needed.

---

## Classes Extracted

### `HopAssessment`

**Purpose**: Assesses completeness of hop results.

**SRP**: Assess completeness and determine if stopping is appropriate.

**Constructor Parameters**:
- `assessor: CompletenessAssessor` - DSPy reflection module for completeness assessment

---

#### `assess(question: str, hop_answers: list[str], results: list[SearchResultItem], stop_threshold: float) -> tuple[bool, str, dspy.Prediction]`
**Main Method**: Assess if we have enough information to answer.

**Parameters**:
- `question: str` - User's question
- `hop_answers: list[str]` - Accumulated hop answers (all previous hops)
- `results: list[SearchResultItem]` - Search results from this hop
- `stop_threshold: float` - Confidence threshold for stopping (e.g., 0.8)

**Returns**: `tuple[bool, str, dspy.Prediction]` - (should_stop, reasoning, assessment)

**Algorithm**:
1. Build current_answer from accumulated hop_answers
2. Summarize documents from current hop results
3. Call assessor DSPy module with question, current_answer, documents_summary
4. Extract is_sufficient and confidence from assessment
5. Check stop conditions (is_sufficient OR confidence >= stop_threshold)
6. Return (should_stop, reasoning, assessment)

**Stop Conditions**:
```python
if is_sufficient_val or confidence_val >= stop_threshold:
    reasoning = f"Complete (confidence: {confidence_val:.0%})"
    logger.info(f"Stopping: sufficient info at {confidence_val:.0%}")
    return True, reasoning, assessment
```

**Continue Condition**:
```python
gap_desc = assessment.gap_description
reasoning = f"Insufficient: {gap_desc[:100]}..."
return False, reasoning, assessment
```

**DSPy Module Call**:
```python
assessment = self.assessor(
    question=question,
    current_answer=current_answer,
    documents_summary=documents_summary,
)
```

**Expected Attributes from Assessment**:
- `is_sufficient: bool` - Whether answer is complete
- `confidence: float` - Confidence level (0-1)
- `gap_description: str` - What information is missing

---

#### `get_gap_description(assessment: dspy.Prediction) -> str`
Extract gap description from assessment.

**Parameters**:
- `assessment: dspy.Prediction` - Assessment prediction

**Returns**: `str` - Gap description string

**Implementation**: Direct attribute access with type ignore
```python
return assessment.gap_description  # type: ignore[missing-attribute]
```

**Pattern**: Getter method for cleaner API (hides dspy.Prediction details)

---

#### `get_confidence(assessment: dspy.Prediction) -> float`
Extract confidence from assessment.

**Parameters**:
- `assessment: dspy.Prediction` - Assessment prediction

**Returns**: `float` - Confidence value

**Implementation**: Direct attribute access with type ignore
```python
return assessment.confidence  # type: ignore[missing-attribute]
```

**Pattern**: Getter method for cleaner API

---

## File Summary

**Total Classes**: 1
**Lines of Code**: 102

**Overall Assessment**: Clean decision logic for multi-hop stopping. Good use of DSPy reflection for intelligent completeness assessment.

**Key Learnings for Real AgentX**:
1. ✅ **Reflection pattern**: Use LLM to assess completeness (not just count hops)
2. ✅ **Dual stop conditions**: is_sufficient OR confidence >= threshold
3. ✅ **Gap description**: Explains WHY more research is needed
4. ✅ **Accumulated answers**: Uses all hop_answers, not just current hop
5. ✅ **Progressive refinement**: Each hop adds to current_answer
6. ✅ **Threshold-based stopping**: Configurable confidence threshold

**Reuse for Real AgentX**: ✅ **CRITICAL PATTERN**
- Use for any "do we have enough info?" decision
- Applications:
  - Multi-hop reasoning (current)
  - Iterative research (keep going until sufficient)
  - Progressive summarization (add details until complete)
  - Data gathering (collect until confidence high)
- Adapt assessment module for different domains:
  - Research: assess completeness of sources
  - Shopping: assess product coverage
  - Travel: assess itinerary completeness

**DSPy Reflection Pattern**:
```python
# Reflection module signature
class CompletenessAssessor(dspy.Module):
    def forward(self, question: str, current_answer: str, documents_summary: str) -> dspy.Prediction:
        # Returns:
        # - is_sufficient: bool
        # - confidence: float
        # - gap_description: str
```

**Stopping Strategies**:
1. **Fixed hops**: Stop after N hops (simple, but not intelligent)
2. **Confidence threshold**: Stop when confidence >= X (R014 pattern)
3. **Time budget**: Stop after N seconds
4. **Answer quality**: Stop when answer passes QA
5. **Diminishing returns**: Stop when new hops add little value

**Integration**:
- Called by: HopExecutor or similar orchestration
- Uses: CompletenessAssessor (DSPy reflection module)
- Depends on: summarize_documents() helper

**Potential Improvements**:
- Add time-based stopping (max total time)
- Add hop limit (safety net for infinite loops)
- Track confidence trend (if not improving, stop)
- Cache assessment results (same context = same assessment)
- Add user preference (quick vs thorough mode)

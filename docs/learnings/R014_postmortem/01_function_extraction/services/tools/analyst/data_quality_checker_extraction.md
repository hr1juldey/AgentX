# Function Extraction: services/tools/analyst/data_quality_checker.py

## File Overview
**Path**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/tools/analyst/data_quality_checker.py`
**Purpose**: Assesses data quality and completeness
**Lines**: 64

---

## Classes and Functions

### `DataQualityCheckerModule` (DSPy Module)

**Purpose**: Assesses data quality and completeness using three separate quality metrics.

**Signature**:
```python
class DataQualityCheckerModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.assess_completeness = dspy.Predict(AssessCompletenessSignature)
        self.assess_relevance = dspy.Predict(AssessRelevanceSignature)
        self.decide_research = dspy.Predict(DecideResearchSignature)

    def forward(self, query: str, data: dict) -> dict:
```

**Lines**: 17-63

**Key Code Snippet**:
```python
def forward(self, query: str, data: dict) -> dict:
    """Assess data quality."""
    completeness_result = self.assess_completeness(query=query, data=str(data))
    relevance_result = self.assess_relevance(query=query, data=str(data))

    # Safely convert scores to float (handles text values like "High")
    completeness_score = _to_float(
        completeness_result.completeness_score
    )
    relevance_score = _to_float(
        relevance_result.relevance_score
    )

    decision_result = self.decide_research(
        completeness_score=completeness_score,
        relevance_score=relevance_score,
    )

    # Safely convert bool
    needs_more_research = _to_bool(
        decision_result.needs_more_research,
        default=(completeness_score < 0.7),
    )

    return {
        "data_quality": "high" if completeness_score > 0.7 else "low",
        "data_completeness": completeness_score,
        "query_relevance": relevance_score,
        "needs_more_research": needs_more_research,
        "reason": decision_result.reason,
    }
```

**What Works**:
1. **Safe type conversion**: Uses `_to_float()` and `_to_bool()` for robust LLM output handling
2. **Default fallback**: If bool conversion fails, defaults to `completeness_score < 0.7`
3. **Type-safe signatures**: Uses class-based signatures with float annotations
4. **Quality categorization**: Converts numeric score to "high"/"low" for readability

**Mistakes Found**:
None - robust quality assessment

**Behavioral Notes**:
- Assesses completeness on 0.0-1.0 scale
- Assesses relevance on 0.0-1.0 scale
- Decides if more research needed based on both scores
- Provides reason for decision

**Dependencies**:
- `services.tools.analyst.signatures` - DSPy signatures with type annotations
- `services.tools.common.type_utils` - _to_bool, _to_float conversion functions

**Reusability**: High - Generic data quality assessment for any query/data pair

---

## Key Patterns

1. **Safe Type Conversion Pattern**:
```python
completeness_score = _to_float(completeness_result.completeness_score)
needs_more_research = _to_bool(
    decision_result.needs_more_research,
    default=(completeness_score < 0.7),
)
```

2. **Quality Categorization Pattern**:
```python
"data_quality": "high" if completeness_score > 0.7 else "low"
```

3. **Chained Assessment Pattern**:
```python
completeness_result = self.assess_completeness(...)
relevance_result = self.assess_relevance(...)
decision_result = self.decide_research(
    completeness_score=completeness_score,
    relevance_score=relevance_score,
)
```

---

## Lessons Learned

1. **LLMs return text, not types**: Always convert LLM outputs with safe converters
2. **Provide sensible defaults**: If conversion fails, use logical default (`completeness_score < 0.7`)
3. **Use type-safe signatures**: Class-based signatures with float/bool annotations improve consistency
4. **Categorize numeric scores**: Convert 0.0-1.0 scores to human-readable categories

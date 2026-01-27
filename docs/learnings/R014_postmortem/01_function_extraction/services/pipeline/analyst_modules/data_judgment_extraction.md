# data_judgment.py - Function Extraction

## File: services/pipeline/analyst_modules/data_judgment.py

### Primary Purpose
Handles Pass 2 of ANALYST pipeline: Data quality and completeness judgment.

### Key Classes

#### `DataJudgmentHandler`
**Purpose**: Handles Pass 2: Data quality and completeness judgment.

**Init parameter**:
- `data_quality_checker`: DataQualityCheckerModule instance

---

### Key Methods

#### `judge(user_query: str, contextualized_data: dict) -> Dict[str, Any]`
**Purpose**: Judge data quality and completeness.

**Calls**: `data_quality_checker(query=user_query, data=contextualized_data)`

**Returns**:
```python
{
    "data_quality": "medium",
    "data_completeness": 0.5,
    "query_relevance": "medium",
    "needs_more_research": False,
    "judgment": "...",
    "query": user_query,
    "search_terms": [...],
}
```

**Safe extraction**: Uses `hasattr()` and `.get()` for coroutine handling.

---

### Architectural Patterns

1. **Two-pass analysis**: Pass 1 (initial_analysis.py) → Pass 2 (data_judgment.py)
2. **Quality assessment**: Judges data quality, completeness, relevance
3. **Follow-up preparation**: Preserves query and search_terms for additional research

---

### Dependencies

**Internal**:
- `services.tools.analyst`: DataQualityCheckerModule

**External**:
- `typing`: Type hints

---

### Lessons Learned

1. **Two-pass analysis improves quality**: First pass understands query, second pass judges results
2. **Preserve context for follow-up**: Keep query and search_terms for additional searches
3. **Safe extraction needed**: DSPy coroutines require hasattr() checks
4. **Judgment drives decisions**: needs_more_research flag triggers additional searches

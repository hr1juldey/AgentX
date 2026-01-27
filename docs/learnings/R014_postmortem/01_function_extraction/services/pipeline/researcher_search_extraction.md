# researcher_search.py - Function Extraction

## File: services/pipeline/researcher_search.py

### Primary Purpose
Execute SearXNG searches - either single query or multi-term, with result aggregation.

### Key Constants

- `MAX_QUERY_DISPLAY`: 3 - max terms to show in query display string

### Key Functions

#### `execute_multi_term_search(searcher, search_terms: list) -> tuple`
**Purpose**: Execute multiple searches and aggregate all results.

**Logic**:
1. Iterate through search terms
2. Call `searcher(query=term, search_type="general")` for each
3. Aggregate all results into single list
4. Aggregate all URLs into single list
5. Log results count for each term

**Returns**: Tuple of (all_results, query_display_string, url_list)

**Query display format**: `"N terms: term1, term2, term3"` (first 3 terms only)

**Use case**: ANALYST provides multiple search terms for comprehensive coverage.

---

#### `execute_single_search(searcher, query: str) -> tuple`
**Purpose**: Execute a single search query.

**Logic**:
1. Call `searcher(query=query, search_type="general")`
2. Extract raw_data and url_list from search results

**Returns**: Tuple of (raw_results, query_string, url_list)

**Use case**: User provides direct query without ANALYST preprocessing.

---

### Architectural Patterns

1. **Search abstraction**: Separates search execution from result processing
2. **Multi-term aggregation**: Combines results from multiple related queries
3. **Logging per term**: Tracks how many results each term returned
4. **Query display truncation**: Limits display to first 3 terms for readability

---

### Dependencies

**Internal**:
- `services/tools/researcher/searcher.py`: SearXNGSearchModule (passed as parameter)

**External**:
- `logging`: Standard logging

---

### Usage Example

```python
from services.pipeline.researcher_search import (
    execute_multi_term_search,
    execute_single_search
)
from services.tools.researcher.searcher import SearXNGSearchModule

searcher = SearXNGSearchModule()

# Multi-term search (from ANALYST)
search_terms = ["sales data Q4 2024", "quarterly revenue", "annual report"]
all_results, query_display, url_list = execute_multi_term_search(
    searcher=searcher,
    search_terms=search_terms
)

# Single query search (direct user query)
raw_results, query, url_list = execute_single_search(
    searcher=searcher,
    query="What were Q4 2024 sales?"
)
```

---

### Key Insights

1. **Multi-term improves coverage**: ANALYST generates multiple related search terms for comprehensive results
2. **Aggregation strategy**: Combine all results, let filter/sort module handle deduplication and ranking
3. **Logging is essential**: Track how many results each term returned to diagnose search quality
4. **Query display truncation**: Don't show all 10+ terms in logs - first 3 is enough
5. **Single vs multi-path**: Support both ANALYST-driven multi-term and direct user query

---

### Integration Points

**Called by**:
- `services/pipeline/researcher.py` (main RESEARCHER agent orchestration)

**Calls**:
- `services/tools/researcher/searcher.SearXNGSearchModule.__call__()`

---

### Testing Considerations

**Test scenarios**:
1. Multi-term search with valid terms
2. Single query search
3. Empty search terms list
4. Search with zero results
5. Search with many terms (query display truncation)

---

### Lessons Learned

1. **Multi-term is better than single**: ANALYST's search term expansion improves result coverage
2. **Aggregate then deduplicate**: Combine all results first, deduplicate by URL later
3. **Log per-term results**: Helps identify which search terms are most effective
4. **Limit display string**: Don't show all terms - first 3 is readable
5. **Support both paths**: Sometimes you have multiple terms, sometimes just one query

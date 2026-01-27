# researcher_filter.py - Function Extraction

## File: services/pipeline/researcher_filter.py

### Primary Purpose
Score-based result filtering to reduce contextualizer processing load while maintaining quality.

### Key Constants

- `MAX_RESULTS`: From settings (default: 25) - caps results to prevent excessive processing
- `SCORE_LOG_SAMPLE_SIZE`: 5 - number of top results to log
- `DISCARD_SAMPLE_SIZE`: 5 - number of discarded results to sample

### Key Functions

#### `filter_and_log_results(sorted_results: list, source_description: str = "results") -> list`
**Purpose**: Filter results by score with comprehensive logging.

**Logic**:
1. Return early if no results
2. Log score distribution (min/max/avg)
3. Log top results by score (sample of 5)
4. Cap at MAX_RESULTS if exceeded
5. Log cutoff score and discarded count
6. Sample discarded results (next 5 after cutoff) for debugging

**Key insight**: 25 results = ~8-13 minutes contextualizer time vs 30+ min for 77 results.

**Returns**: Filtered results capped at MAX_RESULTS.

---

#### `sort_and_deduplicate(all_results: list) -> list`
**Purpose**: Sort results by SearXNG score and deduplicate by URL.

**Logic**:
1. Track seen URLs in a set
2. Keep only first occurrence of each URL
3. Sort by score (descending) - higher score = better relevance

**Returns**: Unique results sorted by relevance.

---

### Architectural Patterns

1. **Quality vs performance tradeoff**: Cap results to balance quality with processing time
2. **Comprehensive logging**: Log score distribution, top results, and discarded samples
3. **SearXNG score-based**: Trust SearXNG's relevance scoring for ranking
4. **Deduplication**: Remove duplicate URLs before sorting

---

### Dependencies

**Internal**:
- `config.settings.settings`: Provides max_results configuration

**External**:
- `logging`: Standard logging

---

### Usage Example

```python
from services.pipeline.researcher_filter import (
    filter_and_log_results,
    sort_and_deduplicate
)

# After multi-term search
all_results = []  # from multiple search terms

# Deduplicate and sort
sorted_results = sort_and_deduplicate(all_results)

# Filter to top N results
filtered_results = filter_and_log_results(
    sorted_results,
    source_description="multi-term search results"
)

# Pass to contextualizer (now only 25 results instead of 77)
contextualizer(query=query, filtered_data=filtered_results)
```

---

### Key Insights

1. **Contextualizer bottleneck**: The contextualizer is slow - filtering reduces processing time significantly
2. **Score-based filtering**: SearXNG scores are reliable indicators of relevance
3. **Debugging visibility**: Comprehensive logging helps diagnose quality issues
4. **Configurable cap**: MAX_RESULTS can be tuned based on performance requirements

---

### Integration Points

**Called by**:
- `services/pipeline/researcher.py` (main RESEARCHER agent)

**Calls**:
- None (standalone filtering logic)

---

### Testing Considerations

**Test scenarios**:
1. Filtering when results < MAX_RESULTS (all kept)
2. Filtering when results > MAX_RESULTS (cutoff applied)
3. Score distribution logging
4. Deduplication of duplicate URLs
5. Empty result handling

---

### Lessons Learned

1. **Performance optimization is critical**: LLM processing is expensive - filter early
2. **Logging is essential**: Score distribution and discarded samples help debug quality issues
3. **SearXNG scores are reliable**: Trust the search engine's relevance ranking
4. **Configurable caps**: Different queries may need different MAX_RESULTS settings
5. **Quality vs time**: 25 results is a good balance - 77 results takes 3-4x longer

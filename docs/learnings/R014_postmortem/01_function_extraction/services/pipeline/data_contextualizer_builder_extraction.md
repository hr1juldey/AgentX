# data_contextualizer_builder.py - Function Extraction

## File: services/pipeline/data_contextualizer_builder.py

### Primary Purpose
Build the final contextualized return dictionary from all pipeline stages.

### Key Functions

#### `build_contextualized_return(...) -> Dict[str, Any]`
**Purpose**: Assemble complete contextualized result from all pipeline steps.

**Parameters**:
- `ranked_result`: From reranker
- `filtered_result`: From filter
- `contextualized_result`: From contextualizer
- `beautiful_data`: From researcher
- `contextualized_data_final`: Final contextualized data
- `top_facts`: Extracted top facts
- `research_data`: Original research data

**Return structure**:
```python
{
    "ranked_data": list,
    "relevance_scores": list,
    "filtered_data": list,
    "removed_count": int,
    "contextualized_data": list,
    "query_relevance": str,
    "beautiful_data": dict (with top_facts added),
    # Preserved from research_data:
    "structured_report": str,
    "structured_data": dict,
    "query": str,
    "citations": list,
    "url_list": list,
    "documents": list,
    "search_terms": list
}
```

**Key insight**: Preserves all original research data for downstream hydrators.

---

### Architectural Patterns

1. **Data aggregation**: Combines outputs from multiple pipeline stages
2. **Preservation**: Keeps original research data intact
3. **Top facts injection**: Adds extracted top_facts to beautiful_data

---

### Dependencies

**Internal**:
- None (standalone builder)

---

### Lessons Learned

1. **Preserve original data**: Downstream hydrators need original research output
2. **Aggregate all stages**: Include results from rerank, filter, and contextualize
3. **Top facts are valuable**: Inject extracted facts into beautiful_data
4. **Safe get pattern**: Use hasattr() checks before .get() for coroutines

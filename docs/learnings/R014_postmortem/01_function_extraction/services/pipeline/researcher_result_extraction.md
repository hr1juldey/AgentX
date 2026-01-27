# researcher_result.py - Function Extraction

## File: services/pipeline/researcher_result.py

### Primary Purpose
Build the final RESEARCHER agent output dictionary with all processed research data.

### Key Functions

#### `build_researcher_result(...) -> dict`
**Purpose**: Assemble complete researcher result from all pipeline stages.

**Parameters**:
- `raw_data`: Filtered search results (from SearXNG)
- `beautiful_data`: Processed beautiful data (key_facts, trends, comparisons, extracted_numbers)
- `structured_data`: Structured data from structurer
- `citations`: Citation list from citation builder
- `analysis`: Original analysis from ANALYST agent
- `url_list`: Optional list of searched URLs

**Return structure**:
```python
{
    "raw_data": list,              # Original search results
    "documents": list,             # Alias for orchestration compatibility
    "beautiful_data": {
        "key_facts": list,
        "trends": list,
        "comparisons": list,
        "extracted_numbers": list  # For charting
    },
    "structured_data": dict,       # From structurer
    "citations": list,             # From citation builder
    "structured_report": str,      # Generated summary report
    "data_type": str,              # Determined data type
    "query": str,                  # Original query
    "search_terms": list,          # Search terms used
    "url_list": list               # URLs searched
}
```

**Key features**:
- Dual keys: `raw_data` and `documents` for compatibility
- Includes `extracted_numbers` for chart/table hydrators
- Generates `structured_report` summary
- Determines `data_type` for downstream routing

---

### Architectural Patterns

1. **Result aggregation**: Combines outputs from multiple pipeline stages
2. **Backward compatibility**: Uses dual keys (`raw_data`/`documents`) for orchestration
3. **Helper delegation**: Uses helper functions for summary generation and data type determination
4. **Safe extraction**: Uses `hasattr()` checks before calling `.get()` on potentially non-dict objects

---

### Dependencies

**Internal**:
- `services.pipeline.researcher_helpers`:
  - `determine_data_type()`: Classifies data type
  - `generate_summary_report()`: Creates narrative summary

**External**:
- None

---

### Usage Example

```python
from services.pipeline.researcher_result import build_researcher_result

# After running researcher pipeline
researcher_result = build_researcher_result(
    raw_data=filtered_search_results,
    beautiful_data=beautiful_data,
    structured_data=structured_data,
    citations=citations,
    analysis=analyst_output,
    url_list=searched_urls
)

# Access results
print(f"Found {len(researcher_result['documents'])} documents")
print(f"Data type: {researcher_result['data_type']}")
print(f"Extracted {len(researcher_result['beautiful_data']['extracted_numbers'])} numbers")
```

---

### Key Insights

1. **Aliases for compatibility**: `documents` alias ensures orchestration layer can find data
2. **Data type routing**: `data_type` field tells downstream agents how to handle results
3. **Number extraction support**: `extracted_numbers` enables chart hydrators
4. **Summary generation**: `structured_report` provides human-readable summary
5. **Safe dict access**: Uses `hasattr()` checks before `.get()` to handle coroutine/dict confusion

---

### Integration Points

**Called by**:
- `services/pipeline/researcher.py` (main RESEARCHER agent orchestration)

**Calls**:
- `services.pipeline.researcher_helpers.determine_data_type()`
- `services.pipeline.researcher_helpers.generate_summary_report()`

---

### Testing Considerations

**Test scenarios**:
1. Complete result with all fields populated
2. Beautiful data as dict vs non-dict object
3. Citations as list vs non-list object
4. Empty raw_data
5. Missing analysis fields

---

### Lessons Learned

1. **Aliases are necessary**: Different parts of system expect different key names (`raw_data` vs `documents`)
2. **Safe extraction is critical**: DSPy coroutines look like dicts but aren't - need `hasattr()` checks
3. **Data type matters**: Downstream agents need to know if data is chartable, textual, etc.
4. **Number extraction is key**: Enables chart hydrators to find table/chart data
5. **Summary reports are useful**: Human-readable narrative is easier to consume than raw data

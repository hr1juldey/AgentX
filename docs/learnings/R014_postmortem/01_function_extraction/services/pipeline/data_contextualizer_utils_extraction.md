# data_contextualizer_utils.py - Function Extraction

## File: services/pipeline/data_contextualizer_utils.py

### Primary Purpose
Utility functions for data contextualization - fact extraction.

### Key Functions

#### `extract_top_facts(contextualized_data: list) -> list`
**Purpose**: Extract top facts from contextualized data.

**Logic**:
1. Return empty list if no data
2. For each of first 5 items:
   - If dict with `title`: use title
   - Else if dict with `text`: use first 100 chars of text
   - Else: use first 100 chars of string representation

**Returns**: List of top fact strings (max 5).

**Use case**: Display key findings in UI or pass to downstream agents.

---

### Architectural Patterns

1. **Simple extraction**: Basic string extraction from data
2. **Field priority**: Prefers title over text over generic
3. **Truncation**: Limits text to 100 chars for readability

---

### Dependencies

**Internal**:
- None (standalone utilities)

---

### Lessons Learned

1. **Top facts are valuable**: Quick summary of key findings
2. **Field priority**: Title > text > generic string
3. **Limit output**: 5 facts max, 100 chars max - keeps UI clean

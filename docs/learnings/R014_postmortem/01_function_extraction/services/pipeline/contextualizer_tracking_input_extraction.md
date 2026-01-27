# contextualizer_tracking_input.py - Function Extraction

## File: services/pipeline/contextualizer_tracking_input.py

### Primary Purpose
Track data entering the DATA CONTEXTUALIZER - shows what fields are present in input.

### Key Functions

#### `track_input_data(research_data: dict) -> None`
**Purpose**: Log detailed information about input data structure.

**Logs**:
- `raw_data`: Count of items
- `beautiful_data keys`: List of keys
- `beautiful_data list item counts`: Count per list field
- `structured_data keys`: First 5 keys
- `query`: First 50 chars + length
- `search_terms`: Count of terms

**Purpose**: Debug visibility into what data is being received.

---

### Architectural Patterns

1. **Input validation tracking**: Verify expected fields are present
2. **Debug visibility**: Show data structure and counts
3. **Truncated display**: Limit output length for readability

---

### Dependencies

**Internal**:
- None (standalone)

**External**:
- `logging`: Standard logging

---

### Lessons Learned

1. **Track input structure**: Helps diagnose missing fields
2. **Show counts**: Knowing data volume helps debug performance
3. **Truncate strings**: Don't log entire query - first 50 chars is enough

# contextualizer_tracking_output.py - Function Extraction

## File: services/pipeline/contextualizer_tracking_output.py

### Primary Purpose
Track final output assembly - shows what data is being passed to next stage.

### Key Functions

#### `track_build_return(...) -> None`
**Purpose**: Log detailed information about output being assembled.

**Parameters**:
- `beautiful_data`: Beautiful data dict
- `contextualized_data_final`: Final contextualized data list
- `top_facts`: Extracted top facts list
- `research_data`: Original research data

**Logs**:
- `beautiful_data`: Keys and list item counts
- `contextualized_data`: Document count
- `top_facts`: Item count
- Preserved fields from research_data: structured_report, structured_data, query, citations, url_list, documents

**Purpose**: Debug visibility into what data is being passed forward.

---

### Architectural Patterns

1. **Output validation**: Verify expected fields are present
2. **Preservation tracking**: Show which original fields are being kept
3. **Type-aware logging**: Different log formats for list/dict/string

---

### Dependencies

**Internal**:
- None (standalone)

**External**:
- `logging`: Standard logging

---

### Lessons Learned

1. **Track output structure**: Verify all expected fields are present
2. **Show preserved fields**: Important to know what data is being passed through
3. **Type-aware logging**: Different formats for list/dict/string improves readability

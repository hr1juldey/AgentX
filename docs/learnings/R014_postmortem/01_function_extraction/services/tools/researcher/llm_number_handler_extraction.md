# Function Postmortem: services/tools/researcher/llm_number_handler.py

## Metadata
- **File**: services/tools/researcher/llm_number_handler.py
- **Lines of Code**: 134
- **Purpose**: LLM-based number extraction handler with error handling and validation
- **Dependencies**: `json`, `logging`, `services.tools.researcher.number_extractor_utils`

---

## Analysis

**File Status**: PRODUCTION UTILITY MODULE

**Purpose**: Encapsulates LLM-based number extraction logic with comprehensive error handling, JSON parsing, validation, and source metadata injection. Interface contract: returns empty list on error (signals regex fallback needed).

---

## Classes Extracted

### Functions

**`extract_numbers_from_document(extractor, content: str, title: str, url: str, doc_index: int, query: str = "") -> list`**
- Extract numbers from document using LLM
- **Parameters**:
  - `extractor`: DSPy ChainOfThought(ExtractDocumentNumbers) instance
  - `content`: Document content text (up to 5000 chars)
  - `title`: Document title for LLM context
  - `url`: Document URL for citation metadata
  - `doc_index`: Document index for logging
  - `query`: Research query for context (optional)
- **Returns**: List of extracted number dicts with source metadata added, or empty list on error
- **Interface Contract**:
  - Returns empty list → caller should use regex fallback
  - Returns non-empty list → extraction succeeded
  - All errors are logged before returning

**Processing Pipeline**:
1. **Input Logging**: Logs content length, has_full_content heuristic (>2000 chars), preview
2. **LLM Invocation**: Calls `extractor(query=query, document_text=content, document_title=title)`
3. **Response Extraction**: Gets `result.structured_numbers`
4. **Markdown Stripping**: Removes ```json wrapper using `strip_markdown_wrapper()`
5. **JSON Parsing**:
   - If str: `json.loads(numbers_str)`
   - If list: Uses directly
   - If other type: Returns empty list with warning
6. **Validation**:
   - Checks for `value` or `numeric_value` key
   - Validates numeric with `float(value)` conversion
   - Skips non-numeric values (e.g., "1970s_level", "N/A", None)
   - Adds source metadata: `source_doc`, `source_title`, `url`
7. **Error Handling**:
   - `json.JSONDecodeError`: Logs warning with raw string, returns []
   - `TypeError`, `AttributeError`: Logs warning with result repr, returns []

**Validation Logic**:
```python
for num in numbers:
    value = num.get("value") or num.get("numeric_value")
    try:
        float(value)  # Validates numeric
        if "value" not in num and "numeric_value" in num:
            num["value"] = num["numeric_value"]  # Normalize key
        num["source_doc"] = doc_index
        num["source_title"] = title
        num["url"] = url
        validated_numbers.append(num)
    except (ValueError, TypeError):
        logger.warning(f"Skipped non-numeric value: {value!r}")
```

---

## File Summary

**Total Classes**: 0 (module-level function)
**Lines of Code**: 134

**Overall Assessment**: Robust error handling with comprehensive logging. Good interface contract (empty list = fallback needed). Numeric validation prevents garbage data. Handles both JSON string and list formats.

**Key Learnings for Real AgentX**:
1. ✅ **Interface contract pattern**: Empty return signals fallback needed, clear contract
2. ✅ **Markdown wrapper stripping**: 14B coder models wrap JSON in ``` blocks
3. ✅ **Dual key handling**: Accepts `value` or `numeric_value`, normalizes to `value`
4. ✅ **Numeric validation**: `float(value)` catches non-numeric strings, prevents downstream errors
5. ✅ **Comprehensive logging**: Logs at each step (input, raw response, parsed, validated)
6. ✅ **Source metadata injection**: Adds doc_index, title, url to every number
7. ⚠️ **Logging verbosity**: 6 log statements per call may be excessive in production

**Reuse for Real AgentX**: ✅ HIGH - Essential pattern for LLM data extraction with fallback. Validation and error handling patterns are reusable. Consider reducing logging verbosity or making it configurable.

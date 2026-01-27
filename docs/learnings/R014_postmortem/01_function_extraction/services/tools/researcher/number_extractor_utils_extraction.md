# Function Postmortem: services/tools/researcher/number_extractor_utils.py

## Metadata
- **File**: services/tools/researcher/number_extractor_utils.py
- **Lines of Code**: 33
- **Purpose**: Utility functions for LLM output processing
- **Dependencies**: None (pure utility module)

---

## Analysis

**File Status**: PRODUCTION UTILITY MODULE

**Purpose**: Strips markdown code block wrapper from LLM output. 14B coder models wrap JSON in ``` blocks for readability, this strips the wrapper before JSON parsing.

---

## Classes Extracted

### Functions

**`def strip_markdown_wrapper(text: str) -> str`**
- Strip markdown code block wrapper from LLM output
- **Parameters**: `text` - Raw LLM output, possibly wrapped in ```
- **Returns**: Cleaned JSON string without markdown wrapper
- **Processing Pipeline**:
  1. Returns early if `not text or not isinstance(text, str)`
  2. Strips whitespace: `text = text.strip()`
  3. Checks for markdown wrapper: `if text.startswith("```")`
  4. Splits by newline: `lines = text.split("\n")`
  5. Filters out markdown lines: `[line for line in lines if not line.strip().startswith("```")]`
  6. Joins and strips: `"\n".join(json_lines).strip()`
  7. Returns original text if no wrapper found

**Filtering Logic**:
```python
if text.startswith("```"):
    lines = text.split("\n")
    # Remove lines that are just ``` or ```json
    json_lines = [line for line in lines if not line.strip().startswith("```")]
    return "\n".join(json_lines).strip()

return text
```

---

## File Summary

**Total Classes**: 0 (module-level function)
**Lines of Code**: 33

**Overall Assessment**: Simple, focused utility for handling coder model output. Good early return for invalid input. List comprehension filtering is clean.

**Key Learnings for Real AgentX**:
1. ✅ **Markdown wrapper detection**: Checks for ``` prefix
2. ✅ **Early return**: Guards against invalid input (None, non-string)
3. ✅ **List comprehension filtering**: Clean removal of markdown lines
4. ✅ **Whitespace handling**: Strips before and after processing
5. ⚠️ **No language detection**: Removes ```json, ```python, etc. but doesn't validate
6. ⚠️ **Edge cases**: Doesn't handle nested ``` blocks or malformed wrappers

**Reuse for Real AgentX**: ✅ MEDIUM - Common pattern for LLM output processing. Consider adding language validation, error handling for malformed wrappers, and support for other code block formats.

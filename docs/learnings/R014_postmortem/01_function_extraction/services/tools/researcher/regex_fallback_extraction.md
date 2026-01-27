# Function Postmortem: services/tools/researcher/regex_fallback.py

## Metadata
- **File**: services/tools/researcher/regex_fallback.py
- **Lines of Code**: 73
- **Purpose**: Regex-based number extraction as fallback when LLM extraction fails
- **Dependencies**: `re`, `logging`

---

## Analysis

**File Status**: PRODUCTION UTILITY MODULE

**Purpose**: Provides regex-based fallback for extracting structured numbers from document text when LLM extraction fails. Handles patterns like "US: 3.7% 2023", "3.7% 2023 US inflation", "GDP 5.2 percent". Returns list of dicts with label, value, unit, context, year, and source metadata.

---

## Classes Extracted

### Constants

**`PATTERNS`** (list[str])
- Three regex patterns for number extraction
- Pattern 1: `"(\w+(?:\s+\w+)*)\s*[:]\s*([\d.]+)\s*([%$])?(?:\s*(\d{4}))?"` - "US: 3.7% 2023"
- Pattern 2: `"([\d.]+)\s*([%$])(?:\s*(\d{4}))?\s*(\w+(?:\s+\w+)*)"` - "3.7% 2023 US inflation"
- Pattern 3: `"(\w+(?:\s+\w+)*)\s*(\d+\.?\d*)\s*(?:percent|%|billion|million|thousand)"` - "GDP 5.2 percent"

### Functions

**`extract_numbers_with_regex(content: str, title: str, url: str, doc_index: int) -> list`**
- Extract numbers using regex patterns as fallback
- Iterates through PATTERNS, matches with `re.finditer(pattern, content, re.IGNORECASE)`
- Parses groups based on pattern structure (number-first vs label-first)
- Converts value_str to float with comma removal
- Returns list of dicts with keys: label, value, unit, context, year, source_doc, source_title, url
- Error handling: Continues to next match if `ValueError` on float conversion

**Pattern Detection Logic**:
```python
if groups[0] and groups[0][0].isdigit():  # Number comes first
    value_str = groups[0]
    unit = groups[1] if len(groups) > 1 else ""
    label = groups[3] if len(groups) > 3 else ""
    year = groups[2] if len(groups) > 2 else None
else:  # Label comes first
    label = groups[0]
    value_str = groups[1]
    unit = groups[2] if len(groups) > 2 else ""
    year = groups[3] if len(groups) > 3 else None
```

---

## File Summary

**Total Classes**: 0 (module-level functions only)
**Lines of Code**: 73

**Overall Assessment**: Clean, focused utility module with well-documented regex patterns. Good fallback strategy when LLM extraction fails. Pattern detection logic handles both number-first and label-first formats.

**Key Learnings for Real AgentX**:
1. ✅ **Regex fallback patterns**: Three patterns cover common data formats (currency, percentage, text labels)
2. ✅ **Group parsing flexibility**: Handles different pattern structures with conditional logic
3. ✅ **Error resilience**: Continues on conversion failures, returns partial results
4. ✅ **Source metadata injection**: Adds doc_index, title, url to every extracted number
5. ⚠️ **Pattern limitation**: Only handles simple patterns, fails on complex tables or nested structures

**Reuse for Real AgentX**: ✅ HIGH - Essential fallback component for any data extraction system. Regex patterns are reusable across domains. Consider adding more patterns for date ranges, geographic data, and formatted numbers (e.g., "1.5M", "3.2B").

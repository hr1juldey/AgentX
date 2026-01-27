# Function Postmortem: services/tools/researcher/link_parser.py

## Metadata
- **File**: services/tools/researcher/link_parser.py
- **Lines of Code**: 48
- **Purpose**: Helper functions for parsing link extraction results
- **Dependencies**: None (pure utility module)

---

## Analysis

**File Status**: PRODUCTION UTILITY MODULE

**Purpose**: Parses DSPy link extraction output and matches with original links. Converts "URL | reason" format to structured dicts with url, text, reason fields.

---

## Classes Extracted

### Functions

**`def parse_relevant_links(relevant_urls: str, original_links: list[dict]) -> list[dict]`**
- Parse relevant URLs from DSPy output and match with original links
- **Parameters**:
  - `relevant_urls`: String output from DSPy with URLs and reasons
  - `original_links`: Original list of link dicts with 'url' and 'text' keys
- **Returns**: List of relevant link dicts with 'reason' field added (max 3)
- **Processing Pipeline**:
  1. Splits `relevant_urls` by newline
  2. Iterates through lines, skips empty or "NONE" lines
  3. Parses "URL | reason" format:
     - Splits on first `|` to separate URL and reason
     - `url_part = line.split("|")[0].strip()`
     - `reason = line.split("|", 1)[1].strip() if "|" in line else ""`
  4. Finds matching link from `original_links` by URL
  5. Builds new dict with keys: url, text, reason
  6. Returns `relevant_links[:3]` (limits to 3 links)

**Parsing Logic**:
```python
for line in relevant_urls.split("\n"):
    line = line.strip()
    if not line or line.upper() == "NONE":
        continue

    if "|" in line:
        url_part = line.split("|")[0].strip()
        reason = line.split("|", 1)[1].strip() if "|" in line else ""

        for link in original_links:
            if link["url"] == url_part:
                relevant_links.append({
                    "url": link["url"],
                    "text": link.get("text", ""),
                    "reason": reason,
                })
                break

return relevant_links[:3]
```

---

## File Summary

**Total Classes**: 0 (module-level function)
**Lines of Code**: 48

**Overall Assessment**: Simple, focused utility for parsing DSPy link output. Good error handling (skips "NONE", empty lines). Matching with original links preserves metadata. Hard limit of 3 links prevents explosion.

**Key Learnings for Real AgentX**:
1. ✅ **"NONE" handling**: Skips lines with no relevant links
2. ✅ **Format parsing**: Handles "URL | reason" format reliably
3. ✅ **Metadata preservation**: Matches with original links to get text field
4. ✅ **Hard limit**: Max 3 links prevents explosion
5. ✅ **Break on match**: Stops searching after finding matching URL
6. ⚠️ **No error handling**: Missing 'url' key in original_links causes KeyError
7. ⚠️ **Case-sensitive matching**: URL comparison is case-sensitive

**Reuse for Real AgentX**: ✅ MEDIUM - Good pattern for parsing structured LLM output. Consider adding error handling, case-insensitive matching, and configurable link limits.

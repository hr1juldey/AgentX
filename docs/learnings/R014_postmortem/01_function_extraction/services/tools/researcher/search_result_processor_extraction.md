# Function Postmortem: services/tools/researcher/search_result_processor.py

## Metadata
- **File**: services/tools/researcher/search_result_processor.py
- **Lines of Code**: 39
- **Purpose**: Extracts and formats search results for OpenGraph rendering
- **Dependencies**: None (pure utility module)

---

## Analysis

**File Status**: PRODUCTION UTILITY MODULE

**Purpose**: Extracts URLs from raw SearXNG search results and formats them for OpenGraph preview rendering. Handles both general/news search (page URLs) and image search (img_src URLs).

---

## Classes Extracted

### Functions

**`extract_url_list(results: list[dict], image_search: bool) -> list[dict]`**
- Extract URLs from search results for OpenGraph rendering
- **Parameters**:
  - `results`: Raw search results from SearXNG
  - `image_search`: Whether this is an image search
- **Returns**: List of URL dicts with keys: url, title, snippet, source, engine
- **Logic**:
  - Iterates through results list
  - **Image search**: Extracts `result.get("img_src", "")` (actual image URL)
  - **General/news search**: Extracts `result.get("url", "")` (page URL)
  - Skips if url is empty or doesn't start with "http"
  - Builds dict with:
    - `url`: Extracted URL (img_src or url)
    - `title`: `result.get("title", "")`
    - `snippet`: `result.get("content", "")[:200]` (truncated to 200 chars)
    - `source`: `result.get("source", "")`
    - `engine`: `result.get("engine", "")`

**Extraction Logic**:
```python
if image_search:
    url = result.get("img_src", "")
else:
    url = result.get("url", "")

if url and url.startswith("http"):
    url_list.append({
        "url": url,
        "title": result.get("title", ""),
        "snippet": result.get("content", "")[:200],
        "source": result.get("source", ""),
        "engine": result.get("engine", ""),
    })
```

---

## File Summary

**Total Classes**: 0 (module-level function)
**Lines of Code**: 39

**Overall Assessment**: Simple, focused utility for result formatting. Good separation of concerns (image vs general search). Snippet truncation prevents bloat. Missing error handling for malformed results.

**Key Learnings for Real AgentX**:
1. ✅ **Search type differentiation**: Separate handling for image vs general search
2. ✅ **URL validation**: Checks for "http" prefix, skips invalid URLs
3. ✅ **Snippet truncation**: Limits to 200 chars, prevents UI bloat
4. ✅ **Metadata preservation**: Keeps source, engine, title for display
5. ⚠️ **No error handling**: Missing `.get()` default values may cause None issues
6. ⚠️ **No deduplication**: Duplicate URLs not filtered

**Reuse for Real AgentX**: ✅ MEDIUM - Good pattern for result formatting. Consider adding error handling, deduplication, and configurable snippet length. Extendable for other search types (video, news, academic).

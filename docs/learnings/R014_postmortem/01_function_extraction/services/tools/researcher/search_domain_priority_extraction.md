# Function Postmortem: services/tools/researcher/search_domain_priority.py

## Metadata
- **File**: services/tools/researcher/search_domain_priority.py
- **Lines of Code**: 76
- **Purpose**: Domain priority scoring for authoritative sources
- **Dependencies**: `typing`

---

## Analysis

**File Status**: PRODUCTION UTILITY MODULE

**Purpose**: Calculates domain priority scores (0-3) for URL ranking. Higher priority = better source. Used for sorting search results by source authority (.gov, .edu, .org > research/news > general > forums).

---

## Classes Extracted

### Functions

**`get_domain_priority(url: str) -> int`**
- Calculate domain priority for authoritative sources
- **Returns**: Priority score (0-3)
- **Priority Levels**:
  - **3**: Government, education, major research institutions (.gov, .edu, .org)
  - **2**: News, research, academic sources (keywords: "research", "academic", "news", "analysis")
  - **1**: Default (general websites)
  - **0**: Forums, social media, Q&A sites (keywords: "forum", "reddit", "quora", "stackexchange")
- **Logic**:
  - Returns 0 if url is falsy
  - Checks url.lower() for priority keywords
  - Returns highest matching priority (order matters)

**`aggregate_and_prioritize_results(all_results: list[Any]) -> list[dict]`**
- Aggregate and deduplicate search results with domain priority sorting
- **Parameters**: `all_results` - List of search result lists from parallel searches
- **Returns**: Aggregated and sorted results (highest priority first)
- **Processing**:
  - Skips Exception instances in results
  - Deduplicates by URL using `seen_urls` set
  - Adds items to `aggregated` list if url not seen
  - Sorts by `get_domain_priority(item.get("url", ""))` in descending order (reverse=True)

**Sorting Logic**:
```python
aggregated.sort(
    key=lambda item: get_domain_priority(item.get("url", "")), reverse=True
)
```

---

## File Summary

**Total Classes**: 0 (module-level functions)
**Lines of Code**: 76

**Overall Assessment**: Simple, effective domain authority scoring. Good deduplication pattern. Priority levels are sensible but may need tuning for specific domains.

**Key Learnings for Real AgentX**:
1. ✅ **Domain authority scoring**: Simple 0-3 scale for source quality ranking
2. ✅ **Deduplication pattern**: `seen_urls` set prevents duplicate results
3. ✅ **Keyword-based detection**: Uses substring matching for domain types
4. ✅ **Priority sorting**: Higher priority sources appear first in results
5. ⚠️ **Keyword collision**: "news" in URL may match false positives (e.g., "fake-news-detector.com")
6. ⚠️ **No TLD parsing**: String matching instead of proper URL parsing (.org in path matches)

**Reuse for Real AgentX**: ✅ MEDIUM - Good foundation for source ranking, but needs refinement. Consider using proper URL parsing (e.g., `urllib.parse`), domain reputation scoring, and configurable priority rules.

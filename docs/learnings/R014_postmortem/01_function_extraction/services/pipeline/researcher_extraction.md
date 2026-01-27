# Function Extraction: services/pipeline/researcher.py

## File Overview
**Path**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/pipeline/researcher.py`
**Purpose**: RESEARCHER Agent - Fetches data via SearXNG, beautifies, structures, and cites
**Lines**: 101
**Phase**: Phase 2 - Beautiful Data + SearXNG

---

## Classes and Functions

### `ResearcherAgent` (Class)

**Purpose**: DSPy Module that orchestrates web search, data beautification, structuring, and citation building.

**Signature**:
```python
class ResearcherAgent(dspy.Module):
    def __init__(self, searxng_url: str = "http://192.168.1.4:8080"):
        # Initializes 4 research tools

    def forward(
        self,
        analysis: dict,
        previous_data: Optional[dict] = None,
    ) -> dict:
```

**Lines**: 32-100

**Key Code Snippet**:
```python
def forward(
    self,
    analysis: dict,
    previous_data: Optional[dict] = None,
) -> dict:
    # Use search_terms if available, otherwise fall back to goal/query
    search_terms = analysis.get("search_terms", [])
    url_list = []
    if search_terms:
        # Multiple search terms - search with each and combine results
        all_results, query_for_display, url_list = execute_multi_term_search(
            self.searcher, search_terms
        )
        sorted_results = sort_and_deduplicate(all_results)
        raw_data_for_beautify = filter_and_log_results(
            sorted_results,
            source_description=f"results from {len(search_terms)} terms",
        )
    else:
        # Fall back to single query
        query = analysis.get("query") or analysis.get("goal") or ""
        raw_results, query_for_display, url_list = execute_single_search(
            self.searcher, query
        )
        sorted_results = sort_and_deduplicate(raw_results)
        raw_data_for_beautify = filter_and_log_results(
            sorted_results, source_description="results from single query"
        )

    # Process data through beautifier, structurer, citation builder
    beautiful_data, structured_data, citations = process_research_data(
        beautifier=self.beautifier,
        structurer=self.structurer,
        citer=self.citer,
        raw_data=raw_data_for_beautify,
        query_display=query_for_display,
    )

    return build_researcher_result(
        raw_data=raw_data_for_beautify,
        beautiful_data=beautiful_data,
        structured_data=structured_data,
        citations=citations,
        analysis=analysis,
        url_list=url_list,
    )
```

**What Works (Success Patterns)**:
1. **Dual-mode search**: Supports both multi-term and single-query search paths
2. **Cascading fallback**: `analysis.get("query") or analysis.get("goal") or ""` ensures valid query
3. **Delegation pattern**: Complex operations delegated to helper functions (search, filter, process, build)
4. **Pipeline flow**: Clear sequence → search → filter/dedupe → beautify → structure → cite → build
5. **URL tracking**: Maintains url_list for citation purposes

**Mistakes Found**:
None - clean pipeline orchestration

**Behavioral Notes**:
- Prefers search_terms from analysis over single query
- Sorts results by SearXNG score (relevance)
- Filters to max_results to limit contextualizer processing time
- Processes data through 3-stage pipeline (beautify → structure → cite)
- Returns data in multiple formats (raw, beautiful, structured, citations)

**Dependencies**:
- `dspy.Module` - Base class
- `services.pipeline.researcher_filter` - filter_and_log_results, sort_and_deduplicate
- `services.pipeline.researcher_process` - process_research_data
- `services.pipeline.researcher_result` - build_researcher_result
- `services.pipeline.researcher_search` - execute_multi_term_search, execute_single_search
- `services.tools.researcher` - SearXNGSearchModule, BeautifierModule, DataStructurerModule, CitationBuilderModule

**Reusability**: High - Generic research orchestration for any query/analysis

---

## Imported Functions (from researcher_helpers.py)

### `generate_summary_report()`

**Purpose**: Generate a summary report from research for display/logging.

**Signature**:
```python
def generate_summary_report(
    beautiful_data: dict,
    citations: list,
    domain: str,
) -> str:
```

**Lines**: researcher_helpers.py 8-36

**Key Code Snippet**:
```python
def generate_summary_report(
    beautiful_data: dict,
    citations: list,
    domain: str,
) -> str:
    parts = []

    key_facts = (
        beautiful_data.get("key_facts", []) if hasattr(beautiful_data, "get") else []
    )
    trends = beautiful_data.get("trends", []) if hasattr(beautiful_data, "get") else []

    if key_facts:
        parts.append("Key findings: " + ", ".join(key_facts[:3]))

    if trends:
        parts.append("Trends: " + ", ".join(trends[:3]))

    return " | ".join(parts) if parts else f"Research completed for {domain}"
```

**What Works**:
- Defensive check with `hasattr()` before calling `.get()`
- Limits to top 3 items for concise summary
- Returns fallback message if no data

**Reusability**: Medium - Specific to beautiful_data structure

### `determine_data_type()`

**Purpose**: Determine the type of data for widget selection (numerical, visual, comparative, general).

**Signature**:
```python
def determine_data_type(analysis: dict, beautiful_data: dict) -> str:
```

**Lines**: researcher_helpers.py 39-59

**Key Code Snippet**:
```python
def determine_data_type(analysis: dict, beautiful_data: dict) -> str:
    query = analysis.get("query", "").lower()
    domain = analysis.get("domain", "").lower()

    if "price" in query or "stock" in query or "finance" in domain:
        return "numerical_time_series"
    if "image" in query or "photo" in query:
        return "visual_image"
    if "comparison" in query:
        return "comparative"

    return "general"
```

**What Works**:
- Simple keyword-based classification
- Case-insensitive matching with `.lower()`
- Returns sensible default ("general")

**Mistakes Found**:
- Keyword-based classification is brittle (doesn't scale)

**Reusability**: Low - Hardcoded keywords limit reusability

---

## Imported Functions (from researcher_filter.py)

### `filter_and_log_results()`

**Purpose**: Filter results by score with comprehensive logging to reduce contextualizer load.

**Signature**:
```python
def filter_and_log_results(
    sorted_results: list,
    source_description: str = "results"
) -> list:
```

**Lines**: researcher_filter.py 20-87

**Key Code Snippet**:
```python
def filter_and_log_results(
    sorted_results: list,
    source_description: str = "results"
) -> list:
    if not sorted_results:
        logger.info(f"[RESEARCHER] No {source_description} to filter")
        return sorted_results

    # Log score distribution
    scores = [r.get("score", 0) for r in sorted_results]
    logger.info(
        f"[RESEARCHER] Score distribution: min={min(scores):.3f}, "
        f"max={max(scores):.3f}, avg={sum(scores) / len(scores):.3f}"
    )

    # Log top results
    top_results = [
        (i + 1, r.get("title", "")[:50], r.get("score", 0))
        for i, r in enumerate(sorted_results[:SCORE_LOG_SAMPLE_SIZE])
    ]
    logger.info(f"[RESEARCHER] Top {len(top_results)} {source_description} by score:")
    for rank, title, score in top_results:
        logger.info(f"    [{rank}] {title}... (score: {score:.3f})")

    # Cap at MAX_RESULTS
    if len(sorted_results) > MAX_RESULTS:
        cutoff_score = sorted_results[MAX_RESULTS - 1].get("score", 0)
        filtered_by_score = sorted_results[:MAX_RESULTS]
        discarded_count = len(sorted_results) - len(filtered_by_score)

        logger.info(
            f"[RESEARCHER] Score filter: {len(sorted_results)} → {len(filtered_by_score)} "
            f"(cutoff score: {cutoff_score:.3f}, discarded: {discarded_count})"
        )

        # Log what's being discarded (sample)
        discarded_sample = sorted_results[
            MAX_RESULTS : MAX_RESULTS + DISCARD_SAMPLE_SIZE
        ]
        if discarded_sample:
            logger.info("[RESEARCHER] Sample discarded results:")
            for r in discarded_sample:
                score = r.get("score", 0)
                title = r.get("title", "")[:40]
                logger.info(f"    [score: {score:.3f}] {title}...")

        return filtered_by_score

    return sorted_results
```

**What Works**:
1. **Score-based filtering**: Uses SearXNG score to prioritize quality
2. **Comprehensive logging**: Shows distribution, top results, discarded samples
3. **Performance optimization**: Limits to MAX_RESULTS (25) to prevent 30+ minute contextualizer runs
4. **Configurable constants**: MAX_RESULTS from settings (Rule 5 compliance)

**Behavioral Notes**:
- 25 results = ~8-13 minutes contextualizer time
- 77 results = 30+ minutes (avoided by filtering)
- Logs cutoff score so user knows filtering threshold

**Reusability**: High - Generic score-based filtering for any search results

### `sort_and_deduplicate()`

**Purpose**: Sort results by score and deduplicate by URL.

**Signature**:
```python
def sort_and_deduplicate(all_results: list) -> list:
```

**Lines**: researcher_filter.py 90-118

**Key Code Snippet**:
```python
def sort_and_deduplicate(all_results: list) -> list:
    # Deduplicate by URL
    seen_urls = set()
    unique_results = []
    for result in all_results:
        url = result.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(result)

    if unique_results:
        logger.info(
            f"[RESEARCHER] After deduplication: {len(unique_results)} unique results"
        )

    # Sort by SearXNG score (descending)
    sorted_results = sorted(
        unique_results, key=lambda r: r.get("score", 0), reverse=True
    )

    return sorted_results
```

**What Works**:
1. **URL deduplication**: Uses set for O(1) lookup
2. **Score sorting**: Descending order puts highest quality first
3. **Empty URL handling**: Skips results without URLs

**Reusability**: High - Generic deduplication and sorting for any search results

---

## Key Patterns

1. **Dual-Mode Search Pattern**:
```python
if search_terms:
    # Multi-term path
else:
    # Single query fallback
```

2. **Score-Based Filtering Pattern**:
```python
sorted_results = sorted(unique_results, key=lambda r: r.get("score", 0), reverse=True)
filtered_by_score = sorted_results[:MAX_RESULTS]
```

3. **Safe DSPy Result Pattern**:
```python
result_raw = self.tool(params)
result = result_raw if hasattr(result_raw, "get") else {}
```

---

## Lessons Learned

1. **Filter for performance**: Limiting results to MAX_RESULTS prevents runaway contextualizer times
2. **Score-based quality**: SearXNG scores provide reliable quality signal for filtering
3. **Content enrichment improves extraction**: Fetching full content significantly improves number extraction
4. **Alias for compatibility**: Multiple field names (raw_data/documents) improve integration flexibility
5. **Comprehensive logging aids debugging**: Score distribution, top results, and discarded samples help troubleshoot

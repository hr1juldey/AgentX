# researcher_process.py - Function Extraction

## File: services/pipeline/researcher_process.py

### Primary Purpose
Execute the RESEARCHER data processing pipeline: beautifier, structurer, citation builder, and number extraction.

### Key Functions

#### `enrich_raw_data_with_content(raw_data: list, max_fetch: int = 10) -> list`
**Purpose**: Fetch full page content for top documents to improve number extraction.

**Logic**:
1. Extract URLs from top documents (max_fetch limit)
2. Run async `fetch_multiple_pages()` in sync context (handles running event loops)
3. Create URL → content mapping
4. Add `full_content` field to raw_data for fetched URLs

**Key challenge**: Async fetch in sync context - uses ThreadPoolExecutor if event loop is running.

**Returns**: Enriched raw_data with `full_content` field added to top documents.

---

#### `process_research_data(...) -> tuple`
**Purpose**: Process raw search data through beautifier, structurer, citation builder, and number extractor.

**Parameters**:
- `beautifier`: BeautifierModule instance
- `structurer`: DataStructurerModule instance
- `citer`: CitationBuilderModule instance
- `raw_data`: Filtered search results
- `query_display`: Query string for display

**Pipeline steps**:
1. **Beautify raw data**: `beautifier(raw_data, query)` → beautiful_data
2. **Enrich with full content**: `enrich_raw_data_with_content(raw_data, 10)`
3. **Extract numbers**: `number_extractor(raw_data=enriched_raw_data)` → extracted_numbers
4. **Add numbers to beautiful_data**: `beautiful_data["extracted_numbers"] = extracted_numbers`
5. **Structure data**: `structurer(beautiful_data=beautiful_data)` → structured_data
6. **Build citations**: `citer(raw_data=raw_data, writing=structured_report)` → citations

**Returns**: Tuple of (beautiful_data, structured_data, citations)

---

### Architectural Patterns

1. **Sequential pipeline**: Each step transforms data for the next
2. **Async/sync bridge**: Handles async fetch in sync context with ThreadPoolExecutor
3. **Data enrichment**: Adds full_content to improve downstream processing
4. **Number extraction enhancement**: New addition to support chart/table data

---

### Dependencies

**Internal**:
- `services/tools/researcher/number_extractor.py`: NumberExtractorModule
- `services/tools/researcher/web_fetcher.py`: fetch_multiple_pages

**External**:
- `asyncio`: Async runtime
- `concurrent.futures.ThreadPoolExecutor`: Thread pool for async operations
- `logging`: Standard logging
- `typing.cast`: Type casting

---

### Usage Example

```python
from services.pipeline.researcher_process import process_research_data
from services.tools.researcher.beautifier import BeautifierModule
from services.tools.researcher.structurer import DataStructurerModule
from services.tools.researcher.citation_builder import CitationBuilderModule

# Initialize modules
beautifier = BeautifierModule()
structurer = DataStructurerModule()
citer = CitationBuilderModule()

# Process search results
beautiful_data, structured_data, citations = process_research_data(
    beautifier=beautifier,
    structurer=structurer,
    citer=citer,
    raw_data=filtered_search_results,
    query_display="sales data by quarter"
)

# Access processed data
key_facts = beautiful_data["key_facts"]
extracted_numbers = beautiful_data["extracted_numbers"]  # NEW
structured_report = structured_data["structured_report"]
```

---

### Key Insights

1. **Content enrichment improves number extraction**: Full page content is better than snippets for extracting chart/table data
2. **Async fetch is complex**: Need to handle both running and non-running event loops
3. **Limited fetch for performance**: Only fetch top 10 documents to balance quality vs latency
4. **Number extraction is new**: Recent addition to support charting hydrators
5. **Sequential dependency**: Each step depends on previous step output

---

### Integration Points

**Called by**:
- `services/pipeline/researcher.py` (main RESEARCHER agent orchestration)

**Calls**:
- `services/tools/researcher/number_extractor.NumberExtractorModule`
- `services/tools/researcher/web_fetcher.fetch_multiple_pages`
- BeautifierModule, DataStructurerModule, CitationBuilderModule (passed as params)

---

### Testing Considerations

**Test scenarios**:
1. Successful content enrichment with valid URLs
2. Failed fetch (network error) - should return original raw_data
3. Empty raw_data handling
4. Number extraction from enriched content
5. Sequential pipeline execution

---

### Lessons Learned

1. **Full content is worth the fetch**: Number extraction quality improves significantly with full page content
2. **Async in sync context is tricky**: Need ThreadPoolExecutor wrapper when event loop is running
3. **Limit fetch count**: Don't fetch all pages - top 10 is enough for number extraction
4. **Data flow matters**: Order of operations (beautify → enrich → extract → structure → cite) is critical
5. **Number extraction enables charting**: This is the foundation for chart hydrators

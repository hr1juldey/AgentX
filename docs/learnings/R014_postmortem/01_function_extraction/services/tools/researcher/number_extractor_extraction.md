# Function Extraction: services/tools/researcher/number_extractor.py

## File Overview
**Path**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/tools/researcher/number_extractor.py`
**Purpose**: Extract structured numbers from research documents for chart/table data
**Lines**: 110

---

## Classes and Functions

### `NumberExtractorModule` (DSPy Module)

**Purpose**: Extract structured numbers from research documents with LLM and regex fallback.

**Signature**:
```python
class NumberExtractorModule(dspy.Module):
    def __init__(self, max_documents: int = 10):
        super().__init__()
        self.extractor = dspy.ChainOfThought(ExtractDocumentNumbers)
        self.max_documents = max_documents

    def forward(self, raw_data: list, query: str = "") -> dict[str, Any]:
```

**Lines**: 17-96

**Key Code Snippet**:
```python
def forward(self, raw_data: list, query: str = "") -> dict[str, Any]:
    """Extract numbers from research documents."""
    from services.tools.researcher.llm_number_handler import (
        extract_numbers_from_document,
    )
    from services.tools.researcher.regex_fallback import extract_numbers_with_regex

    extracted_numbers = []
    processed_docs = raw_data[: self.max_documents]

    logger.info(
        f"[NUMBER_EXTRACTOR] Processing {len(raw_data)} documents (max: {self.max_documents})"
    )

    for index, doc in enumerate(processed_docs):
        # Prioritize full_content if available, fallback to snippet
        content = (doc.get("full_content", "") or doc.get("content", ""))[:5000]
        title = doc.get("title", "")
        url = doc.get("url", "")

        if not content or len(content) < 50:
            logger.warning(
                f"[NUMBER_EXTRACTOR] Skipped doc {index}: content_len={len(content)}",
            )
            continue

        # Try LLM extraction
        numbers = extract_numbers_from_document(
            extractor=self.extractor,
            content=content,
            title=title,
            url=url,
            doc_index=index,
            query=query,
        )

        if numbers:
            logger.info(f"[NUMBER_EXTRACTOR] LLM extracted {len(numbers)} numbers")
            extracted_numbers.extend(numbers)
        else:
            # LLM failed, use regex fallback
            regex_result = extract_numbers_with_regex(content, title, url, index)
            logger.info(
                f"[NUMBER_EXTRACTOR] Regex extracted {len(regex_result)} numbers"
            )
            extracted_numbers.extend(regex_result)

    # Deduplicate and return
    extracted_numbers = self._deduplicate(extracted_numbers)
    logger.info(f"[NUMBER_EXTRACTOR] Total after dedup: {len(extracted_numbers)}")

    return {
        "extracted_numbers": extracted_numbers,
        "metadata": {
            "total_numbers": len(extracted_numbers),
            "documents_processed": len(processed_docs),
            "extraction_method": "llm",
            "has_year_data": any(n.get("year") for n in extracted_numbers),
        },
    }
```

**What Works (Success Patterns)**:
1. **Dual extraction strategy**: LLM with regex fallback ensures robustness
2. **Content prioritization**: Uses `full_content or content` pattern for best data source
3. **Length limiting**: `[:5000]` prevents token overflow
4. **Minimum content check**: Skips docs with < 50 chars to avoid noise
5. **Deduplication**: Removes duplicate numbers based on (label, value, year) tuple

**Mistakes Found**:
None - robust dual-strategy extraction

**Behavioral Notes**:
- Processes up to max_documents (default 10)
- Prioritizes full_content over snippet
- Falls back to regex if LLM fails
- Deduplicates based on label+value+year
- Returns metadata about extraction

**Dependencies**:
- `services.tools.researcher.llm_number_handler` - extract_numbers_from_document
- `services.tools.researcher.regex_fallback` - extract_numbers_with_regex
- `services.tools.hydrators.chart_signatures` - ExtractDocumentNumbers

**Reusability**: High - Generic number extraction for any document list

---

### `_deduplicate()` (Method)

**Purpose**: Remove duplicate numbers based on label+value+year tuple.

**Signature**:
```python
def _deduplicate(self, numbers: list) -> list:
```

**Lines**: 98-109

**Key Code Snippet**:
```python
def _deduplicate(self, numbers: list) -> list:
    """Remove duplicate numbers based on label+value+year."""
    seen = set()
    unique = []

    for num in numbers:
        key = (num.get("label"), num.get("value"), num.get("year"))
        if key not in seen:
            seen.add(key)
            unique.append(num)

    return unique
```

**What Works**:
- Uses tuple as set key for O(1) lookup
- Preserves insertion order (first occurrence kept)

**Reusability**: High - Generic deduplication for any structured data

---

## Key Patterns

1. **Dual-Strategy Extraction Pattern**:
```python
# Try primary method
numbers = extract_numbers_from_document(...)
if numbers:
    extracted_numbers.extend(numbers)
else:
    # Fallback to secondary method
    regex_result = extract_numbers_with_regex(...)
    extracted_numbers.extend(regex_result)
```

2. **Content Prioritization Pattern**:
```python
content = (doc.get("full_content", "") or doc.get("content", ""))[:5000]
```

3. **Minimum Quality Check Pattern**:
```python
if not content or len(content) < 50:
    logger.warning(f"Skipped doc {index}: content_len={len(content)}")
    continue
```

4. **Tuple-Based Deduplication Pattern**:
```python
key = (num.get("label"), num.get("value"), num.get("year"))
if key not in seen:
    seen.add(key)
    unique.append(num)
```

---

## Lessons Learned

1. **Always have a fallback**: LLM → Regex ensures extraction always succeeds
2. **Prioritize full content**: full_content has more data than snippet
3. **Limit token count**: [:5000] prevents overflow while preserving data
4. **Skip low-quality inputs**: < 50 chars is likely noise
5. **Deduplicate on compound key**: label+value+year uniquely identifies a data point

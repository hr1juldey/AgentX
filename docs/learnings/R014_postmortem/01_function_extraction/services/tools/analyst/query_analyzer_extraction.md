# Function Postmortem: services/tools/analyst/query_analyzer.py

## Metadata
- **File**: services/tools/analyst/query_analyzer.py
- **Lines of Code**: 100
- **Purpose**: Analyzes query context and extracts insights with chunking
- **Dependencies**: dspy, typing, services.core.chunking

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE - ITERATIVE CHUNKING PATTERN

**Purpose**: Two modules that analyze query context (type, domain, urgency) and extract insights using iterative chunking for large texts.

---

## Classes Extracted

### ContextAnalyzerModule

**Purpose**: DSPy Module that analyzes query context across three dimensions.

**Lines**: 11-31

**Key Code**:
```python
class ContextAnalyzerModule(dspy.Module):
    """Analyzes the context and domain of the user query."""

    def __init__(self):
        super().__init__()
        self.detect_type = dspy.Predict("query -> query_type")
        self.extract_domain = dspy.Predict("query -> domain")
        self.identify_urgency = dspy.Predict("query -> urgency")

    def forward(self, query: str) -> dict:
        """Analyze query context."""
        type_result = self.detect_type(query=query)
        domain_result = self.extract_domain(query=query)
        urgency_result = self.identify_urgency(query=query)

        return {
            "query_type": type_result.query_type,  # type: ignore[attr-defined]
            "domain": domain_result.domain,  # type: ignore[attr-defined]
            "urgency": urgency_result.urgency,  # type: ignore[attr-defined]
        }
```

**What Works**:
- ✅ Three parallel analyses (type, domain, urgency)
- ✅ Simple string-based API
- ✅ Type ignore comments for mypy/pyrefly

**Mistakes Found**:
- ⚠️ No fallback if attributes are missing
- ⚠️ No validation of returned values

**Behavioral Notes**:
- Runs three independent predictions in parallel
- Uses type ignore for dynamic attributes
- Returns dict with three string fields

**Dependencies**:
- **Imports**: dspy, typing.List
- **Uses**: dspy.Predict(), type ignore comments

**Reusability**: HIGH - Pattern applies to any multi-dimensional analysis

### InsightExtractorModule

**Purpose**: DSPy Module that extracts insights using decision tree and iterative chunking.

**Lines**: 33-100

**Key Code**:
```python
class InsightExtractorModule(dspy.Module):
    """Extracts insights using chunking + iterative refinement.

    Uses decision tree:
    1. If text < 500 chars → direct extraction
    2. If text > 500 chars → chunk + iterate 3 times
    3. Deduplicate results
    """

    MAX_CHUNK_SIZE = 500
    OVERLAP = 100
    ITERATIONS = 3

    def __init__(self):
        super().__init__()
        from services.tools.analyst.signatures import (
            ExtractInitialInsights,
            RefineInsights,
        )

        self.initial_extractor = dspy.Predict(ExtractInitialInsights)
        self.refiner = dspy.Predict(RefineInsights)

    def forward(self, query: str) -> dict:
        # Decision tree: small query?
        if len(query) <= self.MAX_CHUNK_SIZE:
            return self._extract_single(query)

        # Large query: chunk + iterate
        return self._extract_iterative(query)

    def _extract_single(self, query: str) -> dict:
        """Fast path for small queries."""
        result = self.initial_extractor(text_chunk=query)
        insights = self._parse_insights(result.insights)
        return {"insights": insights, "key_questions": []}

    def _extract_iterative(self, query: str) -> dict:
        """Chunk + iterate for large text."""
        from services.core.chunking import chunk_text, deduplicate_items

        chunks = chunk_text(query, self.MAX_CHUNK_SIZE, self.OVERLAP)
        all_insights = []
        existing = ""

        for i, chunk in enumerate(chunks[: self.ITERATIONS]):
            if i == 0:
                result = self.initial_extractor(text_chunk=chunk)
                all_insights.extend(self._parse_insights(result.insights))
            else:
                result = self.refiner(text_chunk=chunk, existing_insights=existing)
                all_insights.extend(self._parse_insights(result.new_insights))

            existing = ", ".join([ins[:30] for ins in all_insights])

        unique_insights = deduplicate_items(all_insights)
        return {"insights": unique_insights, "key_questions": []}

    def _parse_insights(self, insights_str: str) -> List[str]:
        """Parse insight string into list."""
        if not insights_str:
            return []
        return [
            line.strip().lstrip("-").strip()
            for line in insights_str.split("\n")
            if line.strip() and line.strip().startswith("-")
        ]
```

**What Works**:
- ✅ Decision tree pattern (fast path for small, chunking for large)
- ✅ Iterative refinement with existing insights context
- ✅ Overlapping chunks to preserve context
- ✅ Deduplication of results
- ✅ Bullet list parsing (strips "-" prefix)
- ✅ Limited iterations (3 chunks max)

**Mistakes Found**:
- ⚠️ Hard-coded chunk size (500) and overlap (100)
- ⚠️ Assumes insights are bullet lists (starts with "-")
- ⚠️ Truncates existing insights to 30 chars (might lose context)

**Behavioral Notes**:
- First chunk uses initial_extractor, subsequent use refiner
- Builds "existing" context from previous insights
- Parses bullet lists (lines starting with "-")
- Deduplicates final results

**Dependencies**:
- **Imports**: dspy, typing.List, chunk_text, deduplicate_items
- **Uses**: dspy.Predict(), str.split(), enumerate(), list comprehension

**Reusability**: VERY HIGH - Iterative chunking pattern applies to any large text processing

---

## File Summary

**Total Classes**: 2
**Lines of Code**: 100

**Overall Assessment**: EXCELLENT iterative chunking implementation. The decision tree pattern (fast path for small, chunking for large) is production-ready. The bullet list parser is clever but assumes specific format.

**Key Learnings for Real AgentX**:
1. ✅ Use decision tree pattern: check size first, then choose strategy
2. ✅ Fast path for small inputs (no chunking overhead)
3. ✅ Iterative refinement: pass previous results as context to next iteration
4. ✅ Use overlapping chunks (OVERLAP = 100) to preserve context at boundaries
5. ✅ Limit iterations to prevent runaway processing (ITERATIONS = 3)
6. ✅ Deduplicate results from multiple chunks
7. ✅ Parse specific formats (bullet lists) with lstrip("-")
8. ⚠️ Make chunk size configurable per model context window
9. ⚠️ Don't truncate context (30 chars might be too short)

**Reuse for Real AgentX**: ✅ DIRECT - Use this iterative chunking pattern for any large text extraction/summarization

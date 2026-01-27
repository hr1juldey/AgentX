# Function Postmortem: services/tools/researcher/data_processor.py

## Metadata
- **File**: services/tools/researcher/data_processor.py
- **Lines of Code**: 134
- **Purpose**: Beautifies and structures data for presentation
- **Dependencies**: dspy, typing

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE - CHUNKING PATTERN

**Purpose**: Two modules that beautify raw search data and structure it using chunking for large inputs.

---

## Classes Extracted

### BeautifierModule

**Purpose**: DSPy Module that extracts facts, trends, and comparisons from raw search data.

**Lines**: 11-39

**Key Code**:
```python
class BeautifierModule(dspy.Module):
    """Beautifies raw search data for presentation."""

    def __init__(self):
        super().__init__()
        self.extract_facts = dspy.Predict("raw_data -> key_facts")
        self.identify_trends = dspy.Predict("raw_data -> trends")
        self.create_comparisons = dspy.Predict("raw_data, query -> comparisons")

    def forward(self, raw_data: list, query: str) -> dict:
        """Beautify raw search data."""
        facts_result = self.extract_facts(raw_data=str(raw_data[:5]))
        trends_result = self.identify_trends(raw_data=str(raw_data[:5]))
        comparisons_result = self.create_comparisons(
            raw_data=str(raw_data[:5]), query=query
        )

        return {
            "key_facts": [facts_result.key_facts]
            if hasattr(facts_result, "key_facts")
            else [],
            "trends": [trends_result.trends]
            if hasattr(trends_result, "trends")
            else [],
            "comparisons": [comparisons_result.comparisons]
            if hasattr(comparisons_result, "comparisons")
            else [],
        }
```

**What Works**:
- ✅ Three parallel extractions (facts, trends, comparisons)
- ✅ Limits input to first 5 results (prevents token overflow)
- ✅ Wraps single items in lists for consistency
- ✅ Simple string-based API

**Mistakes Found**:
- ⚠️ Wrapping single items in lists is inconsistent (should extract actual lists)
- ⚠️ No validation that results are actually different from each other
- ⚠️ Hard-coded slice [:5] might be too restrictive

**Behavioral Notes**:
- Converts raw_data list to string for LLM
- Limits to first 5 items to manage context window
- Returns dict with three list fields
- Uses hasattr() for safe attribute access

**Dependencies**:
- **Imports**: dspy
- **Uses**: dspy.Predict(), hasattr()

**Reusability**: MEDIUM - Pattern is good but implementation has issues

### StructureDataChunk (Signature)

**Purpose**: DSPy Signature for structuring a chunk of data into organized sections.

**Lines**: 41-48

**Key Code**:
```python
class StructureDataChunk(dspy.Signature):
    """Structure a chunk of data into organized sections."""

    data_chunk: str = dspy.InputField(desc="Data to structure (max 500 chars)")
    key_facts: str = dspy.OutputField(desc="Key facts from data, numbered 1-5")
    trends: str = dspy.OutputField(desc="Trends from data, numbered 1-3")
    comparisons: str = dspy.OutputField(desc="Comparisons from data, numbered 1-2")
```

**What Works**:
- ✅ Clear size constraint (max 500 chars)
- ✅ Numbered list format for consistent parsing
- ✅ Separate fields for different content types

**Mistakes Found**: None - good signature design

**Behavioral Notes**:
- Uses numbered list format (1-5, 1-3, 1-2) for parsing
- Size limit prevents context overflow

**Dependencies**:
- **Uses**: dspy.Signature, dspy.InputField, dspy.OutputField

**Reusability**: HIGH - Good pattern for chunked data processing

### DataStructurerModule

**Purpose**: DSPy Module that structures data using ChainOfThought with intelligent chunking.

**Lines**: 50-134

**Key Code**:
```python
class DataStructurerModule(dspy.Module):
    """Structures data using ChainOfThought + chunking."""

    MAX_CHUNK_SIZE = 500

    def __init__(self):
        super().__init__()
        self.structurer = dspy.ChainOfThought(StructureDataChunk)

    def forward(self, beautiful_data: dict) -> dict:
        """Structure data by processing chunks and combining."""
        data_str = self._format_data(beautiful_data)

        if len(data_str) <= self.MAX_CHUNK_SIZE:
            return self._structure_single(data_str)

        return self._structure_chunked(data_str)

    def _structure_single(self, data_str: str) -> dict:
        """Fast path for small data."""
        result = self.structurer(data_chunk=data_str)

        return {
            "structured_data": {
                "key_facts": self._parse_numbered(result.key_facts),
                "trends": self._parse_numbered(result.trends),
                "comparisons": self._parse_numbered(result.comparisons),
            }
        }

    def _structure_chunked(self, data_str: str) -> dict:
        """Process data in chunks and combine."""
        sections = data_str.split("\n\n")
        chunks = []
        current_chunk = []
        current_size = 0

        for section in sections:
            if current_size + len(section) > self.MAX_CHUNK_SIZE:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [section]
                current_size = len(section)
            else:
                current_chunk.append(section)
                current_size += len(section)

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        all_facts = []
        all_trends = []
        all_comparisons = []

        for chunk in chunks:
            result = self.structurer(data_chunk=chunk)
            all_facts.extend(self._parse_numbered(result.key_facts))
            all_trends.extend(self._parse_numbered(result.trends))
            all_comparisons.extend(self._parse_numbered(result.comparisons))

        return {
            "structured_data": {
                "key_facts": all_facts[:5],
                "trends": all_trends[:3],
                "comparisons": all_comparisons[:2],
            }
        }

    def _parse_numbered(self, text: str) -> List[str]:
        """Parse numbered list into array."""
        items = []
        for line in text.split("\n"):
            line = line.strip()
            if any(line.startswith(f"{i}.") for i in range(1, 10)):
                items.append(line)
        return items

    def _format_data(self, data: dict) -> str:
        """Format dict to string."""
        parts = []
        if "key_facts" in data:
            parts.append("Key Facts:\n" + "\n".join(data["key_facts"]))
        if "trends" in data:
            parts.append("\nTrends:\n" + "\n".join(data["trends"]))
        return "\n\n".join(parts)
```

**What Works**:
- ✅ Fast path for small data (no chunking overhead)
- ✅ Intelligent chunking by paragraph sections (preserves context)
- ✅ Numbered list parser (1-9) with any() check
- ✅ Caps output at specific counts (5 facts, 3 trends, 2 comparisons)
- ✅ Uses ChainOfThought for better reasoning
- ✅ Combines chunked results with extend()

**Mistakes Found**:
- ⚠️ Chunk size (500) might be too small for some models
- ⚠️ Numbered list parser only handles 1-9 (what about 10+?)
- ⚠️ Paragraph splitting (\n\n) might break mid-sentence

**Behavioral Notes**:
- Checks data size first (fast path for small data)
- Splits by paragraphs to preserve sentence context
- Processes chunks independently and combines results
- Parses numbered lists using pattern matching
- Limits final output to prevent bloat

**Dependencies**:
- **Imports**: dspy, typing.List
- **Uses**: dspy.ChainOfThought(), str.split(), list.extend(), slicing [:5]

**Reusability**: HIGH - Chunking pattern applies to any large data processing

---

## File Summary

**Total Classes**: 3 (2 modules + 1 signature)
**Lines of Code**: 134

**Overall Assessment**: EXCELLENT chunking pattern implementation. The fast path for small data and intelligent paragraph-based chunking are production-ready. The numbered list parser is clever but has limitations (1-9 only).

**Key Learnings for Real AgentX**:
1. ✅ Use fast path for small data (check size before chunking)
2. ✅ Chunk by semantic units (paragraphs, not arbitrary character counts)
3. ✅ Use ChainOfThought for better reasoning on complex tasks
4. ✅ Parse numbered lists with pattern matching: `any(line.startswith(f"{i}.") for i in range(1, 10))`
5. ✅ Combine chunked results with extend() (not append)
6. ✅ Cap final output to prevent bloat ([:5], [:3], [:2])
7. ⚠️ Consider using regex for numbered list parsing (handles 10+)
8. ⚠️ Make MAX_CHUNK_SIZE configurable per model context size

**Reuse for Real AgentX**: ✅ DIRECT - Use this chunking pattern for any large data processing with LLMs

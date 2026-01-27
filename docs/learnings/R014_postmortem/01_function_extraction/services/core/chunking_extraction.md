# Function Postmortem: services/core/chunking.py

## Metadata
- **File**: services/core/chunking.py
- **Lines of Code**: 96
- **Purpose**: Text chunking utilities for processing large inputs in smaller pieces
- **Dependencies**: `typing`

---

## Analysis

**File Status**: PRODUCTION INFRASTRUCTURE

**Purpose**: Provides utilities for chunking text and lists, deduplicating items, and iterative refinement.

---

## Functions Extracted

### chunk_text

**Purpose**: Split text into overlapping chunks

**Signature**:
```python
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]
```

**Lines**: 12-32

**Complexity**: O(n) where n is length of text

**Key Code**:
```python
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks.

    Args:
        text: Full text to chunk
        chunk_size: Target chunk size in characters
        overlap: Overlap between chunks

    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start = end - overlap if end < len(text) else len(text)
    return chunks
```

**What Works**:
- ✅ Fast path for small text (returns single chunk)
- ✅ Overlapping chunks (prevents content split at boundaries)
- ✅ Handles end condition correctly
- ✅ Default values: chunk_size=500, overlap=100 (tuned for qwen3:8b)

**Mistakes Found**: None

**Behavioral Notes**:
- Text <= chunk_size returns single-element list
- Overlap only applied between chunks, not after last chunk
- Example: 1500 char text with chunk_size=500, overlap=100 → 3 chunks:
  - [0:500], [400:900], [800:1500]

**Test Cases**:
| Input | chunk_size | overlap | Output |
|-------|------------|---------|--------|
| "abc" | 500 | 100 | ["abc"] |
| "a"*1500 | 500 | 100 | 3 chunks overlapping |

**Reusability**: HIGH - Essential for LLM context window management

---

### chunk_list

**Purpose**: Split a list into chunks

**Signature**:
```python
def chunk_list(items: List[T], chunk_size: int) -> List[List[T]]
```

**Lines**: 35-45

**Complexity**: O(n) where n is length of items list

**Key Code**:
```python
def chunk_list(items: List[T], chunk_size: int) -> List[List[T]]:
    """Split a list into chunks.

    Args:
        items: List to chunk
        chunk_size: Items per chunk

    Returns:
        List of item chunks
    """
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]
```

**What Works**:
- ✅ Generic type variable T
- ✅ List comprehension (efficient)
- ✅ No overlap (unlike chunk_text)

**Mistakes Found**: None

**Behavioral Notes**:
- Non-overlapping chunks
- Last chunk may be smaller than chunk_size
- Example: [1,2,3,4,5] with chunk_size=2 → [[1,2], [3,4], [5]]

**Reusability**: HIGH - Generic list chunking

---

### deduplicate_items

**Purpose**: Remove duplicate items from a list

**Signature**:
```python
def deduplicate_items(
    items: List[str], normalize: bool = True, min_length: int = 10
) -> List[str]
```

**Lines**: 48-70

**Complexity**: O(n) where n is length of items list

**Key Code**:
```python
def deduplicate_items(
    items: List[str], normalize: bool = True, min_length: int = 10
) -> List[str]:
    """Remove duplicate items from a list.

    Args:
        items: List of items to deduplicate
        normalize: Whether to normalize (lowercase, strip) before comparison
        min_length: Minimum item length to keep

    Returns:
        Unique items
    """
    seen = set()
    unique = []
    for item in items:
        if not item or len(item) < min_length:
            continue
        key = item.lower().strip() if normalize else item
        if key and key not in seen:
            seen.add(key)
            unique.append(item)
    return unique
```

**What Works**:
- ✅ Preserves order (first occurrence kept)
- ✅ Normalization option (case-insensitive dedup)
- ✅ Minimum length filter
- ✅ Empty string filtering
- ✅ Set-based O(1) lookup

**Mistakes Found**:
- ⚠️ Only works for strings (not generic despite being in chunking module)
- ⚠️ Type hint shows `List[str]` but could be more generic

**Behavioral Notes**:
- Normalization: lowercase + strip before comparison
- Original item returned (not normalized version)
- Example: ["Apple", "apple", "BANANA"] → ["Apple", "BANANA"]

**Reusability**: HIGH - Useful for LLM output cleaning

---

### iterative_refine

**Purpose**: Run processor iteratively, feeding results back in

**Signature**:
```python
def iterative_refine(
    items: List[T],
    processor: Callable[[List[T], List[T]], List[T]],
    iterations: int = 3,
) -> List[T]
```

**Lines**: 73-95

**Complexity**: O(i * n) where i is iterations, n is processor complexity

**Key Code**:
```python
def iterative_refine(
    items: List[T],
    processor: Callable[[List[T], List[T]], List[T]],
    iterations: int = 3,
) -> List[T]:
    """Run processor iteratively, feeding results back in.

    Args:
        items: Initial items
        processor: Function that takes (current_items, previous_items) and returns new_items
        iterations: Number of iterations to run

    Returns:
        Refined items after all iterations
    """
    current = items
    previous: List[T] = []

    for i in range(iterations):
        current = processor(current, previous)
        previous = current

    return current
```

**What Works**:
- ✅ Generic type variable T
- ✅ Callable-based processor (flexible)
- ✅ Default iterations = 3
- ✅ Previous items passed to processor

**Mistakes Found**:
- ⚠️ Docstring mentions `processor(current, previous)` but signature shows `processor` takes two params - this is inconsistent
- ⚠️ `previous` set to `current` after each iteration (not tracking full history)

**Behavioral Notes**:
- Each iteration: current = processor(current, previous)
- Previous becomes what current was before processing
- Example for chunking+iteration pattern:
  - Iteration 1: processor([chunk1, chunk2, chunk3], [])
  - Iteration 2: processor(results, [chunk1, chunk2, chunk3])
  - Iteration 3: processor(results2, results)

**Reusability**: HIGH - Pattern used in InsightExtractorModule

**Related to**: `services/tools/analyst/insight_extractor.py` (uses this pattern)

---

## File Summary

**Total Functions**: 4
**Total Classes**: 0
**Lines of Code**: 96

**Violations**: None

**Success Patterns**:
- ✅ Text chunking with overlap (`chunk_text`)
- ✅ List chunking (`chunk_list`)
- ✅ Deduplication with normalization (`deduplicate_items`)
- ✅ Iterative refinement pattern (`iterative_refine`)
- ✅ Generic type variables for reusability
- ✅ Sensible defaults (500 char chunks, 100 char overlap, 3 iterations)

**Overall Assessment**: EXCELLENT - Core infrastructure for processing large LLM inputs.

**Key Learnings for Real AgentX**:
1. ✅ **Chunking is Essential**: LLMs have context limits - must chunk large inputs
2. ✅ **Overlap Prevents Splitting**: 100 char overlap prevents content boundaries from being split
3. ✅ **Default Parameters**: chunk_size=500, overlap=100 tuned for qwen3:8b (4K context)
4. ✅ **Iterative Refinement**: 3 iterations balances quality and latency
5. ✅ **Deduplication**: Normalization prevents case/whitespace duplicates

**Reuse for Real AgentX**: ✅ REQUIRED - All 4 functions are core infrastructure.

**Parameters for Different Models**:
| Model | Context | chunk_size | overlap | iterations |
|-------|---------|------------|---------|------------|
| qwen3:8b | ~4K | 500 | 100 | 3 |
| gemma3:4b | ~8K | 1000 | 200 | 2-3 |
| GPT-4 | ~32K | 4000 | 500 | 1-2 |

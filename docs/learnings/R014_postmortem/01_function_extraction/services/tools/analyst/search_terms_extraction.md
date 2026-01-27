# Function Extraction: services/tools/analyst/search_terms.py

## File Overview
**Path**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/tools/analyst/search_terms.py`
**Purpose**: Extract short search phrases for traditional search engines (SearXNG)
**Lines**: 78

---

## Classes and Functions

### `ExtractSearchTerms` (DSPy Signature)

**Purpose**: DSPy Signature for extracting specific search terms with temporal and domain qualifiers.

**Signature**:
```python
class ExtractSearchTerms(dspy.Signature):
    query: str = dspy.InputField(desc="User's original question")
    domain: str = dspy.InputField(desc="Subject area (economics, technology, etc.)")
    insights: str = dspy.InputField(desc="Context from query analysis")
    search_terms: str = dspy.OutputField(
        desc="3-5 specific search phrases with temporal/domain qualifiers, comma-separated"
    )
```

**Lines**: 10-33

**What Works**:
- Comprehensive docstring with examples
- Clear input/output field descriptions
- Temporal and domain qualifiers specified

**Reusability**: High - Generic search term extraction signature

---

### `SearchTermExtractorModule` (DSPy Module)

**Purpose**: Extracts short search terms for SearXNG from natural language queries using multiple iterations.

**Signature**:
```python
class SearchTermExtractorModule(dspy.Module):
    def __init__(self, num_iterations: int = 3):
        super().__init__()
        self.extractor = dspy.ChainOfThought(ExtractSearchTerms)
        self.num_iterations = num_iterations

    def forward(self, query: str, insights: list, domain: str = "general") -> dict:
```

**Lines**: 36-77

**Key Code Snippet**:
```python
def forward(self, query: str, insights: list, domain: str = "general") -> dict:
    all_terms = set()

    for i in range(self.num_iterations):
        result = self.extractor(
            query=query,
            domain=domain,
            insights=str(insights),
        )

        raw_terms = result.search_terms if hasattr(result, "search_terms") else ""

        if "," in raw_terms:
            terms = [t.strip() for t in raw_terms.split(",")]
        else:
            terms = [t.strip() for t in raw_terms.split("\n") if t.strip()]

        for t in terms:
            t_clean = t.lower().strip()
            if 2 <= len(t_clean.split()) <= 5:
                all_terms.add(t_clean)

    valid_terms = list(all_terms)

    if not valid_terms:
        words = query.split()[:5]
        valid_terms = [" ".join(words).lower()]

    return {"search_terms": valid_terms, "domain": domain}
```

**What Works (Success Patterns)**:
1. **Multiple iterations**: Runs extraction 3 times for diverse terms
2. **Set-based deduplication**: Uses `set()` to automatically remove duplicates
3. **Flexible parsing**: Handles both comma-separated and newline-separated terms
4. **Length validation**: Filters terms to 2-5 words for quality
5. **Fallback mechanism**: Uses first 5 words of query if extraction fails

**Mistakes Found**:
None - robust multi-iteration extraction

**Behavioral Notes**:
- Extracts 3-5 specific search phrases per iteration
- Includes temporal qualifiers (years, ranges)
- Includes domain-specific keywords
- Deduplicates across iterations

**Dependencies**:
- `dspy.ChainOfThought` - Chain-of-thought reasoning
- `dspy.Signature` - Base signature class

**Reusability**: High - Generic search term extraction for any query

---

## Key Patterns

1. **Multi-Iteration Extraction Pattern**:
```python
all_terms = set()
for i in range(self.num_iterations):
    result = self.extractor(...)
    # Parse and add to set
```

2. **Flexible Term Parsing Pattern**:
```python
if "," in raw_terms:
    terms = [t.strip() for t in raw_terms.split(",")]
else:
    terms = [t.strip() for t in raw_terms.split("\n") if t.strip()]
```

3. **Length Validation Pattern**:
```python
if 2 <= len(t_clean.split()) <= 5:
    all_terms.add(t_clean)
```

4. **Fallback Pattern**:
```python
if not valid_terms:
    words = query.split()[:5]
    valid_terms = [" ".join(words).lower()]
```

---

## Lessons Learned

1. **Multiple iterations improve diversity**: Running extraction 3x gives more varied search terms
2. **Set-based deduplication**: Automatically removes duplicates without manual checking
3. **Flexible parsing**: Handle both comma and newline separators for robustness
4. **Length filtering**: 2-5 word terms are optimal for search engines
5. **Always have a fallback**: If LLM extraction fails, fall back to query words

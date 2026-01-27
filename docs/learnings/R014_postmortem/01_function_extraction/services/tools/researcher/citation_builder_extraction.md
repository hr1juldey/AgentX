# Function Postmortem: services/tools/researcher/citation_builder.py

## Metadata
- **File**: services/tools/researcher/citation_builder.py
- **Lines of Code**: 108
- **Purpose**: Builds citations from search results using position prediction
- **Dependencies**: dspy, re

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE - CITATION PLACEMENT

**Purpose**: Intelligently places citations in writing by finding best-matching sentences using relevance scoring.

---

## Classes Extracted

### FindBestCitationSpot (Signature)

**Purpose**: DSPy Signature for finding the best sentence to place a citation link.

**Lines**: 11-21

**Key Code**:
```python
class FindBestCitationSpot(dspy.Signature):
    """Find best sentence to place citation link."""

    sentence: str = dspy.InputField(desc="Sentence to evaluate")
    source_info: str = dspy.InputField(desc="Source: Title | URL")
    relevance_score: str = dspy.OutputField(
        desc="Relevance score 0.0 to 1.0 for how well this sentence matches the source. "
        "0.0 = no relation, 1.0 = directly uses facts from source."
    )
    rationale: str = dspy.OutputField(desc="Brief explanation of relevance")
```

**What Works**:
- ✅ Clear numeric range (0.0 to 1.0)
- ✅ Descriptive output fields
- ✅ Rationale provides interpretability

**Mistakes Found**: None - good signature design

**Behavioral Notes**:
- LLM outputs relevance score as string (needs parsing)
- Returns rationale for debugging

**Dependencies**:
- **Uses**: dspy.Signature, dspy.InputField, dspy.OutputField

**Reusability**: HIGH - Good pattern for any similarity scoring task

### CitationBuilderModule

**Purpose**: DSPy Module that builds citations by finding best insertion spots using relevance prediction.

**Lines**: 23-108

**Key Code**:
```python
class CitationBuilderModule(dspy.Module):
    """Builds citations by finding best insertion spots in writing."""

    RELEVANCE_THRESHOLD = 0.5

    def __init__(self):
        super().__init__()
        self.spot_finder = dspy.ChainOfThought(FindBestCitationSpot)

    def _parse_relevance_score(self, score_str: str) -> float:
        """Parse relevance score from LLM output with fallback."""
        if not score_str:
            return 0.0

        # Try to extract a number
        match = re.search(r"0?\.\d+|1\.0|0|1", score_str)
        if match:
            try:
                return float(match.group())
            except (ValueError, IndexError):
                pass

        # Fallback: check for positive keywords
        positive = ["high", "relevant", "direct", "strong", "yes"]
        if any(word in score_str.lower() for word in positive):
            return 0.7

        return 0.0

    def forward(self, raw_data: list, writing: str = "") -> list:
        """Build citations from raw search results.

        Args:
            raw_data: List of search results with title/url/snippet
            writing: Existing writing to place citations in

        Returns:
            List of citation dicts
        """
        citations = []

        # If no writing, return basic citations
        if not writing:
            for index, item in enumerate(raw_data[:5]):
                citations.append(
                    {
                        "cited_text": item.get("content", "")[:200],
                        "document_index": index,
                        "document_title": item.get("title", ""),
                        "url": item.get("url", ""),
                    }
                )
            return citations

        # Find best spots for each source
        sentences = writing.split(". ")

        for index, source in enumerate(raw_data[:5]):
            source_info = f"{source.get('title', '')} | {source.get('url', '')}"

            best_sentence = None
            best_score = 0.0

            # Check each sentence (limit to 10 for efficiency)
            for sentence in sentences[:10]:
                result = self.spot_finder(sentence=sentence, source_info=source_info)

                # Parse relevance score with proper fallback
                score = self._parse_relevance_score(result.relevance_score)

                if score > self.RELEVANCE_THRESHOLD and score > best_score:
                    best_score = score
                    best_sentence = sentence

            if best_sentence:
                citations.append(
                    {
                        "cited_text": best_sentence[:200],
                        "document_index": index,
                        "document_title": source.get("title", ""),
                        "url": source.get("url", ""),
                    }
                )

        return citations
```

**What Works**:
- ✅ Regex-based score parsing with multiple patterns (0.5, .5, 1.0, 0, 1)
- ✅ Keyword-based fallback for non-numeric scores
- ✅ Dual threshold check (RELEVANCE_THRESHOLD and best_score)
- ✅ Efficiency limit (10 sentences max per source)
- ✅ Graceful degradation (basic citations if no writing)
- ✅ Uses ChainOfThought for better reasoning

**Mistakes Found**:
- ⚠️ Keyword fallback (0.7) might not be appropriate threshold
- ⚠️ Sentence split (". ") might fail on abbreviations ("Dr.", "Mr.", "etc.")
- ⚠️ No handling for duplicate best sentences

**Behavioral Notes**:
- If no writing provided, returns basic citations (first 5 sources)
- Splits writing into sentences by ". " (period + space)
- Scores each sentence against each source
- Only cites sources with scores above threshold (0.5)
- Tracks best_score to avoid duplicates
- Limits cited_text to 200 characters

**Dependencies**:
- **Imports**: dspy, re
- **Uses**: dspy.ChainOfThought(), re.search(), str.split(), enumerate()

**Reusability**: HIGH - Pattern applies to any placement/relevance task

---

## File Summary

**Total Classes**: 2 (1 module + 1 signature)
**Lines of Code**: 108

**Overall Assessment**: EXCELLENT citation placement implementation. The regex-based score parsing with keyword fallback is robust. The dual threshold check (both absolute threshold and relative best) prevents false positives.

**Key Learnings for Real AgentX**:
1. ✅ Use regex with multiple patterns for numeric parsing: `r"0?\.\d+|1\.0|0|1"`
2. ✅ Provide keyword-based fallback for non-numeric LLM outputs
3. ✅ Use dual threshold: absolute (RELEVANCE_THRESHOLD) and relative (best_score)
4. ✅ Limit search space for efficiency (10 sentences max)
5. ✅ Provide graceful degradation (basic citations if no writing)
6. ✅ Use ChainOfThought for reasoning tasks (need rationale)
7. ⚠️ Use better sentence splitting (nltk, spaCy) not just ". "
8. ⚠️ Make keyword fallback score configurable per use case

**Reuse for Real AgentX**: ✅ DIRECT - Use this pattern for any placement/relevance scoring task (not just citations)

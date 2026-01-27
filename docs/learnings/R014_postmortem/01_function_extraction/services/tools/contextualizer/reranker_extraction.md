# Function Extraction: services/tools/contextualizer/reranker.py

## File Overview
**Path**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/tools/contextualizer/reranker.py`
**Purpose**: Reranks search results by relevance
**Lines**: 87

---

## Classes and Functions

### `RerankerModule` (DSPy Module)

**Purpose**: Reranks search results by relevance with both sync and async execution.

**Signature**:
```python
class RerankerModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.score_relevance = dspy.Predict(ScoreRelevanceSignature)
        self.rank_by_quality = dspy.Predict("query, results -> ranked_results")

    def forward(self, query: str, results: list) -> dict:
    async def aforward(self, query: str, results: list) -> dict:
```

**Lines**: 20-86

**Key Code Snippet (Sync)**:
```python
def forward(self, query: str, results: list) -> dict:
    """Rerank results by relevance."""
    # Score each result
    scored_results = []
    for result in results:
        score_result = self.score_relevance(query=query, result=str(result))
        if hasattr(score_result, "relevance_score"):
            result_copy = result.copy() if isinstance(result, dict) else result
            score = _to_float(score_result.relevance_score)
            scored_results.append({"data": result_copy, "score": score})

    # Sort by score
    scored_results.sort(key=lambda x: x["score"], reverse=True)

    # Rank by quality
    ranked_result = self.rank_by_quality(query=query, results=str(scored_results))

    return {
        "ranked_data": [r["data"] for r in scored_results],
        "scores": [r["score"] for r in scored_results],
        "ranked_results": ranked_result.ranked_results
        if hasattr(ranked_result, "ranked_results")
        else scored_results,
    }
```

**What Works**:
1. **Two-stage ranking**: Individual scoring + global quality ranking
2. **Numeric sorting**: Sorts by float score for precise ordering
3. **Multiple outputs**: Returns ranked_data, scores, and ranked_results
4. **Safe type conversion**: _to_float() for LLM output robustness

**Mistakes Found**:
None - clean reranking implementation

**Behavioral Notes**:
- Scores each result individually
- Sorts by score (descending)
- Applies global quality ranking
- Returns both data and scores separately

**Dependencies**:
- `services.tools.contextualizer.signatures` - ScoreRelevanceSignature
- `services.tools.common.type_utils` - _to_float
- `services.tools.contextualizer.async_executor` - execute_parallel

**Reusability**: High - Generic reranking for any query/results pair

---

## Key Patterns

1. **Two-Stage Ranking Pattern**:
```python
# Stage 1: Score individually
scored_results = []
for result in results:
    score = self.score_relevance(query=query, result=str(result))
    scored_results.append({"data": result, "score": score})

# Stage 2: Sort globally
scored_results.sort(key=lambda x: x["score"], reverse=True)

# Stage 3: Quality ranking
ranked_result = self.rank_by_quality(query=query, results=str(scored_results))
```

2. **Descending Sort Pattern**:
```python
scored_results.sort(key=lambda x: x["score"], reverse=True)
```

3. **Multi-Output Pattern**:
```python
return {
    "ranked_data": [r["data"] for r in scored_results],
    "scores": [r["score"] for r in scored_results],
    "ranked_results": ranked_result.ranked_results,
}
```

---

## Lessons Learned

1. **Two-stage ranking works better**: Individual scores + global ranking > individual scores alone
2. **Return scores separately**: Downstream code may need raw scores for thresholding
3. **Sort descending**: Highest scores first (reverse=True)
4. **Use float for precision**: Numeric scores allow precise sorting

# Spec: Search Term Pattern Memory

**Domain**: search_term_pattern_memory
**Generated**: 2026-02-03
**Status**: Draft

---

## 1. Purpose

Learn from past successful search terms and predict terms for new queries. For topic A, terms X,Y,Z worked; for topic B, what terms will work?

**Problem Statement**: SearchTermExtractorModule (R014) extracts terms via multi-iteration DSPy, but doesn't learn from past successes. Each search is independent, missing opportunity for term pattern learning.

**Success Criteria**: System learns which search terms work well for each topic type and predicts terms for new queries.

---

## 2. Scope

### In Scope

- SearchTermPatternMemory entity tracking: query, search_terms_used, result_quality_score, timestamp, topic_type
- Pattern extraction: "For [topic_type], terms [X,Y,Z] work well"
- Term prediction for new queries based on similarity
- Integration with SearchTermExtractorModule (from R014 - already ported)
- Quality feedback: Record which terms produced good results

### Out of Scope

- SearchTermExtractorModule itself (PRESERVE existing R014 mechanism)
- SearXNG search execution (handled by existing search_executor.py)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-TERM-001 | SearchTermPatternMemory tracks: original_query, search_terms_used, result_quality_score, timestamp, topic_type | Must |
| FR-TERM-002 | Pattern extraction: Group successful searches by topic_type, extract common term patterns | Must |
| FR-TERM-003 | Term prediction: For new query, retrieve similar topic patterns, suggest terms | Must |
| FR-TERM-004 | Quality feedback: Record which terms produced good results (>0.7 quality) | Must |
| FR-TERM-005 | Term diversity: Encourage varied term selection (avoid term repetition) | Should |
| FR-TERM-006 | Integration with SearchTermExtractorModule (R014) | Must |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-TERM-001 | All files pass Ruff and Pyrefly | Must |
| NFR-TERM-002 | Absolute imports only | Must |

---

## 4. Data Model

```python
# agentx/domain/entities/search_term_pattern.py
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from enum import Enum

class TopicType(str, Enum):
    """High-level topic categories for pattern learning."""
    HEALTH = "health"
    FINANCE = "finance"
    TECHNOLOGY = "technology"
    SCIENCE = "science"
    TRAVEL = "travel"
    GENERAL = "general"

@dataclass
class SearchTermPattern:
    """Pattern of successful search terms for a topic type."""
    pattern_id: UUID
    user_id: str
    topic_type: TopicType
    search_terms: list[str]  # Terms that worked well
    success_count: int  # How many times this pattern succeeded
    fail_count: int  # How many times this pattern failed
    avg_quality_score: float  # Average quality when used
    last_used_at: datetime
    created_at: datetime

    def success_rate(self) -> float:
        """Calculate success rate for this pattern."""
        total = self.success_count + self.fail_count
        if total == 0:
            return 0.5  # Neutral for new patterns
        return self.success_count / total

    def is_reliable(self) -> bool:
        """Check if pattern is reliable enough for reuse."""
        return (self.success_count >= 3 and
                self.success_rate() >= 0.6 and
                self.avg_quality_score >= 0.7)

@dataclass
class SearchTermRecord:
    """Record of a search execution with terms used and results."""
    record_id: UUID
    user_id: str
    original_query: str
    search_terms_used: list[str]
    result_quality_score: float
    topic_type: TopicType
    pattern_id: UUID | None  # Which pattern was used (if any)
    timestamp: datetime
```

---

## 5. API Contract

This spec defines domain entities and service. No REST/WebSocket endpoints.

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-TERM-001 | Only record patterns for quality >= 0.7 | SearchTermPatternService |
| BR-TERM-002 | Term diversity: Don't repeat exact same terms | SearchTermPatternService |
| BR-TERM-003 | Pattern must be used 3+ times before considered reliable | is_reliable() |
| BR-TERM-004 | For new query, retrieve patterns from similar topic_type | SearchTermPatternService |

---

## 7. Acceptance Criteria

- [ ] SearchTermPattern entity exists with required fields
- [ ] SearchTermRecord entity exists for tracking executions
- [ ] SearchTermPatternService extracts patterns from successful searches
- [ ] SearchTermPatternService predicts terms for new queries
- [ ] Pattern extraction logic: "For health queries about [fruit], terms [X, Y, Z] work"
- [ ] Term prediction: "For new topic, try these terms based on similar past topics"
- [ ] Integration with SearchTermExtractorModule (R014)
- [ ] Quality feedback loop: Successful terms reinforce pattern
- [ ] All files pass: `ruff check` and `pyrefly check`

**Verification**:
```python
from agentx.application.services.search_term_pattern_service import SearchTermPatternService

service = SearchTermPatternService()

# Record a successful search
await service.record_search(
    query="blueberries health benefits",
    search_terms=["blueberries antioxidants", "blueberry nutrition facts"],
    quality_score=0.85,
    topic_type=TopicType.HEALTH
)

# Predict terms for similar query
predicted = await service.predict_terms("raspberries health benefits")
print(f"Predicted terms: {predicted}")
# Should suggest terms based on successful blueberry pattern
```

---

## 8. References

- **R014 SearchTermExtractorModule**: `prototypes/R014_ui_showcase/backend/services/tools/analyst/search_terms.py`
- **agentx port**: `agentx/agent/tools/analyst/search_terms.py` (already ported)
- **Related Specs**: `specs/memory_guided_search/spec.md`, `specs/searxng_hybrid_search/spec.md`

---

**Related Specs**:
- `specs/memory_guided_search/spec.md` - Uses search term patterns for guidance
- `specs/searxng_hybrid_search/spec.md` - Integrates with SearXNG search

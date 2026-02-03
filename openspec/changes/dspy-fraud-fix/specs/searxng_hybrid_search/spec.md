# Spec: SearXNG Hybrid Search

**Domain**: searxng_hybrid_search
**Generated**: 2026-02-03
**Status**: Draft

---

## 1. Purpose

Hybrid approach: RAG for stored facts + SearXNG for current/predictive info. Protect against RAG-only failures for current events, predictions, niche topics.

**Problem Statement**: RAG only covers stored knowledge. For current events, predictions, niche topics, need fresh web search via SearXNG.

**Success Criteria**: System decides when to use RAG vs SearXNG vs both, with search term pattern guidance.

---

## 2. Scope

### In Scope

- Hybrid RAG + SearXNG approach
- SearchTermExtractorModule (from R014 - already ported to agentx)
- Integration with SearchTermPatternMemory for term prediction
- Decision logic: when to use RAG vs SearXNG vs both
- Hybrid synthesis: combine RAG + SearXNG results

### Out of Scope

- SearchTermExtractorModule itself (PRESERVE existing R014 mechanism)
- SearXNG client implementation (PRESERVE existing search_executor.py)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| RF-HYBRID-001 | Decision logic: RAG vs SearXNG vs both based on query analysis | Must |
| RF-HYBRID-002 | Niche/Current Topic → SearXNG (fresh web data) | Must |
| RF-HYBRID-003 | Well-Established Topic → RAG (stored knowledge) | Must |
| RF-HYBRID-004 | Contradicting Info → SearXNG (verify current) | Must |
| RF-HYBRID-005 | Complex Query → Both (RAG + SearXNG synthesis) | Must |
| RF-HYBRID-006 | SearchTermPatternMemory integration for term prediction | Must |
| RF-HYBRID-007 | SearchTermExtractorModule preserved (R014) | Must |
| RF-HYBRID-008 | Hybrid synthesis: combine RAG + SearXNG results | Must |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-HYBRID-001 | All files pass Ruff and Pyrefly | Must |
| NFR-HYBRID-002 | Absolute imports only | Must |

---

## 4. Data Model

```python
# agentx/application/services/hybrid_search_service.py
from enum import Enum
from dataclasses import dataclass
from typing import Literal

class SearchStrategy(str, Enum):
    """Search strategy decision."""
    RAG_ONLY = "rag_only"           # Use stored knowledge only
    SEARXNG_ONLY = "searxng_only"   # Use web search only
    HYBRID = "hybrid"               # Use both and synthesize

class QueryCharacteristics(str, Enum):
    """Characteristics that influence search strategy."""
    CURRENT_EVENTS = "current_events"     # Recent news, time-sensitive
    PREDICTIONS = "predictions"         # Future forecasts, predictions
    WELL_ESTABLISHED = "well_established"  # Stable facts, history
    NICHE = "niche"                     # Obscure topics, limited data
    CONTRADICTING = "contradicting"     # Conflicting information detected

@dataclass
class HybridSearchDecision:
    """Decision for hybrid search strategy."""
    strategy: SearchStrategy
    characteristics: list[QueryCharacteristics]
    reasoning: str  # Why this strategy was chosen
    rag_weight: float = 1.0  # For HYBRID: weight for RAG results
    searxng_weight: float = 1.0  # For HYBRID: weight for SearXNG results

class HybridSearchService:
    """Service for hybrid RAG + SearXNG search decisions."""

    def __init__(self):
        from agentx.application.services.search_term_pattern_service import SearchTermPatternService
        from agentx.agent.tools.analyst.search_terms import SearchTermExtractorModule

        self.term_pattern_service = SearchTermPatternService()
        self.term_extractor = SearchTermExtractorModule(num_iterations=3)

    async def decide_strategy(
        self,
        query: str,
        user_id: str,
        memory_context: dict | None = None
    ) -> HybridSearchDecision:
        """Decide whether to use RAG, SearXNG, or both.

        Decision Logic:
        - Niche/Current Topic → SEARXNG_ONLY
        - Well-Established Topic → RAG_ONLY
        - Contradicting Info → SEARXNG_ONLY (verify current)
        - Complex Query → HYBRID
        """
        # Implementation follows decision logic
        pass

    async def get_search_terms(
        self,
        query: str,
        user_id: str,
        use_pattern_memory: bool = True
    ) -> list[str]:
        """Get search terms, optionally using pattern memory.

        Args:
            query: User's query
            user_id: User identifier
            use_pattern_memory: Whether to use past successful patterns

        Returns:
            List of search terms to use
        """
        if use_pattern_memory:
            # Try to get terms from past successful patterns
            predicted_terms = await self.term_pattern_service.predict_terms(query)
            if predicted_terms:
                return predicted_terms

        # Fall back to SearchTermExtractorModule (R014 mechanism)
        result = self.term_extractor(query=query, insights=[], domain="general")
        return result.get("search_terms", [])
```

---

## 5. API Contract

This spec defines service only. No REST/WebSocket endpoints.

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-HYBRID-001 | Current events (within 7 days) → SearXNG | QueryAnalysis |
| BR-HYBRID-002 | Predictions/forecasts → SearXNG (future data) | QueryAnalysis |
| BR-HYBRID-003 | Well-established facts (>1 year old) → RAG | QueryAnalysis |
| BR-HYBRID-004 | Contradicting memories → SearXNG (verify) | ConflictDetection |
| BR-HYBRID-005 | Complex queries (multiple topics) → HYBRID | QueryAnalysis |
| BR-HYBRID-006 | SearchTermPatternMemory guides term selection | TermPrediction |

---

## 7. Acceptance Criteria

- [ ] HybridSearchService exists with decide_strategy() method
- [ ] Decision logic exists: when to use RAG vs SearXNG vs both
- [ ] QueryCharacteristics enum exists: CURRENT_EVENTS, PREDICTIONS, WELL_ESTABLISHED, NICHE, CONTRADICTING
- [ ] SearchTermPatternMemory predicts terms based on past patterns
- [ ] SearchTermExtractorModule preserved (R014 mechanism)
- [ ] Hybrid synthesis combines RAG + SearXNG results
- [ ] All files pass: `ruff check` and `pyrefly check`

**Verification**:
```python
from agentx.application.services.hybrid_search_service import HybridSearchService

service = HybridSearchService()

# Test 1: Current event → SearXNG
decision1 = await service.decide_strategy("Who won the Super Bowl 2025?", user_id="test")
assert decision1.strategy == SearchStrategy.SEARXNG_ONLY
assert QueryCharacteristics.CURRENT_EVENTS in decision1.characteristics

# Test 2: Well-established fact → RAG
decision2 = await service.decide_strategy("What is the capital of France?", user_id="test")
assert decision2.strategy == SearchStrategy.RAG_ONLY
assert QueryCharacteristics.WELL_ESTABLISHED in decision2.characteristics

# Test 3: Complex query → HYBRID
decision3 = await service.decide_strategy("Compare blueberry vs raspberry nutrition for athletes", user_id="test")
assert decision3.strategy == SearchStrategy.HYBRID

# Test 4: Term pattern memory usage
terms = await service.get_search_terms("blueberry health benefits", user_id="test")
print(f"Predicted terms: {terms}")
# Should return terms based on successful past patterns (if any)
```

---

## 8. References

- **R014 SearchTermExtractorModule**: `prototypes/R014_ui_showcase/backend/services/tools/analyst/search_terms.py`
- **agentx port**: `agentx/agent/tools/analyst/search_terms.py` (already ported)
- **SearXNG integration**: `agentx/agent/tools/researcher/search_executor.py` (PRESERVE existing)

---

**Related Specs**:
- `specs/search_term_pattern_memory/spec.md` - Provides term prediction
- `specs/memory_guided_search/spec.md` - Uses term patterns for guidance

# Spec: Multi-Source Synthesis

**Domain**: multi_source_synthesis
**Generated**: 2026-02-03
**Status**: Draft

---

## 1. Purpose

Synthesize multiple research sources into unified answer. Combine assessed sources with consensus/conflict detection.

**Problem Statement**: No synthesis service for combining research results. Multiple sources not integrated.

**Success Criteria**: SynthesisService combines assessed sources; returns unified_answer, consensus_points, conflicts.

---

## 2. Scope

### In Scope

- SynthesisService for combining research sources
- MultiSourceSynthesisSignature
- Consensus points detection
- Conflicts detection
- JSON input handling for assessed sources

### Out of Scope

- Research execution (handled by existing nodes)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| RF-SYN-001 | SynthesisService exists in application/services/ | Must |
| RF-SYN-002 | MultiSourceSynthesisSignature exists in dspy_signatures/ | Must |
| RF-SYN-003 | synthesize() returns unified_answer, consensus_points, conflicts | Must |
| RF-SYN-004 | Uses dspy.ChainOfThought or Predict | Must |
| RF-SYN-005 | Handles JSON input of assessed sources | Must |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-SYN-001 | All files pass Ruff and Pyrefly | Must |
| NFR-SYN-002 | Absolute imports only | Must |

---

## 4. Data Model

```python
# agentx/agent/dspy_signatures/synthesis_signatures.py
import dspy

class MultiSourceSynthesisSignature(dspy.Signature):
    """Synthesize multiple research sources into unified answer."""
    query: str = dspy.InputField(desc="User's original question")
    sources: str = dspy.InputField(desc="JSON string of assessed research sources")
    unified_answer: str = dspy.OutputField(desc="One coherent answer")
    consensus_points: str = dspy.OutputField(desc="Key points agreed by sources")
    conflicts: str = dspy.OutputField(desc="Conflicting information")

# agentx/application/services/synthesis_service.py
import json
import dspy
from agentx.agent.dspy_signatures.synthesis_signatures import MultiSourceSynthesisSignature

class SynthesisService:
    """Service for synthesizing multiple research sources."""

    def __init__(self):
        self.synthesizer = dspy.ChainOfThought(MultiSourceSynthesisSignature)

    async def synthesize(self, query: str, assessed_sources: list[dict]) -> dict:
        """Synthesize multiple sources into unified answer."""
        # Format sources for DSPy
        sources_json = json.dumps([
            {
                "content": s.get("content", ""),
                "relevance": s.get("relevance_score", 0)
            }
            for s in assessed_sources
        ], indent=2)

        result = self.synthesizer(query=query, sources=sources_json)

        return {
            "unified_answer": result.unified_answer,
            "consensus_points": result.consensus_points,
            "conflicts": result.conflicts
        }
```

---

## 5. API Contract

This spec defines application service only. No REST/WebSocket endpoints.

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-SYN-001 | Sources formatted as JSON | SynthesisService |
| BR-SYN-002 | Consensus points are agreed by 2+ sources | DSPy LLM |
| BR-SYN-003 | Conflicts are disagreements between sources | DSPy LLM |

---

## 7. Acceptance Criteria

- [ ] SynthesisService exists in application/services/
- [ ] MultiSourceSynthesisSignature exists in dspy_signatures/
- [ ] synthesize() method returns dict with unified_answer, consensus_points, conflicts
- [ ] Uses dspy.ChainOfThought or Predict
- [ ] Handles JSON input of assessed sources
- [ ] All files pass: `ruff check` and `pyrefly check`

---

## 8. References

- **Plan**: `.claude/plans/golden-skipping-hedgehog.md` (Batch 4)
- **DSPy Docs**: `/home/riju279/Downloads/dspy-main/dspy-main/docs/`

---

**Related Specs**:
- `specs/real_rag/spec.md` - Provides retrieved sources

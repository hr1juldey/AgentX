# Spec: Context Rotting Prevention

**Domain**: context_rotting
**Generated**: 2026-02-03
**Status**: Draft

---

## 1. Purpose

Prevent context rotting using TTL + supersede + decay + reinforcement mechanisms.

**Problem Statement**: Memories never expire, never decay, and never get superseded by better information, leading to "rotting" context.

**Success Criteria**: ContextRotManager checks TTL, applies decay, handles supersede; ReinforcementTracker logs retrieval outcomes for TTL adjustment.

---

## 2. Scope

### In Scope

- ContextRotManager for TTL, decay, supersede
- ReinforcementTracker for logging retrieval outcomes
- TTL extension on good retrieval
- TTL shortening on bad retrieval
- Configurable base_ttl_days, ttl_extension_days, ttl_shorten_days

### Out of Scope

- Memory storage logic (separate concern)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| RF-ROT-001 | ContextRotManager checks TTL and enforces expiration | Must |
| RF-ROT-002 | ContextRotManager applies quality decay over time | Must |
| RF-ROT-003 | ContextRotManager handles supersede (better memory replaces older) | Must |
| RF-ROT-004 | ReinforcementTracker logs retrieval outcomes | Must |
| RF-ROT-005 | Good retrievals extend TTL, bad retrievals shorten TTL | Must |
| RF-ROT-006 | Configurable TTL parameters | Must |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-ROT-001 | All files pass Ruff and Pyrefly | Must |
| NFR-ROT-002 | Absolute imports only | Must |

---

## 4. Data Model

```python
# agentx/infrastructure/memory/context_rot_manager.py
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class ContextRotManager:
    """Manages memory TTL, decay, and supersede mechanisms."""
    base_ttl_days: int = 30
    ttl_extension_days: int = 7
    ttl_shorten_days: int = 14
    decay_rate_per_day: float = 0.01  # 1% quality loss per day

    def check_ttl(self, memory: MemoryRecord) -> bool:
        """Check if memory has expired."""
        return memory.is_expired()

    def apply_decay(self, memory: MemoryRecord) -> None:
        """Apply quality decay based on time since last access."""
        if memory.last_accessed_at:
            elapsed_days = (datetime.now() - memory.last_accessed_at).days
            decay_amount = elapsed_days * self.decay_rate_per_day
            memory.quality_score = max(0.0, memory.quality_score - decay_amount)

    def extend_ttl(self, memory: MemoryRecord) -> None:
        """Extend TTL after good retrieval."""
        memory.ttl_days += self.ttl_extension_days

    def shorten_ttl(self, memory: MemoryRecord) -> None:
        """Shorten TTL after bad retrieval."""
        memory.ttl_days = max(1, memory.ttl_days - self.ttl_shorten_days)

# agentx/infrastructure/memory/reinforcement_tracker.py
from dataclasses import dataclass
from typing import Dict
from uuid import UUID

@dataclass
class ReinforcementTracker:
    """Tracks retrieval outcomes for TTL adjustment."""
    _outcomes: Dict[UUID, list[bool]]  # memory_id -> list of success/failure

    def log_retrieval_outcome(self, memory_id: UUID, success: bool) -> None:
        """Log a retrieval outcome."""
        if memory_id not in self._outcomes:
            self._outcomes[memory_id] = []
        self._outcomes[memory_id].append(success)

    def get_success_rate(self, memory_id: UUID) -> float:
        """Calculate success rate for a memory."""
        if memory_id not in self._outcomes or not self._outcomes[memory_id]:
            return 0.5  # Neutral
        successes = sum(1 for s in self._outcomes[memory_id] if s)
        return successes / len(self._outcomes[memory_id])
```

---

## 5. API Contract

This spec defines infrastructure services only. No REST/WebSocket endpoints.

---

## 6. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-ROT-001 | TTL checked before retrieval | ContextRotManager.check_ttl() |
| BR-ROT-002 | Decay applied after each access | ContextRotManager.apply_decay() |
| BR-ROT-003 | Good retrieval (success_rate >= 0.7) extends TTL | ReinforcementTracker |
| BR-ROT-004 | Bad retrieval (success_rate < 0.4) shortens TTL | ReinforcementTracker |
| BR-ROT-005 | Supersede sets superseded_by field | MemoryRepository |

---

## 7. Acceptance Criteria

- [ ] ContextRotManager exists with check_ttl(), apply_decay(), extend_ttl(), shorten_ttl()
- [ ] ReinforcementTracker exists with log_retrieval_outcome(), get_success_rate()
- [ ] TTL is checked and enforced
- [ ] Quality decay is applied over time
- [ ] Supersede mechanism works (superseded_by field)
- [ ] Good retrievals extend TTL, bad retrievals shorten TTL
- [ ] All files pass: `ruff check` and `pyrefly check`

---

## 8. References

- **Plan**: `.claude/plans/golden-skipping-hedgehog.md` (Batch 0d)
- **Memory Entity**: `specs/work_experience_memory/spec.md`

---

**Related Specs**:
- `specs/work_experience_memory/spec.md` - MemoryRecord entity
- `specs/adaptive_retrieval/spec.md` - Quality-based retrieval

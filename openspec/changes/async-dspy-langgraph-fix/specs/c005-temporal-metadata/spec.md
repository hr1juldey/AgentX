# Spec: C005 Temporal Metadata

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Draft

---

## 1. Purpose

Define the C005 temporal metadata models for fact invalidation and time-based forgetting.

**Success Criteria**:
- TemporalMetadata model with C005 fields
- TemporalType enum with 6 types
- valid_from/valid_until for TTL
- supersedes/superseded_by for fact chaining

---

## 2. Scope

### In Scope

- TemporalMetadata Pydantic model
- TemporalType enum
- Fact invalidation logic
- TTL-based forgetting

### Out of Scope

- Memory storage implementation (covered by agent-memory-store spec)
- Consolidation logic (covered by mem0-consolidation spec)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-TM-001 | TemporalMetadata MUST have valid_from/valid_until | Must |
| FR-TM-002 | TemporalMetadata MUST have supersedes/superseded_by | Should |
| FR-TM-003 | TemporalType MUST include all 6 C005 types | Must |
| FR-TM-004 | Memory MUST check validity before retrieval | Must |

---

## 4. Data Model

```python
# domain/models/episodic_memory.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import list
from enum import Enum

class TemporalType(str, Enum):
    """Types of temporal memory (C005 aligned)."""

    # User preferences (long-lived)
    PREFERENCE = "preference"

    # User state (medium-lived)
    STATE = "state"

    # One-time events (short-lived)
    EVENT = "event"

    # Future plans (time-bound)
    PLAN = "plan"

    # Factual knowledge (valid until superseded)
    FACT = "fact"

    # Research results (medium-lived)
    RESEARCH = "research"

class TemporalMetadata(BaseModel):
    """C005 temporal metadata for memory management.

    Enables:
    - Time-based forgetting (TTL via valid_until)
    - Fact invalidation (supersedes chain)
    - Temporal queries (what did I know on date X?)
    """

    # Creation tracking
    created_at: datetime = Field(description="When this memory was created")
    modified_at: datetime = Field(description="When this memory was last modified")

    # Validity period (TTL)
    valid_from: datetime = Field(description="When this memory becomes valid")
    valid_until: datetime | None = Field(
        default=None,
        description="When this memory expires (None = indefinite)"
    )

    # Type categorization
    temporal_type: TemporalType = Field(description="Type of temporal memory")

    # Fact chaining (for invalidation)
    supersedes: list[str] = Field(
        default_factory=list,
        description="Memory IDs this memory supersedes (invalidates)"
    )
    superseded_by: str | None = Field(
        default=None,
        description="Memory ID that supersedes this memory"
    )

    def is_valid_at(self, timestamp: datetime) -> bool:
        """Check if memory is valid at given timestamp.

        Args:
            timestamp: Time to check validity at

        Returns:
            bool: True if memory is valid at timestamp
        """
        if timestamp < self.valid_from:
            return False
        if self.valid_until is not None and timestamp > self.valid_until:
            return False
        if self.superseded_by is not None:
            return False  # Superseded by newer memory
        return True

    def get_ttl_seconds(self) -> int | None:
        """Get time-to-live in seconds.

        Returns:
            int | None: Seconds until expiry, or None if no expiry
        """
        if self.valid_until is None:
            return None
        delta = self.valid_until - datetime.now()
        return max(0, int(delta.total_seconds()))
```

---

## 5. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-TM-001 | Preferences have long TTL | valid_until = created + 90 days |
| BR-TM-002 | Events have short TTL | valid_until = created + 7 days |
| BR-TM-003 | Facts have no TTL | valid_until = None |
| BR-TM-004 | Supersedes creates chain | Update superseded_by on old |

---

## 6. Usage Examples

```python
# Create research memory (30-day TTL)
research_meta = TemporalMetadata(
    created_at=datetime.now(),
    modified_at=datetime.now(),
    valid_from=datetime.now(),
    valid_until=datetime.now() + timedelta(days=30),
    temporal_type=TemporalType.RESEARCH,
    supersedes=[],
    superseded_by=None,
)

# Create preference (90-day TTL)
preference_meta = TemporalMetadata(
    created_at=datetime.now(),
    modified_at=datetime.now(),
    valid_from=datetime.now(),
    valid_until=datetime.now() + timedelta(days=90),
    temporal_type=TemporalType.PREFERENCE,
    supersedes=[],
    superseded_by=None,
)

# Create fact with invalidation
fact_meta_v1 = TemporalMetadata(
    created_at=datetime(2024, 1, 1),
    valid_from=datetime(2024, 1, 1),
    valid_until=None,  # No TTL
    temporal_type=TemporalType.FACT,
    supersedes=[],
    superseded_by="fact_456",  # Superseded by newer fact
)

# Check validity
now = datetime.now()
print(research_meta.is_valid_at(now))  # True if < 30 days old
print(fact_meta_v1.is_valid_at(now))  # False (superseded)
```

---

## 7. Acceptance Criteria

- [ ] TemporalMetadata model created
- [ ] TemporalType enum with 6 types
- [ ] is_valid_at() method works
- [ ] get_ttl_seconds() method works
- [ ] Supersede chain logic works
- [ ] Pyrefly type checking passes

---

## 8. Test Scenarios

| Scenario | Expected Result |
|----------|-----------------|
| Research < 30 days old | is_valid_at = True |
| Research > 30 days old | is_valid_at = False |
| Fact with superseded_by set | is_valid_at = False |
| Preference < 90 days old | is_valid_at = True |
| Event > 7 days old | is_valid_at = False |

---

**Next**: See `mem0-consolidation/spec.md` for consolidation logic.

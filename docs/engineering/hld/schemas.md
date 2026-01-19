# AGENTX Data Schemas

**Version**: 1.0.0
**Date**: 2026-01-19
**Status**: Draft
**Part of**: AGENTX HLD v1.0

---

## Overview

This document defines all Pydantic schemas used throughout AGENTX. These schemas ensure type safety, validation, and consistent data structures across the system.

**Note**: Follow CLAUDE_POLICY.md when implementing these schemas:
- Use absolute imports only
- Follow Ruff formatting and linting
- Keep files under 100 lines of executable code

---

## Table of Contents

1. [Canonical Document Models](#1-canonical-document-models)
2. [Plugin Models](#2-plugin-models)
3. [API Models](#3-api-models)
4. [Memory Models](#4-memory-models)
5. [Voice Models](#5-voice-models)

---

## 1. Canonical Document Models

### CanonicalDocument

The core data model for all information stored in AGENTX.

```python
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class ContentType(str, Enum):
    """Type of content in the document."""
    PREFERENCE = "preference"
    EVENT = "event"
    FACT = "fact"
    STATE = "state"
    PLAN = "plan"


class Source(str, Enum):
    """Origin of the data."""
    USER_INPUT = "user_input"
    PLUGIN_INGEST = "plugin_ingest"
    SYSTEM_INFERRED = "system_inferred"


class TTLPolicy(str, Enum):
    """Retention policy for the document."""
    DAYS_30 = "30d"
    DAYS_90 = "90d"
    DAYS_365 = "365d"
    FOREVER = "forever"


class RedactionMarker(BaseModel):
    """PII redaction marker."""

    type: str = Field(..., description="Type of PII (credit_card, ssn, email, etc.)")
    start_index: int = Field(..., ge=0, description="Start index in text")
    end_index: int = Field(..., gt=lambda self: self.start_index, description="End index in text")
    replacement: str = Field(default="[REDACTED]", description="Replacement text")
    reason: str = Field(..., description="Reason for redaction")


class CanonicalDocument(BaseModel):
    """Canonical document model for all AGENTX data.

    This is the single source of truth for all information stored in the system.
    All data from plugins, APIs, and user input is converted to this format.
    """

    # Identity
    id: UUID = Field(default_factory=uuid4)
    source_id: str = Field(..., description="Origin system identifier")
    user_id: str = Field(..., description="SHA-256 hash of user ID for isolation")

    # Content
    text: str = Field(..., min_length=1, max_length=2000)
    content_type: ContentType = Field(default=ContentType.FACT)

    # Temporal (REQUIRED)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: datetime = Field(default_factory=datetime.utcnow)
    valid_from: datetime = Field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = Field(None, description="Null = still valid")

    # Provenance
    source: Source = Field(default=Source.USER_INPUT)
    ingest_timestamp: datetime = Field(default_factory=datetime.utcnow)
    version_id: str = Field(default="1.0.0", description="Schema version")

    # Relationships
    supersedes: Optional[list[str]] = Field(None, description="IDs of outdated memories")
    related_events: Optional[list[str]] = Field(None, description="IDs of related memories")

    # Redaction
    redacted: bool = Field(default=False)
    redaction_markers: Optional[list[RedactionMarker]] = Field(None)

    # TTL
    ttl_policy: TTLPolicy = Field(default=TTLPolicy.DAYS_90)
    expires_at: Optional[datetime] = Field(None)

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate text content."""
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """Validate user ID is a hash."""
        if len(v) != 64:  # SHA-256 hex length
            raise ValueError("User ID must be SHA-256 hash (64 hex characters)")
        try:
            int(v, 16)
        except ValueError:
            raise ValueError("User ID must be hexadecimal string")
        return v
```

---

## 2. Plugin Models

### PluginManifest

Manifest that all plugins must provide.

```python
from typing import Literal
from pydantic import BaseModel, Field


class Permission(BaseModel):
    """Permission required by plugin."""

    resource: Literal["memory", "voice", "search", "mis", "filesystem"]
    operations: list[Literal["read", "write", "delete"]] = Field(min_items=1)
    scope: Literal["own", "shared", "all"]


class ResourceQuota(BaseModel):
    """Resource limits for plugin."""

    cpu_percent: float = Field(default=10.0, ge=0, le=100)
    ram_mb: int = Field(default=100, ge=16, le=1024)
    timeout_seconds: int = Field(default=60, ge=1, le=300)


class PluginManifest(BaseModel):
    """Plugin manifest describing capabilities and requirements."""

    name: str = Field(..., min_length=1, max_length=50)
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")  # semver
    type: Literal["automation", "extension", "experimental"]

    capabilities: list[str] = Field(default_factory=list)
    required_permissions: list[Permission] = Field(default_factory=list)
    resource_quotas: ResourceQuota = Field(default_factory=ResourceQuota)

    data_scope: Literal["none", "user_preferences", "user_data", "system"] = "none"
    retention_policy: Literal["none", "session", "30d", "90d", "forever"] = "none"

    health_check_endpoint: Optional[str] = Field(None, pattern=r"^/[a-z0-9/_-]+$")
    signature: str = Field(..., description="GPG signature of manifest")
```

### PluginStatus

Status information for installed plugins.

```python
from enum import Enum


class PluginState(str, Enum):
    """Plugin state."""
    INSTALLED = "installed"
    ACTIVATING = "activating"
    ACTIVE = "active"
    DEACTIVATING = "deactivating"
    CRASHED = "crashed"


class PluginHealth(str, Enum):
    """Plugin health status."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class PluginStatus(BaseModel):
    """Status of an installed plugin."""

    name: str
    version: str
    type: str
    state: PluginState
    health: PluginHealth = PluginHealth.UNKNOWN
    enabled: bool = False
    error_message: Optional[str] = None
```

---

## 3. API Models

### Authentication Models

```python
from datetime import datetime, timedelta


class LoginRequest(BaseModel):
    """Login request."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class LoginResponse(BaseModel):
    """Login response with JWT token."""

    access_token: str
    token_type: Literal["Bearer"]
    expires_in: int = Field(..., description="Seconds until expiration")
    issued_at: datetime = Field(default_factory=datetime.utcnow)


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: str = Field(..., description="User ID (SHA-256 hash)")
    exp: datetime = Field(..., description="Expiration time")
    iat: datetime = Field(..., description="Issued at")
    jti: str = Field(..., description="Token ID (UUID)")

    @classmethod
    def create(cls, user_id: str, expires_delta: timedelta = timedelta(hours=24)) -> "TokenPayload":
        """Create token payload."""
        now = datetime.utcnow()
        exp = now + expires_delta
        return cls(
            sub=user_id,
            exp=exp,
            iat=now,
            jti=str(uuid4()),
        )
```

### Error Models

```python
class ErrorCode(str, Enum):
    """Standard error codes."""

    VALIDATION = "validation"
    TIMEOUT = "timeout"
    QUOTA_EXCEEDED = "quota_exceeded"
    NOT_AUTHORIZED = "not_authorized"
    INTERNAL_ERROR = "internal_error"
    PLUGIN_ERROR = "plugin_error"


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    error_code: ErrorCode
    retryable: bool = False
    request_id: str = Field(default_factory=lambda: str(uuid4()))
```

---

## 4. Memory Models

### Memory Search Models

```python
class TimeWindow(str, Enum):
    """Predefined time windows for search."""

    RECENT_30D = "recent_30d"
    RECENT_90D = "recent_90d"
    ALL = "all"
    CUSTOM = "custom"


class FreshnessHint(str, Enum):
    """Freshness preference for search results."""

    PREFER_RECENT = "prefer_recent"
    PREFER_COMPREHENSIVE = "prefer_comprehensive"
    BALANCED = "balanced"


class MemorySearchRequest(BaseModel):
    """Memory search request with temporal filtering."""

    query: str = Field(..., min_length=1, max_length=512)
    time_window: TimeWindow = TimeWindow.ALL
    custom_start: Optional[datetime] = None
    custom_end: Optional[datetime] = None
    freshness_hint: FreshnessHint = FreshnessHint.BALANCED
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=50)

    @field_validator("custom_start", "custom_end")
    @classmethod
    def validate_custom_range(cls, start: Optional[datetime], end: Optional[datetime], info) -> None:
        """Validate custom time range."""
        if info.data.get("time_window") != TimeWindow.CUSTOM:
            if start is not None or end is not None:
                raise ValueError("custom_start and custom_end only valid with custom time_window")
        else:
            if start is None or end is None:
                raise ValueError("custom_start and custom_end required for custom time_window")
            if start >= end:
                raise ValueError("custom_start must be before custom_end")


class Confidence(str, Enum):
    """Retrieval confidence level."""

    HIGH = "high"  # score > 0.8 AND temporal_weight > 0.5
    MEDIUM = "medium"  # score > 0.6 AND temporal_weight > 0.3
    LOW = "low"  # score > 0.4


class SearchResultProvenance(BaseModel):
    """Provenance information for search result."""

    created_at: datetime
    source: Source
    version_id: str


class SearchResult(BaseModel):
    """Single search result."""

    id: UUID
    text: str
    score: float = Field(..., ge=0, le=1)
    provenance: SearchResultProvenance
    confidence: Confidence
    redacted: bool


class MemorySearchResponse(BaseModel):
    """Memory search response."""

    results: list[SearchResult]
    total_count: int
    retrieval_time_ms: int
```

### Memory Storage Models

```python
class MemoryAddRequest(BaseModel):
    """Request to add memory."""

    text: str = Field(..., min_length=1, max_length=2000)
    content_type: ContentType = ContentType.FACT
    source: Source = Source.USER_INPUT
    ttl_policy: TTLPolicy = TTLPolicy.DAYS_90


class MemoryAddResponse(BaseModel):
    """Response after adding memory."""

    id: UUID
    created_at: datetime
    indexed: bool
```

---

## 5. Voice Models

### Voice Session Models

```python
class VoiceSessionState(str, Enum):
    """Voice session state."""

    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    INTERRUPTED = "interrupted"


class VoiceSession(BaseModel):
    """Active voice session."""

    session_id: UUID
    user_id: str
    state: VoiceSessionState
    started_at: datetime
    last_activity: datetime
    turn_count: int = 0


class VoiceChunk(BaseModel):
    """Audio chunk for voice streaming."""

    type: Literal["chunk"] = "chunk"
    audio: bytes = Field(..., description="Opus-encoded audio (24kHz)")
    sample_rate: int = Field(default=24000)


class VoiceTranscription(BaseModel):
    """Transcription from STT."""

    type: Literal["transcription"] = "transcription"
    text: str
    is_final: bool = False
    confidence: float = Field(default=1.0, ge=0, le=1)
```

### Voice Configuration

```python
class VoiceConfig(BaseModel):
    """Voice interface configuration."""

    stt_model: Literal["stt-1b-en_fr", "stt-2.6b-en"] = "stt-1b-en_fr"
    tts_voice: str = Field(default="hf://kyutai/tts-voices/alba-mackenna/casual.wav")
    sample_rate: int = Field(default=24000, ge=16000, le=48000)
    chunk_size_ms: int = Field(default=100, ge=50, le=500)
    vad_sensitivity: float = Field(default=0.5, ge=0, le=1)


class VoiceMetrics(BaseModel):
    """Voice pipeline metrics."""

    vad_latency_ms: float
    stt_latency_ms: float
    llm_first_token_ms: float
    llm_total_ms: float
    tts_first_chunk_ms: float
    end_to_end_ms: float
```

---

## Appendix: Schema Validation

### Validation Rules

| Schema | Validation | Rules |
|--------|------------|-------|
| **CanonicalDocument** | Text | 1-2000 chars, non-empty |
| **CanonicalDocument** | User ID | SHA-256 hash (64 hex chars) |
| **PluginManifest** | Version | Semver pattern |
| **MemorySearchRequest** | Query | 1-512 chars |
| **MemorySearchRequest** | Custom range | start < end, only for custom window |

### Type Conversion

| Type | From | To |
|------|------|-----|
| **datetime** | ISO 8601 string | Python datetime |
| **UUID** | String hex | UUID object |
| **bytes** | Base64 string | Raw bytes |

---

**This schema document is part of AGENTX HLD v1.0. See [HLD.md](HLD.md) for complete architecture.**

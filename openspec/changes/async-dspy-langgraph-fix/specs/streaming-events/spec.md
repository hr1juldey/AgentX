# Spec: Streaming Events

**Domain**: agent-runtime
**Generated**: 2026-02-02
**Status**: Draft

---

## 1. Purpose

Define the streaming event models for real-time UI updates during long-running tasks.

**Success Criteria**:
- TokenEvent for token-by-token streaming
- ProgressEvent for progress updates
- CompleteEvent for completion notification
- BackgroundPromptEvent for 15s prompt

---

## 2. Scope

### In Scope

- Streaming event Pydantic models
- Event type definitions
- WebSocket event format

### Out of Scope

- Progress tracking logic (covered by progress-tracking spec)
- Skeleton screens (covered by skeleton-screens spec)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-SE-001 | TokenEvent MUST include token field | Must |
| FR-SE-002 | ProgressEvent MUST include progress percent | Must |
| FR-SE-003 | CompleteEvent MUST include final response | Should |
| FR-SE-004 | BackgroundPromptEvent MUST include prompt | Should |

---

## 4. Data Model

```python
# domain/models/streaming_events.py
from pydantic import BaseModel, Field
from enum import Enum

class StreamingEventType(str, Enum):
    """Types of streaming events."""
    TOKEN = "token"
    PROGRESS = "progress"
    STATUS = "status"
    COMPLETE = "complete"
    BACKGROUND_PROMPT = "background_prompt"
    WIDGET_REVEAL = "widget_reveal"

class TokenEvent(BaseModel):
    """Single token streaming event."""

    event_type: StreamingEventType = Field(default=StreamingEventType.TOKEN)
    token: str = Field(description="Single text token")
    is_first: bool = Field(default=False, description="First token of stream")
    index: int = Field(description="Token index in stream")

class ProgressEvent(BaseModel):
    """Progress update event."""

    event_type: StreamingEventType = Field(default=StreamingEventType.PROGRESS)
    progress: float = Field(ge=0.0, le=1.0, description="Progress (0.0-1.0)")
    message: str = Field(description="Human-readable progress message")
    current_step: str = Field(description="Current step name")
    total_steps: int = Field(description="Total steps")

class StatusEvent(BaseModel):
    """Status update event."""

    event_type: StreamingEventType = Field(default=StreamingEventType.STATUS)
    status: str = Field(description="Status message")
    level: str = Field(default="info", description="Log level")

class CompleteEvent(BaseModel):
    """Completion event."""

    event_type: StreamingEventType = Field(default=StreamingEventType.COMPLETE)
    final_response: str = Field(description="Complete response text")
    widget_count: int = Field(default=0, description="Number of widgets")
    duration_seconds: float = Field(description="Total duration")

class BackgroundPromptEvent(BaseModel):
    """Background prompt event (after 15s)."""

    event_type: StreamingEventType = Field(default=StreamingEventType.BACKGROUND_PROMPT)
    prompt: str = Field(description="Prompt message to user")
    allow_background: bool = Field(description="Allow running in background")

class WidgetRevealEvent(BaseModel):
    """Widget reveal event for progressive disclosure."""

    event_type: StreamingEventType = Field(default=StreamingEventType.WIDGET_REVEAL)
    widget: dict = Field(description="Widget specification")
    index: int = Field(description="Widget index")
    total: int = Field(description="Total widgets")

# Union type for all events
StreamingEvent = (
    TokenEvent | ProgressEvent | StatusEvent |
    CompleteEvent | BackgroundPromptEvent | WidgetRevealEvent
)
```

---

## 5. Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-SE-001 | is_first only on first token | Emitter logic |
| BR-SE-002 | progress always 0.0-1.0 | Pydantic constraint |
| BR-SE-003 | Background prompt at 15s | Timer logic |

---

## 6. Acceptance Criteria

- [ ] All event models created
- [ ] Event types defined in enum
- [ ] Pydantic constraints enforce ranges
- [ ] Union type works for type hints
- [ ] Pyrefly type checking passes

---

## 7. WebSocket Format

```python
# WebSocket message format
{
    "event_type": "token",
    "token": "Hello",
    "is_first": True,
    "index": 0
}

# Frontend handles
socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    switch (data.event_type) {
        case "token":
            // Append token to response
            break;
        case "progress":
            // Update progress bar
            break;
        case "complete":
            // Finalize response
            break;
    }
};
```

---

## 8. Test Scenarios

| Event | Expected Fields |
|-------|----------------|
| First token | is_first=True, index=0 |
| Progress | progress=0.5, message="Researching..." |
| Completion | final_response, duration_seconds |
| Background prompt | prompt="Continue in background?", allow_background=true |

---

**Next**: See `progress-tracking/spec.md` for progress tracking implementation.

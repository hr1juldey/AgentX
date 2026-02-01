# Spec: Transient UX for Long-Running Tasks

**Domain**: agent-runtime
**Generated**: 2026-02-01
**Status**: Draft

---

## 1. Purpose

Define the transient UX patterns that keep users engaged during long-running AI tasks (15+ seconds). Users abandon sessions when tasks take too long without feedback.

**Problem Statement**: Even if a task takes 15 minutes, humans won't wait and will leave. We need transient UX to keep them engaged and provide feedback during execution.

**Success Criteria**:
- Users stay engaged during 15-60s tasks
- Progress feedback appears within 300ms
- Streaming responses reduce perceived latency
- "Continue in background" option after 15s

---

## 2. Scope

### In Scope

- Streaming responses (token-by-token)
- Skeleton screens (progressive loading)
- Progressive disclosure (summary first, details on demand)
- "Continue in background?" prompt after 15s
- Determinate progress indicators for ≥10s waits
- Optimistic UI with undo

### Out of Scope

- Widget selection UI (see adaptive-widget-selection spec)
- Voice UI patterns (see C010 voice client)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| FR-UX-001 | Show skeleton within 300ms of user action | Must | Perceived speed |
| FR-UX-002 | Stream LLM responses token-by-token | Must | Reduce latency |
| FR-UX-003 | Progressive disclosure: summary first | Should | Prevent overwhelm |
| FR-UX-004 | "Continue in background?" after 15s | Should | Reduce abandonment |
| FR-UX-005 | Determinate progress for ≥10s tasks | Should | Feedback |
| FR-UX-006 | Optimistic UI with undo for actions | Optional | Responsiveness |
| FR-UX-007 | Graceful degradation when streaming unavailable | Must | Fallback |

### 3.2 Non-Functional Requirements

| ID | Requirement | Priority | Target Metric |
|----|-------------|----------|---------------|
| NFR-UX-001 | Time-to-first-token < 1s | Must | Fast startup |
| NFR-UX-005 | Skeleton appear < 300ms | Must | Immediate feedback |
| NFR-UX-006 | Progress update every 1-2s | Should | Regular updates |

---

## 4. Data Model

### 4.1 Streaming Events

```python
# domain/models/streaming_events.py
from pydantic import BaseModel, Field
from typing import Literal, Optional, Any
from enum import Enum

class StreamingEventType(str, Enum):
    """Types of streaming events."""
    TOKEN = "token"  # Single token from LLM
    CHUNK = "chunk"  # Larger chunk of content
    PROGRESS = "progress"  # Progress update
    STATUS = "status"  # Status message
    ERROR = "error"  # Error message
    COMPLETE = "complete"  # Task complete

class TokenEvent(BaseModel):
    """Single token from streaming LLM."""
    event_type: Literal["token"] = Field(default="token")
    token: str = Field(description="Single token from LLM")
    is_first: bool = Field(default=False, description="True for first token")
    index: int = Field(description="Token index in stream")

class ProgressEvent(BaseModel):
    """Progress update for long-running task."""
    event_type: Literal["progress"] = Field(default="progress")
    current: int = Field(description="Current progress value")
    total: int = Field(description="Total value (100% = total)")
    message: str = Field(description="Human-readable progress message")
    stage: str = Field(description="Current stage (e.g., 'researching', 'synthesizing')")
    timestamp: float = Field(description="Event timestamp (seconds since epoch)")

class StatusEvent(BaseModel):
    """Status message (not progress, just info)."""
    event_type: Literal["status"] = Field(default="status")
    message: str = Field(description="Status message")
    stage: str = Field(description="Current stage")
    metadata: dict[str, Any] = Field(default_factory=dict)

class CompleteEvent(BaseModel):
    """Task completion event."""
    event_type: Literal["complete"] = Field(default="complete")
    final_response: str = Field(description="Final response text")
    duration_ms: float = Field(description="Total duration in milliseconds")
    metadata: dict[str, Any] = Field(default_factory=dict)

class BackgroundPromptEvent(BaseModel):
    """Prompt user to continue in background."""
    event_type: Literal["background_prompt"] = Field(default="background_prompt")
    message: str = Field(description="Prompt message")
    estimated_remaining_seconds: float = Field(description="Estimated remaining time")
    allow_continue: bool = Field(default=True, description="True if user can continue in background")
```

### 4.2 Skeleton Screen Schema

```python
class SkeletonSchema(BaseModel):
    """Skeleton screen configuration."""
    structure: list[str] = Field(description="UI structure elements to show as skeletons")
    shimmer_enabled: bool = Field(default=True, description="Enable shimmer animation")
    shimmer_duration_ms: int = Field(default=1500, description="Shimmer animation duration")
    loading_text: str = Field(default="Loading...", description="Text to show during loading")

class ProgressiveDisclosureSchema(BaseModel):
    """Progressive disclosure configuration."""
    summary_first: bool = Field(default=True, description="Show summary before details")
    details_on_demand: bool = Field(default=True, description="Reveal details on request")
    expandable_sections: list[str] = Field(default_factory=list, description="Sections that can be expanded")
```

---

## 5. Architecture

### 5.1 Streaming Response Flow

```python
# agent/nodes/synthesizer.py
from typing import AsyncGenerator
import time

async def synthesizer_node(state: AgentState) -> AsyncGenerator[dict, None]:
    """Synthesize final response with streaming.

    This node streams tokens to the frontend as they're generated,
    reducing perceived latency.
    """

    # Gather research findings
    findings = state.get("research_findings", [])
    query = state["query"]

    # Generate response using DSPy with streaming
    from dspy import streamify

    # Wrap synthesizer with streaming
    stream_synthesizer = streamify(
        synthesizer_module,
        stream_listeners=[
            dspy.streaming.StreamListener(
                signature_field_name="response",
                allow_reuse=True
            )
        ]
    )

    # Stream tokens
    start_time = time.perf_counter()
    token_count = 0
    response_parts = []

    for i, chunk in enumerate(stream_synthesizer(query=query, findings=findings)):
        token_count += 1
        response_parts.append(chunk)

        # Emit token event
        yield {
            "streaming_event": TokenEvent(
                token=chunk,
                is_first=(i == 0),
                index=i,
            ),
        }

    # Emit completion event
    duration_ms = (time.perf_counter() - start_time) * 1000
    final_response = "".join(response_parts)

    yield {
        "streaming_event": CompleteEvent(
            final_response=final_response,
            duration_ms=duration_ms,
        ),
        "final_response": final_response,
    }
```

### 5.2 Progress Tracking During Execution

```python
# agent/nodes/progress_tracker.py
import asyncio
from datetime import datetime

class ProgressTracker:
    """Track and emit progress during long-running tasks."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.start_time = datetime.now()
        self.emitted_background_prompt = False

    async def track_progress(
        self,
        total_tasks: int,
        state: AgentState,
    ) -> AsyncGenerator[ProgressEvent, None]:
        """Track progress and emit events.

        Emits:
        - Progress events every 1-2 seconds
        - Background prompt after 15 seconds
        """

        visited = set(state.get("visited_tasks", []))
        total = total_tasks

        while len(visited) < total:
            # Check for timeout (15 seconds)
            elapsed = (datetime.now() - self.start_time).total_seconds()

            # Emit background prompt after 15s
            if elapsed > 15 and not self.emitted_background_prompt:
                yield BackgroundPromptEvent(
                    message="This task is taking longer than expected. Would you like to continue in the background?",
                    estimated_remaining_seconds=30,  # Estimate
                    allow_continue=True,
                )
                self.emitted_background_prompt = True

            # Emit progress update
            yield ProgressEvent(
                current=len(visited),
                total=total,
                message=f"Completed {len(visited)} of {total} research tasks...",
                stage="researching",
                timestamp=datetime.now().timestamp(),
            )

            # Wait before next update
            await asyncio.sleep(1.5)

            # Update visited from state
            visited = set(state.get("visited_tasks", []))

# In research worker node
async def research_worker_with_progress(
    state: AgentState,
    *,
    store: BaseStore,
):
    """Execute research with progress tracking."""

    tracker = ProgressTracker(state["session_id"])
    total_tasks = len(state["execution_plan"].research_tasks)

    # Start progress tracking in background
    async def emit_progress():
        async for event in tracker.track_progress(total_tasks, state):
            # Emit to frontend via WebSocket or SSE
            await emit_to_frontend(state["session_id"], event)

    progress_task = asyncio.create_task(emit_progress())

    # Execute research
    result = await execute_research(state)

    # Cancel progress tracking
    progress_task.cancel()

    return result

async def emit_to_frontend(session_id: str, event: BaseModel):
    """Emit event to frontend via WebSocket/SSE."""
    # Implementation depends on your transport:
    # - WebSocket: send JSON message
    # - SSE: send text/event-stream
    # - LangGraph: push_ui_message()
    pass
```

### 5.3 Skeleton Screen Configuration

```python
# presentation/api/v1/streaming.py
from fastapi import WebSocket
from langgraph.graph.ui import push_ui_message

@router.websocket("/ws/stream/{session_id}")
async def streaming_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for streaming events."""

    await websocket.accept()

    try:
        # Send initial skeleton immediately (< 300ms)
        await push_ui_message(
            "skeleton",
            {
                "structure": ["title", "summary", "findings_list", "details"],
                "shimmer_enabled": True,
                "loading_text": "Analyzing your query...",
            },
            message=None,
        )

        # Process query (this will take time)
        result = await process_query(session_id, websocket)

        # Send final result
        await push_ui_message(
            "card",
            {
                "title": "Complete",
                "content": result["final_response"],
                "metadata": {"variant": "success"},
            },
            message=None,
        )

    except Exception as e:
        await push_ui_message(
            "error",
            {
                "title": "Error",
                "content": str(e),
                "metadata": {"variant": "error"},
            },
            message=None,
        )

async def process_query(session_id: str, websocket: WebSocket) -> dict:
    """Process query with streaming updates."""

    # Emit initial status
    await websocket.send_json({
        "event_type": "status",
        "message": "Planning research...",
        "stage": "planning",
    })

    # ... process query ...

    # Emit progress updates
    await websocket.send_json({
        "event_type": "progress",
        "current": 1,
        "total": 3,
        "message": "Researching topic...",
        "stage": "researching",
    })

    # ... continue processing ...

    return {"final_response": "Final answer here"}
```

---

## 6. Business Rules

| Rule | Description | Enforcement | Source |
|------|-------------|-------------|--------|
| BR-UX-001 | Skeleton appears < 300ms | Frontend component | Immediate feedback |
| BR-UX-002 | First token < 1s | Backend streaming | Perceived speed |
| BR-UX-003 | Background prompt at 15s | Progress tracker | Reduce abandonment |
| BR-UX-004 | Progressive disclosure for complex results | Synthesizer | Prevent overwhelm |
| BR-UX-005 | Fallback to spinner if streaming unavailable | Error handling | Graceful degradation |

---

## 7. Acceptance Criteria

- [ ] Skeleton appears within 300ms
- [ ] First token arrives < 1s
- [ ] Progress updates every 1-2s
- [ ] Background prompt appears after 15s
- [ ] Progressive disclosure shows summary first
- [ ] Graceful degradation when streaming fails
- [ ] Ruff and pyrefly checks pass

---

## 8. Test Scenarios

### 8.1 Streaming Response

| Task | Duration | Expected Behavior |
|------|----------|-------------------|
| Simple query | < 5s | Stream tokens, no skeleton needed |
| Moderate query | 15-30s | Skeleton → tokens → complete |
| Complex query | 30-60s | Skeleton → progress → tokens → background prompt? |

### 8.2 Background Prompt

| Elapsed Time | User Action | Expected |
|--------------|-------------|----------|
| < 15s | None | Continue waiting |
| 15s | User clicks "Continue" | Task continues in background, notify when complete |
| 15s | User waits | Task continues normally |

---

## 9. Frontend Integration

### 9.1 Streaming Component

```typescript
// frontend/components/StreamingResponse.tsx
import { useState, useEffect } from 'react';

interface StreamingResponseProps {
  sessionId: string;
  query: string;
}

export function StreamingResponse({ sessionId, query }: StreamingResponseProps) {
  const [tokens, setTokens] = useState<string[]>([]);
  const [progress, setProgress] = useState<ProgressEvent | null>(null);
  const [isComplete, setIsComplete] = useState(false);
  const [showSkeleton, setShowSkeleton] = useState(true);

  useEffect(() => {
    // Connect to WebSocket for streaming
    const ws = new WebSocket(`ws://localhost:8015/ws/stream/${sessionId}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.event_type) {
        case 'token':
          // Append token
          setTokens(prev => [...prev, data.token]);
          setShowSkeleton(false);
          break;

        case 'progress':
          setProgress(data);
          break;

        case 'background_prompt':
          // Show background continuation prompt
          setShowBackgroundPrompt(true);
          break;

        case 'complete':
          setIsComplete(true);
          break;
      }
    };

    return () => ws.close();
  }, [sessionId]);

  return (
    <div>
      {showSkeleton && <SkeletonScreen />}
      {tokens.length > 0 && (
        <div>
          <StreamingText tokens={tokens} />
          {progress && <ProgressBar {...progress} />}
        </div>
      )}
      {isComplete && <CompleteBadge />}
    </div>
  );
}

function SkeletonScreen() {
  return (
    <div className="skeleton-screen">
      <div className="skeleton-title shimmer" />
      <div className="skeleton-text shimmer" />
      <div className="skeleton-text shimmer" />
      <div className="skeleton-text shimmer short" />
    </div>
  );
}

function StreamingText({ tokens }: { tokens: string[] }) {
  return (
    <div className="streaming-text">
      {tokens.join('')}
    </div>
  );
}
```

### 9.2 Progressive Disclosure

```typescript
// frontend/components/ProgressiveDisclosure.tsx
export function ProgressiveDisclosure({ findings }: { findings: string[] }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div>
      <SummaryView findings={findings.slice(0, 3)} />

      <button onClick={() => setExpanded(!expanded)}>
        {expanded ? 'Show Less' : `Show All (${findings.length})`}
      </button>

      {expanded && <DetailedView findings={findings} />}
    </div>
  );
}
```

---

## 10. References

- **Transient UX Research**: tavily_research on long-running AI task UX patterns
- **Skeleton Screens**: UX research on 300ms target
- **Progressive Disclosure**: Information architecture best practices
- **Streaming Patterns**: OpenAI, Anthropic streaming APIs

---

## 11. UX Guidelines Summary

| Wait Time | Pattern | Implementation |
|-----------|--------|----------------|
| < 2s | No indicator needed | Direct response |
| 2-9s | Indeterminate loop | Spinner with "Working..." |
| ≥ 10s | Determinate progress | Progress bar + stage text |
| ≥ 15s | Background continuation | "Continue in background?" prompt |
| Any | Skeleton | Show structure within 300ms |

---

**Next**: See `query-complexity-assessment/spec.md` for how query planning integrates with these UX patterns.

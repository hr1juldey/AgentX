"""Domain models for the AgentX system.

This package contains Pydantic models and TypedDicts for:
- AgentState with reducers (graph_state)
- Execution plans (query_plan)
- Routing decisions (routing)
- Episodic memory (episodic_memory)
- STT preprocessing (stt_preprocessing)
- Streaming events (streaming_events)
- Voice subgraph state (voice_state)
- Widget selection (widget_selection)
"""

from agentx.domain.models.episodic_memory import (
    EpisodicMemory,
    OutcomeQuality,
    TemporalMetadata,
    TemporalType,
)
from agentx.domain.models.graph_state import AgentState
from agentx.domain.models.query_plan import ExecutionPlan, ResearchTask, TaskType
from agentx.domain.models.routing import (
    ContinuationAction,
    ContinuationDecision,
    ResearchQuality,
    RoutingPath,
)
from agentx.domain.models.stt_preprocessing import InputPath, PreprocessedQuery
from agentx.domain.models.streaming_events import (
    BackgroundPromptEvent,
    CompleteEvent,
    ProgressEvent,
    StreamingEventType,
    TokenEvent,
    WidgetRevealEvent,
)
from agentx.domain.models.voice_state import VoiceState
from agentx.domain.models.widget_selection import (
    ContentPattern,
    WidgetSpecification,
    WidgetType,
)

__all__ = [
    # graph_state
    "AgentState",
    # query_plan
    "ExecutionPlan",
    "ResearchTask",
    "TaskType",
    # routing
    "ContinuationAction",
    "ContinuationDecision",
    "ResearchQuality",
    "RoutingPath",
    # episodic_memory
    "EpisodicMemory",
    "TemporalMetadata",
    "TemporalType",
    "OutcomeQuality",
    # stt_preprocessing
    "InputPath",
    "PreprocessedQuery",
    # streaming_events
    "StreamingEventType",
    "TokenEvent",
    "ProgressEvent",
    "WidgetRevealEvent",
    "BackgroundPromptEvent",
    "CompleteEvent",
    # voice_state
    "VoiceState",
    # widget_selection
    "WidgetType",
    "ContentPattern",
    "WidgetSpecification",
]

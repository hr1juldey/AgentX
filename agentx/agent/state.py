"""LangGraph State definition for Real AgentX v0.1.

AgentState TypedDict with ui_message_reducer for server-driven UI (C007).
Following LangGraph documentation from docs.langchain.com/langsmith/generative-ui-react
"""

from typing import Annotated, Sequence

from langgraph.graph.message import add_messages  # type: ignore[import]
from langgraph.graph.ui import (  # type: ignore[import]
    AnyUIMessage,
    ui_message_reducer,
)
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    """Agent state for LangGraph with server-driven UI support.

    The ui field uses ui_message_reducer for automatic state tracking.
    Designer agent can access state.ui to see existing widgets.

    Attributes:
        messages: Conversation messages with add_messages reducer
        ui: UI components with ui_message_reducer (automatic tracking)
        session_id: Current session identifier
        reasoning_steps: Current reasoning step count
        total_tool_calls: Total number of tool calls made
        contextualized_data: Research data from contextualizer (optional, for Pass 2)
    """

    messages: Annotated[Sequence[BaseMessage], add_messages]
    ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]
    session_id: str | None
    reasoning_steps: int
    total_tool_calls: int
    contextualized_data: dict[str, object]  # type: ignore[assignment]
    _analysis: dict[str, object]  # type: ignore[assignment]  # Analyst results
    _research: dict[str, object]  # type: ignore[assignment]  # Research results
    _widget_design: dict[str, object]  # type: ignore[assignment]  # Designer results
    _widget_selection: dict[str, object]  # type: ignore[assignment]  # Widget selector results

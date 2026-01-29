"""LangGraph State definition for Real AgentX v0.1.

AgentState TypedDict with ui_message_reducer for server-driven UI (C007).
Following LangGraph documentation from docs.langchain.com/langsmith/generative-ui-react
"""

from typing import Annotated, Sequence

from langgraph.graph.messages import add_messages
from langgraph.graph.ui import ui_message_reducer, AnyUIMessage
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """Agent state for LangGraph with server-driven UI support.

    The ui field uses ui_message_reducer for automatic state tracking.
    Designer agent can access state.ui to see existing widgets.

    Attributes:
        messages: Conversation messages with add_messages reducer
        ui: UI components with ui_message_reducer (automatic tracking)
        session_id: Current session identifier
        reasoning_steps: Current reasoning step count
    """

    messages: Annotated[Sequence[BaseMessage], add_messages]
    ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]
    session_id: str | None
    reasoning_steps: int
    total_tool_calls: int

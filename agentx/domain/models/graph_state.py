"""Domain models for LangGraph agent state.

This module defines the AgentState TypedDict with reducers for state-driven routing.
State accumulates across iterations to support evaluator decisions.

Key insight: Findings accumulate with each research iteration.
The evaluator reads accumulated state to decide "what do I know vs what do I need?"
"""

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages
from operator import add

from agentx.domain.models.query_plan import ExecutionPlan
from agentx.domain.models.routing import ResearchQuality
from agentx.domain.models.stt_preprocessing import InputPath
from agentx.domain.models.widget_selection import WidgetSpecification


class AgentState(TypedDict):
    """Shared state for state-driven routing.

    Key insight: State ACCUMULATES across iterations.
    The evaluator reads this accumulated state to decide "what do I know?"
    """

    # Input
    messages: Annotated[list, add_messages]
    query: str
    user_id: str
    session_id: str
    input_path: InputPath
    preprocessed_query: str | None

    # Execution plan
    execution_plan: ExecutionPlan
    current_iteration: int

    # ACCUMULATED STATE (for state-driven decisions)
    research_findings: Annotated[list[str], add]  # Accumulates!
    research_sources: Annotated[list[str], add]  # Accumulates!
    task_results: dict[str, str]  # {task_id: result}
    information_gaps: Annotated[list[str], add]  # Accumulates!

    # State for evaluator decisions
    accumulated_confidence: float  # Increases with each finding
    research_quality: ResearchQuality | None  # LLM's assessment

    # Execution tracking
    visited_tasks: list[str]  # Tasks executed (not accumulated)
    execution_path: Annotated[list[str], add]  # Nodes visited

    # Output
    final_response: str | None
    selected_widgets: list[WidgetSpecification]  # For UI

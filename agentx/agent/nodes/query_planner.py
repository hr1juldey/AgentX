"""Query planner node for the dynamic agent graph.

This node generates execution plans using the QueryPlannerModule DSPy module.
It analyzes query complexity and determines if research is needed.
"""

from agentx.agent.tools.planner.query_planner import QueryPlannerModule
from agentx.domain.models.graph_state import AgentState
from agentx.domain.models.stt_preprocessing import InputPath


def query_planner_node(state: AgentState) -> dict:
    """Generate execution plan for the query.

    This node uses the QueryPlannerModule to analyze the query
    and generate an execution plan with 0 to N research tasks.

    Args:
        state: Current agent state

    Returns:
        dict: Updated state with execution_plan and initial values
    """
    query = state["query"]

    # Get conversation context from messages
    messages = state.get("messages", [])
    conversation_context = ""
    if messages:
        conversation_context = "\n".join(str(m) for m in messages[-5:])

    # Initialize planner module
    planner = QueryPlannerModule()

    # Generate execution plan
    prediction = planner(
        query=query,
        conversation_context=conversation_context,
    )

    execution_plan = prediction.execution_plan  # type: ignore[attr-defined]

    return {
        "execution_plan": execution_plan,
        "current_iteration": 0,
        "research_findings": [],
        "research_sources": [],
        "task_results": {},
        "information_gaps": [],
        "accumulated_confidence": 0.0,
        "research_quality": None,
        "visited_tasks": [],
        "execution_path": ["query_planner"],
        # Determine input path if not set
        "input_path": state.get("input_path", InputPath.TEXT),
        "preprocessed_query": state.get("preprocessed_query", query),
    }

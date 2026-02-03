"""Query planner node for the dynamic agent graph.

This node generates execution plans using the QueryPlannerModule DSPy module.
It analyzes query complexity and determines if research is needed.

ENHANCED with memory-guided search planning from SearchGuidanceModule.
"""

from agentx.agent.dspy_signatures.decision_signatures import SearchGuidanceModule
from agentx.agent.tools.planner.query_planner import QueryPlannerModule
from agentx.domain.models.graph_state import AgentState
from agentx.domain.models.stt_preprocessing import InputPath


async def query_planner_node(state: AgentState) -> dict:
    """Generate execution plan for the query.

    This node uses the QueryPlannerModule to analyze the query
    and generate an execution plan with 0 to N research tasks.

    ENHANCED with memory-guided search planning:
    1. Retrieves user preferences from memory (optional)
    2. Passes guidance to planner for enhanced task generation
    3. PRESERVES existing 0-to-N task pattern

    Args:
        state: Current agent state

    Returns:
        dict: Updated state with execution_plan and initial values
    """
    query = state["query"]
    user_id = state.get("user_id", "default")

    # Get conversation context from messages
    messages = state.get("messages", [])
    conversation_context = ""
    if messages:
        conversation_context = "\n".join(str(m) for m in messages[-5:])

    # Step 1: Retrieve memory-guided search context (ENHANCEMENT)
    # This is OPTIONAL - the planner works without it
    search_guidance = None
    try:
        guidance_module = SearchGuidanceModule()
        guidance_result = await guidance_module(
            query=query,
            user_id=user_id,
        )
        # Convert Prediction to dict for easier access
        search_guidance = {
            "search_depth": guidance_result.search_depth,  # type: ignore[attr-defined]
            "prioritized_terms": guidance_result.prioritized_terms,  # type: ignore[attr-defined]
            "source_preferences": guidance_result.source_preferences,  # type: ignore[attr-defined]
            "answer_format": guidance_result.answer_format,  # type: ignore[attr-defined]
        }
    except Exception:
        # If memory retrieval fails, continue without guidance
        search_guidance = None

    # Step 2: Generate ExecutionPlan (PRESERVED - 0 to N tasks pattern)
    planner = QueryPlannerModule()

    prediction = planner(
        query=query,
        conversation_context=conversation_context,
        search_guidance=search_guidance,
    )

    execution_plan = prediction.execution_plan  # type: ignore[attr-defined]

    # CRITICAL: PRESERVE existing state structure
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

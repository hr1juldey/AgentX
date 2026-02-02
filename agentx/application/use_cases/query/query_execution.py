"""Query execution logic for agent processing.

Handles the main query processing workflow with LangGraph.
"""

import logging
from langchain_core.messages import HumanMessage

from agentx.agent.graph import get_graph
from agentx.application.dtos.ui_dtos import UIComponentDTO
from agentx.application.use_cases.query.ui_extraction import extract_ui_components
from agentx.core.dependencies import ensure_dspy_configured

logger = logging.getLogger(__name__)


async def execute_query(
    session_id: str,
    query_text: str,
) -> tuple[str, str, list[UIComponentDTO], int]:
    """Execute a query through the LangGraph agent pipeline.

    Args:
        session_id: The session identifier.
        query_text: The user's query text.

    Returns:
        tuple: (response_text, reasoning, ui_components, total_tool_calls)
    """
    # Step 1: Ensure DSPy is configured
    ensure_dspy_configured()
    logger.debug("[QueryExecution] DSPy configured")

    # Step 2: Build initial state for LangGraph
    initial_state = {
        "messages": [HumanMessage(content=query_text)],
        "ui": [],
        "session_id": session_id,
        "reasoning_steps": 0,
        "total_tool_calls": 0,
    }

    # Step 3: Invoke LangGraph (this runs the 7-pipeline agent sequence)
    logger.info("[QueryExecution] Invoking LangGraph...")
    graph = get_graph().compile()  # type: ignore[arg-type]
    final_state = await graph.ainvoke(initial_state)
    logger.info(
        f"[QueryExecution] LangGraph execution complete. "
        f"Total tool calls: {final_state.get('total_tool_calls', 0)}"
    )

    # Step 4: Extract response from final state
    messages = final_state.get("messages", [])
    response_text = ""
    reasoning = ""

    for msg in messages:
        if hasattr(msg, "content") and isinstance(msg.content, str):
            if not response_text:
                response_text = msg.content
            else:
                reasoning += msg.content + "\n"

    if not response_text:
        response_text = "No response generated."
        logger.warning("[QueryExecution] No response text generated")

    logger.debug(f"[QueryExecution] Response length: {len(response_text)} chars")

    # Step 5: Extract UI components from state
    ui_messages = final_state.get("ui", [])
    ui_components = extract_ui_components(ui_messages)
    logger.info(f"[QueryExecution] Extracted {len(ui_components)} UI components")

    # Step 6: Return results
    total_tool_calls = final_state.get("total_tool_calls", 0)
    return (
        response_text,
        reasoning or "Agent processing complete.",
        ui_components,
        total_tool_calls,
    )

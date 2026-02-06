"""Conversation agent node for LangGraph conversation graph.

This node processes user queries through the ConversationAgent.
Following CLAUDE_POLICY.md: Absolute imports only.
"""

import dspy
import logging

from agentx.application.graphs.state import ChatState
from agentx.core.sessions import get_session_manager

logger = logging.getLogger(__name__)


def conversation_agent_node(state: ChatState) -> dict:  # type: ignore[return-value]
    """Process query through ConversationAgent.

    User Decision: Store conversation_history in BOTH graph state AND agent
    internal. Gets or creates session via SessionStateManager, calls agent as
    callable (CORRECT DSPy pattern - NOT .forward()).

    Args:
        state: Current graph state with query, session_id, user_id fields

    Returns:
        dict: Updated state with agent_response and conversation_history
    """
    session_manager = get_session_manager()
    session = session_manager.get_or_create_session(
        state.get("session_id", ""), state.get("user_id", "default")
    )

    agent = session.agent
    query = state.get("query", "")
    result: dspy.Prediction = agent(question=query)  # type: ignore[assignment]

    session_manager.add_assistant_message(state.get("session_id", ""), query, result)

    history = agent.get_history()
    logger.info(f"Agent response: {result.answer}")
    return {
        "agent_response": result.answer,
        "conversation_history": history,
    }


__all__ = ["conversation_agent_node"]

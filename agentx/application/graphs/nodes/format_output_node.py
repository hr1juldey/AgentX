"""Format output node for LangGraph conversation graph.

This node formats agent responses for output (text or TTS).
Following CLAUDE_POLICY.md: Absolute imports only.
"""

import logging

from agentx.application.services.text_processing.tts_formatter import format_tts_phrase
from agentx.application.graphs.state import ChatState

logger = logging.getLogger(__name__)


def format_output_node(state: ChatState) -> dict:  # type: ignore[return-value]
    """Format agent response for output.

    Uses format_tts_phrase() to remove markdown, add punctuation, break long
    sentences.

    Args:
        state: Current graph state with agent_response and error fields

    Returns:
        dict: Updated state with formatted_response
    """
    logger.info(f"format_output_node: state={state}")
    error = state.get("error")
    if error:
        logger.warning(f"Error in state: {error}")
        return {"formatted_response": f"Error: {error}"}

    agent_response = state.get("agent_response")
    if not agent_response:
        logger.error("No agent response in state")
        return {
            "error": "No agent response",
            "formatted_response": "I apologize, but I couldn't generate a response.",
        }

    formatted = format_tts_phrase(agent_response)
    logger.info(
        f"Output formatting: '{agent_response[:100]}...' -> '{formatted[:100]}...'"
    )
    return {"formatted_response": formatted}


__all__ = ["format_output_node"]

"""Validate input node for LangGraph conversation graph.

This node validates and preprocesses user input before passing to the agent.
Following CLAUDE_POLICY.md: Absolute imports only.
"""

import logging

from agentx.application.services.text_processing.stt_cleaner import format_stt_query
from agentx.application.graphs.state import ChatState

logger = logging.getLogger(__name__)


def validate_input_node(state: ChatState) -> dict:  # type: ignore[return-value]
    """Validate and preprocess user input.

    Uses format_stt_query() to remove filler words, fix ASR errors, capitalize.

    Args:
        state: Current graph state with query field

    Returns:
        dict: Updated state with cleaned query or error message
    """
    logger.info(f"validate_input_node: state={state}")
    query = state.get("query", "")
    if not query or len(query.strip()) < 1:
        logger.warning("Empty query received")
        return {"error": "Empty query"}

    cleaned = format_stt_query(query)
    logger.info(f"Input validation: '{query}' -> '{cleaned}'")
    return {"query": cleaned}


__all__ = ["validate_input_node"]

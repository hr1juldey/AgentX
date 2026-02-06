"""Chat WebSocket handler with LangGraph conversation orchestration."""

import logging

from fastapi import WebSocket
from langgraph.errors import GraphRecursionError

from agentx.core.dependencies import get_chat_graph

logger = logging.getLogger(__name__)


async def handle_chat_query(
    websocket: WebSocket,
    query_text: str,
    session_id: str,
) -> None:
    """Handle a chat query through the LangGraph conversation graph.

    Args:
        websocket: WebSocket connection
        query_text: User's query text
        session_id: Session identifier
    """
    try:
        # Invoke LangGraph with input_mode="text" for chat
        # User Decision: thread_id derived with graph type prefix
        config = {
            "configurable": {
                "thread_id": f"conversation:{session_id}",
                "collection_name": "conversation_agent_memory",
            }
        }
        result = get_chat_graph().invoke(  # type: ignore[misc]
            {
                "query": query_text,
                "user_id": "default",
                "session_id": session_id,
                "input_mode": "text",
            },
            config=config,
        )

        response_text = result.get("formatted_response", "")
        await websocket.send_json(
            {
                "message_type": "response",
                "data": {"response": response_text},
                "session_id": session_id,
            }
        )
    except GraphRecursionError as e:
        logger.error(f"Graph recursion error: {e}")
        await websocket.send_json(
            {
                "message_type": "error",
                "data": {"error": "Conversation recursion limit exceeded"},
                "session_id": session_id,
            }
        )
    except Exception as e:
        logger.error(f"Graph execution error: {e}")
        await websocket.send_json(
            {
                "message_type": "error",
                "data": {"error": str(e)},
                "session_id": session_id,
            }
        )

# =============================================================================
# AGENTX R013 - Streaming ReAct WebSocket Endpoint with History
# =============================================================================
# WebSocket endpoint for real-time streaming with dspy.streamify
# Supports conversation history across multiple turns
# =============================================================================

import logging
from typing import Any

import dspy
from fastapi import WebSocket, WebSocketDisconnect

from services.session_manager import get_session_manager

logger = logging.getLogger(__name__)

# dspy.streaming is a dynamic module that exists at runtime
# Access via getattr to avoid type checker issues
_streaming_module: Any = getattr(dspy, "streaming", None)
if _streaming_module is None:
    raise RuntimeError("dspy.streaming module not available")
StreamResponse = _streaming_module.StreamResponse


async def travel_websocket_stream(websocket: WebSocket) -> None:
    """WebSocket endpoint for REAL-TIME streaming with conversation history.

    This endpoint uses the ReAct agent with streamify for true token-level
    streaming as the LLM generates responses.

    CRITICAL: The ReAct agent must be warmed up synchronously BEFORE this
    endpoint is called (done in main.py lifespan).

    Session Management:
    - Client sends session_id in first message or via query param
    - Server maintains conversation history per session
    - History is passed to agent for context-aware responses
    """
    from api.routes import _travel_agent

    await websocket.accept()
    logger.info("Streaming WebSocket connection established")

    # Get session manager
    session_mgr = get_session_manager()

    # Get session_id from query params or create new session
    query_params = dict(websocket.query_params)
    session_id = query_params.get("session_id")
    session = session_mgr.get_or_create_session(session_id)

    # Send session_id to client
    await websocket.send_json(
        {
            "type": "session",
            "session_id": session.session_id,
            "turn_count": len(session.turns),
        }
    )
    logger.info(f"Session {session.session_id}: {len(session.turns)} previous turns")

    input_buffer = []
    input_complete = False

    try:
        # Receive input stream
        while not input_complete:
            data = await websocket.receive_json()

            if data.get("type") == "chunk":
                input_buffer.append(data.get("text", ""))
                await websocket.send_json(
                    {"type": "ack", "received": len(input_buffer)}
                )

            elif data.get("type") == "end":
                input_complete = True
                logger.info(f"Input complete. Received {len(input_buffer)} chunks")

        user_question = "".join(input_buffer)
        logger.info(f"Session {session.session_id}: {user_question[:400]}...")

        # Check agent is ready
        if _travel_agent is None:
            await websocket.send_json(
                {
                    "type": "error",
                    "msg": "Travel agent not initialized. Check server startup.",
                }
            )
            return

        streamer = _travel_agent.get_streamer()
        await websocket.send_json({"type": "status", "msg": "Streaming response..."})

        # Process with real-time streaming, passing history
        final_answer = None
        response_chunks = []

        async for chunk in streamer(question=user_question, history=session.history):
            if isinstance(chunk, StreamResponse):
                # Collect response chunks
                response_chunks.append(chunk.chunk)
                # Send individual tokens/chunks to client
                await websocket.send_json(
                    {
                        "type": "token",
                        "field": chunk.signature_field_name,
                        "chunk": chunk.chunk,
                    }
                )
            elif isinstance(chunk, dspy.Prediction):
                final_answer = chunk
                await websocket.send_json({"type": "prediction", "data": str(chunk)})

        # Build final answer from chunks
        full_response = "".join(response_chunks)

        # Append conversation turn to session history
        session.append_turn(question=user_question, answer=full_response)

        # Signal completion with final answer
        await websocket.send_json(
            {
                "type": "done",
                "final": str(final_answer) if final_answer else full_response,
                "session_id": session.session_id,
                "turn_number": len(session.turns),
            }
        )
        logger.info(f"Session {session.session_id}: Turn {len(session.turns)} complete")

    except WebSocketDisconnect:
        logger.info(f"Session {session.session_id}: WebSocket disconnected")
    except RuntimeError as e:
        logger.error(f"Streaming setup error: {e}")
        await websocket.send_json(
            {"type": "error", "msg": "Streaming not ready - ensure agent was warmed up"}
        )
    except Exception as e:
        logger.error(f"Streaming WebSocket error: {e}")
        await websocket.send_json({"type": "error", "msg": str(e)})

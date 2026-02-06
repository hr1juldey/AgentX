"""Real-time WebSocket API endpoints."""

import logging
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from agentx.core.dependencies import get_voice_gateway


router = APIRouter(prefix="/ws", tags=["websocket"])

logger = logging.getLogger(__name__)


@router.websocket("/test")
async def test_websocket(websocket: WebSocket) -> None:
    """Simple test WebSocket endpoint - no dependencies."""
    await websocket.accept()
    logger.info("Test WebSocket connected successfully!")
    await websocket.send_json({"message": "WebSocket test successful"})
    await websocket.close()


@router.websocket("/root")
async def root_websocket(websocket: WebSocket) -> None:
    """Root WebSocket endpoint - routes to voice gateway.

    This is the primary endpoint for voice conversations with memory.
    Coordinates STT → Agent → TTS flow through VoiceGatewayService.

    Args:
        websocket: WebSocket connection

    Query Params:
        session_id: Optional session identifier (auto-generated if not provided)
    """
    await websocket.accept()

    # Get session_id from query params, generate if not provided
    session_id = websocket.query_params.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.info(f"Generated new session_id: {session_id}")
    logger.info(f"WebSocket connected: session_id={session_id}")

    voice_gateway = get_voice_gateway()

    try:
        await voice_gateway.handle_session(websocket, session_id)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: session_id={session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: session_id={session_id}, error={e}")
        try:
            await websocket.close()
        except Exception:
            pass


@router.websocket("/chat")
async def chat_websocket(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time text chat.

    Handles text-based chat messages with agent responses.
    Keeps connection open for bidirectional messaging.

    Args:
        websocket: WebSocket connection
    """
    await websocket.accept()
    logger.info("Chat WebSocket connected")

    session_id = websocket.query_params.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.info(f"Generated new session_id: {session_id}")

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            logger.info(
                f"Chat message received (session={session_id}): {data[:100]}..."
            )

            # Parse message
            try:
                import json

                message = json.loads(data)
                message_type = message.get("message_type", "unknown")
                message_data = message.get("data", {})

                if message_type == "query":
                    # Handle text query
                    query_text = message_data.get("query", "")
                    logger.info(f"Query: {query_text}")

                    # TODO: Process query through agent
                    # For now, echo back
                    await websocket.send_json(
                        {
                            "message_type": "response",
                            "data": {"response": f"Echo: {query_text}"},
                            "session_id": session_id,
                        }
                    )
                else:
                    logger.warning(f"Unknown message type: {message_type}")
                    await websocket.send_json(
                        {
                            "message_type": "error",
                            "data": {"error": f"Unknown message type: {message_type}"},
                            "session_id": session_id,
                        }
                    )

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse message: {e}")
                await websocket.send_json(
                    {
                        "message_type": "error",
                        "data": {"error": "Invalid JSON format"},
                        "session_id": session_id,
                    }
                )

    except WebSocketDisconnect:
        logger.info(f"Chat WebSocket disconnected: session_id={session_id}")
    except Exception as e:
        logger.error(f"Chat WebSocket error: session_id={session_id}, error={e}")
        try:
            await websocket.close()
        except Exception:
            pass

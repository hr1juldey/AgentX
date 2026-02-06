"""Real-time WebSocket API endpoints."""

import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from agentx.presentation.api.v1.websocket.chat_handler import handle_chat_query
from agentx.presentation.api.v1.websocket.voice_handler import (
    generate_session_id,
    handle_test_websocket,
    handle_voice_websocket,
)

router = APIRouter(prefix="/ws", tags=["websocket"])
logger = logging.getLogger(__name__)


@router.websocket("/test")
async def test_websocket(websocket: WebSocket) -> None:
    """Simple test WebSocket endpoint - no dependencies."""
    await handle_test_websocket(websocket)


@router.websocket("/root")
async def root_websocket(websocket: WebSocket) -> None:
    """Root WebSocket endpoint - routes to voice gateway.

    This is the primary endpoint for voice conversations with memory.
    Coordinates STT → Agent → TTS flow through VoiceGatewayService.

    Query Params:
        session_id: Optional session identifier (auto-generated if not provided)
    """
    session_id = generate_session_id(websocket)
    await handle_voice_websocket(websocket, session_id)


@router.websocket("/chat")
async def chat_websocket(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time text chat.

    Handles text-based chat messages with agent responses.
    Keeps connection open for bidirectional messaging.
    """
    await websocket.accept()
    logger.info("Chat WebSocket connected")

    session_id = generate_session_id(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(
                f"Chat message received (session={session_id}): {data[:100]}..."
            )

            try:
                message = json.loads(data)
                message_type = message.get("message_type", "unknown")
                message_data = message.get("data", {})

                if message_type == "query":
                    query_text = message_data.get("query", "")
                    logger.info(f"Query: {query_text}")
                    await handle_chat_query(websocket, query_text, session_id)
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

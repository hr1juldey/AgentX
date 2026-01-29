"""Voice routes for kyutai integration."""

from uuid import UUID

from fastapi import APIRouter, WebSocket

from agentx.application.dtos.voice_gateway_dtos import (
    ConversationContextDTO,
    ConversationMessageDTO,
)
from agentx.application.use_cases.conversation_state_manager import (
    ConversationStateManager,
)
from agentx.infrastructure.external.voice_gateway_service import (
    VoiceGatewayService,
)

router = APIRouter(prefix="/api/v1/voice", tags=["voice"])
_gateway_service = VoiceGatewayService()
_state_manager = ConversationStateManager()


@router.get("/kyutai/status")
async def kyutai_status() -> dict[str, bool]:
    """Check if kyutai server is available.

    Returns:
        Dictionary with 'available' key.
    """
    available = await _gateway_service.check_kyutai_health()
    return {"available": available}


@router.get("/conversation/history")
async def get_conversation_history(
    session_id: str,
    limit: int = 20,
) -> list[ConversationMessageDTO]:
    """Get conversation history for a session.

    Args:
        session_id: Session identifier.
        limit: Maximum number of messages to return.

    Returns:
        List of conversation messages.
    """
    session = _state_manager.get_session(UUID(session_id))
    if not session:
        return []

    messages = _state_manager.get_conversation_history(UUID(session_id), limit)

    return [
        ConversationMessageDTO(
            messageId=str(msg.message_id),
            role=msg.role,
            content=msg.content,
            timestamp=msg.timestamp,
            metadata=msg.metadata,
        )
        for msg in messages
    ]


@router.post("/conversation/context")
async def update_conversation_context(
    session_id: str,
    context: ConversationContextDTO,
) -> ConversationContextDTO:
    """Update conversation context.

    Args:
        session_id: Session identifier.
        context: Context data to update.

    Returns:
        Updated context.
    """
    _state_manager.update_context(
        UUID(session_id),
        current_topic=context.current_topic,
        entities=context.entities,
        sentiment=context.sentiment,
        language=context.language,
        timezone=context.timezone,
    )

    session = _state_manager.get_session(UUID(session_id))
    if not session:
        return context

    return ConversationContextDTO(
        currentTopic=session.context.current_topic,
        entities=session.context.entities,
        sentiment=session.context.sentiment,
        language=session.context.language,
        timezone=session.context.timezone,
    )


@router.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket) -> None:
    """WebSocket endpoint for voice interaction.

    Handles real-time audio streaming between frontend and kyutai server.

    Args:
        websocket: The WebSocket connection.
    """
    await websocket.accept()

    # Get session_id from query params
    session_id_str = websocket.query_params.get("session_id")
    if not session_id_str:
        await websocket.close(code=1008, reason="Missing session_id")
        return

    try:
        session_id = UUID(session_id_str)
        await _gateway_service.handle_session(websocket, session_id)
    except ValueError:
        await websocket.close(code=1008, reason="Invalid session_id format")
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))

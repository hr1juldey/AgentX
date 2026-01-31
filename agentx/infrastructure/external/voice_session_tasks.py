"""Voice session task handlers for VoiceGatewayService.

Provides input/output task handlers for routing messages
between frontend and kyutai voice-server.
"""

import asyncio
import logging
from typing import Any, TYPE_CHECKING

from agentx.application.dtos.voice_gateway_dtos import KyutaiMessage, KyutaiMessageType
from fastapi import WebSocket

if TYPE_CHECKING:
    from uuid import UUID

    from agentx.application.use_cases.conversation_state_manager import (
        ConversationStateManager,
    )
    from agentx.infrastructure.external.text_stream_handler import TextStreamHandler


logger = logging.getLogger(__name__)


async def input_task(
    frontend_ws: WebSocket,
    session_id: "UUID",
    stt_ws: Any,
    tts_ws: Any,
    text_handler: "TextStreamHandler",
) -> None:
    """Handle messages from frontend to kyutai.

    Args:
        frontend_ws: The frontend WebSocket connection
        session_id: The session UUID
        stt_ws: The STT WebSocket connection
        tts_ws: The TTS WebSocket connection
        text_handler: The text stream handler for interruptions
    """
    try:
        while True:
            data = await frontend_ws.receive_json()
            message = KyutaiMessage.from_dict(data)

            if message.type == KyutaiMessageType.AUDIO:
                await stt_ws.send(message.to_json())
            elif message.type == KyutaiMessageType.TEXT:
                # Handle interruption request
                if message.data.get("action") == "interrupt":
                    text_handler.interrupt_tts(session_id)
                await tts_ws.send(message.to_json())
    except Exception as e:
        logger.error(f"Input task error: {e}")
        raise


async def output_task(
    frontend_ws: WebSocket,
    session_id: "UUID",
    stt_ws: Any,
    tts_ws: Any,
    state_manager: "ConversationStateManager",
    text_handler: "TextStreamHandler",
    process_agent_fn: Any,
) -> None:
    """Handle messages from kyutai to frontend.

    Args:
        frontend_ws: The frontend WebSocket connection
        session_id: The session UUID
        stt_ws: The STT WebSocket connection
        tts_ws: The TTS WebSocket connection
        state_manager: The conversation state manager
        text_handler: The text stream handler
        process_agent_fn: Function to process agent responses
    """
    try:
        stt_task: asyncio.Task | None = None
        tts_task: asyncio.Task | None = None

        while True:
            # Cancel previous pending tasks if they exist
            for task in [stt_task, tts_task]:
                if task and not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass  # Expected cancellation

            # Create new recv tasks
            stt_task = asyncio.create_task(stt_ws.recv())
            tts_task = asyncio.create_task(tts_ws.recv())

            # Wait for first to complete
            done, pending = await asyncio.wait(
                [stt_task, tts_task], return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel pending tasks immediately
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass  # Expected

            # Process completed message
            message = KyutaiMessage.from_json(list(done)[0].result())

            # Handle STT text response
            if (
                message.type == KyutaiMessageType.TEXT
                and message.data.get("source") == "stt"
            ):
                text = message.data.get("text", "")
                # Buffer STT chunk
                transcript = text_handler.buffer_stt_chunk(session_id, text)
                if transcript:
                    # Complete sentence received, process with agent
                    await process_agent_fn(session_id, transcript)
                await frontend_ws.send_json(message.to_dict())
            # Handle TTS audio response
            elif message.type == KyutaiMessageType.AUDIO:
                await frontend_ws.send_json(message.to_dict())
            # Handle error messages
            elif message.type == KyutaiMessageType.ERROR:
                await frontend_ws.send_json(message.to_dict())
            # Forward all other messages
            else:
                await frontend_ws.send_json(message.to_dict())

    except Exception as e:
        logger.error(f"Output task error: {e}")
        raise
    finally:
        # Final cleanup
        for task in [stt_task, tts_task]:
            if task and not task.done():
                task.cancel()

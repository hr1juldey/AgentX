"""Voice direct output task handling.

Handles messages from kyutai to frontend.
"""

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from agentx.application.dtos.voice_gateway_dtos import KyutaiMessage, KyutaiMessageType

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from fastapi import WebSocket

logger = logging.getLogger(__name__)


async def run_output_task(
    frontend_ws: "WebSocket",
    session_id: UUID,
    stt_ws: Any,
    tts_ws: Any,
    agent_callback: "Callable[[str], str] | None" = None,
    state_manager: object = None,
    text_handler: object = None,
) -> None:
    """Handle messages from kyutai to frontend.

    Args:
        frontend_ws: Frontend WebSocket connection
        session_id: The session identifier
        stt_ws: STT WebSocket connection
        tts_ws: TTS WebSocket connection
        agent_callback: Agent callback for processing text
        state_manager: Conversation state manager
        text_handler: Text stream handler
    """
    from agentx.infrastructure.external.voice_direct.task_utils import (
        cancel_pending_tasks,
        wait_for_first_completed,
    )

    stt_task: asyncio.Task | None = None
    tts_task: asyncio.Task | None = None

    try:
        while True:
            # Cancel previous pending tasks if they exist
            cancel_pending_tasks(stt_task, tts_task)

            # Create new recv tasks
            stt_task = asyncio.create_task(stt_ws.recv())
            tts_task = asyncio.create_task(tts_ws.recv())

            # Wait for first to complete
            done, _pending = await wait_for_first_completed(stt_task, tts_task)

            # Process completed message
            message = KyutaiMessage.from_json(list(done)[0].result())

            if (
                message.type == KyutaiMessageType.TEXT
                and message.data.get("source") == "stt"
            ):
                text = message.data.get("text", "")
                if text_handler and agent_callback:
                    transcript = text_handler.buffer_stt_chunk(  # type: ignore[missing-attribute]
                        session_id, text
                    )
                    if transcript:
                        response = agent_callback(transcript)
                        if state_manager:
                            state_manager.add_user_message(  # type: ignore[missing-attribute]
                                session_id, transcript
                            )
                            state_manager.add_assistant_message(  # type: ignore[missing-attribute]
                                session_id, response
                            )

                        async def send_sentence(sentence: str) -> None:
                            await tts_ws.send(
                                KyutaiMessage(
                                    type=KyutaiMessageType.TEXT,
                                    data={"text": sentence, "action": "speak"},
                                    sessionId=str(session_id),
                                    timestamp=0,
                                ).to_json()
                            )

                        await text_handler.stream_tts_sentences(  # type: ignore[missing-attribute]
                            session_id, response, send_sentence
                        )
                await frontend_ws.send_json(message.to_dict())
            else:
                await frontend_ws.send_json(message.to_dict())

    except Exception as e:
        logger.error(f"Output task error: {e}")
        raise
    finally:
        # Final cleanup
        cancel_pending_tasks(stt_task, tts_task)

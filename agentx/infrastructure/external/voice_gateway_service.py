"""Voice gateway service for external kyutai integration."""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any
from uuid import UUID

import websockets
from fastapi import WebSocket

from agentx.application.dtos.voice_gateway_dtos import KyutaiMessage, KyutaiMessageType
from agentx.infrastructure.external.voice_protocol import (
    KYUTAI_STT_URL,
    KYUTAI_TTS_URL,
    create_config_message,
)

if TYPE_CHECKING:
    from agentx.application.use_cases.conversation_state_manager import (
        ConversationStateManager,
    )
    from agentx.infrastructure.external.text_stream_handler import TextStreamHandler


class VoiceGatewayError(Exception):
    """Voice gateway error."""


@dataclass
class VoiceGatewayConfig:
    """Voice gateway configuration."""

    stt_url: str = KYUTAI_STT_URL
    tts_url: str = KYUTAI_TTS_URL
    max_concurrent_sessions: int = 5


@dataclass
class VoiceSession:
    """Active voice session."""

    session_id: UUID
    frontend_ws: WebSocket
    stt_ws: Any | None = None  # type: ignore[valid-type]
    tts_ws: Any | None = None  # type: ignore[valid-type]
    interrupted: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class VoiceGatewayService:
    """Gateway for routing messages between frontend and kyutai voice-server."""

    def __init__(
        self,
        config: VoiceGatewayConfig | None = None,
        state_manager: "ConversationStateManager | None" = None,
        text_handler: "TextStreamHandler | None" = None,
    ) -> None:
        """Initialize voice gateway service."""
        from agentx.application.use_cases.conversation_state_manager import (
            ConversationStateManager,
        )
        from agentx.infrastructure.external.text_stream_handler import TextStreamHandler

        self._config = config or VoiceGatewayConfig()
        self._sessions: dict[UUID, VoiceSession] = {}
        self._state_manager = state_manager or ConversationStateManager()
        self._text_handler = text_handler or TextStreamHandler()

    async def handle_session(self, frontend_ws: WebSocket, session_id: UUID) -> None:
        """Handle a voice session WebSocket connection."""
        if len(self._sessions) >= self._config.max_concurrent_sessions:
            raise VoiceGatewayError("Max concurrent sessions reached")

        # Create or get conversation session
        self._state_manager.get_or_create_session(session_id)

        stt_ws = await websockets.connect(self._config.stt_url)
        tts_ws = await websockets.connect(self._config.tts_url)

        config_msg = create_config_message(session_id, streaming_mode="both")
        await stt_ws.send(config_msg.to_json())
        await tts_ws.send(config_msg.to_json())

        session = VoiceSession(
            session_id=session_id,
            frontend_ws=frontend_ws,
            stt_ws=stt_ws,
            tts_ws=tts_ws,
        )
        self._sessions[session_id] = session

        try:
            await asyncio.gather(self._input_task(session), self._output_task(session))
        finally:
            await self._cleanup_session(session_id)

    async def _input_task(self, session: VoiceSession) -> None:
        """Handle messages from frontend to kyutai."""
        try:
            while True:
                data = await session.frontend_ws.receive_json()
                message = KyutaiMessage.from_dict(data)

                if message.type == KyutaiMessageType.AUDIO and session.stt_ws:
                    await session.stt_ws.send(message.to_json())  # type: ignore[union-attr]
                elif message.type == KyutaiMessageType.TEXT:
                    # Handle interruption request
                    if message.data.get("action") == "interrupt":
                        self._text_handler.interrupt_tts(session.session_id)
                        if session.tts_ws:
                            await session.tts_ws.send(message.to_json())  # type: ignore[union-attr]
                    elif session.tts_ws:
                        await session.tts_ws.send(message.to_json())  # type: ignore[union-attr]
        except Exception as e:
            raise VoiceGatewayError(f"Input task error: {e}") from e

    async def _output_task(self, session: VoiceSession) -> None:
        """Handle messages from kyutai to frontend."""
        try:
            while True:
                stt_task = (
                    asyncio.create_task(session.stt_ws.recv())  # type: ignore[union-attr]
                    if session.stt_ws
                    else None
                )
                tts_task = (
                    asyncio.create_task(session.tts_ws.recv())  # type: ignore[union-attr]
                    if session.tts_ws
                    else None
                )

                if stt_task and tts_task:
                    done, _ = await asyncio.wait(
                        [stt_task, tts_task], return_when=asyncio.FIRST_COMPLETED
                    )
                    message = KyutaiMessage.from_json(list(done)[0].result())
                elif stt_task:
                    message = KyutaiMessage.from_json(await stt_task)
                elif tts_task:
                    message = KyutaiMessage.from_json(await tts_task)
                else:
                    break

                # Handle STT text response
                if (
                    message.type == KyutaiMessageType.TEXT
                    and message.data.get("source") == "stt"
                ):
                    text = message.data.get("text", "")
                    # Buffer STT chunk
                    transcript = self._text_handler.buffer_stt_chunk(
                        session.session_id, text
                    )
                    if transcript:
                        # Complete sentence received, process with agent
                        await self._process_agent_response(session, transcript)
                    await session.frontend_ws.send_json(message.to_dict())
                # Handle TTS audio response
                elif message.type == KyutaiMessageType.AUDIO and session.tts_ws:
                    await session.frontend_ws.send_json(message.to_dict())
                # Handle error messages
                elif message.type == KyutaiMessageType.ERROR:
                    await session.frontend_ws.send_json(message.to_dict())
                # Forward all other messages
                else:
                    await session.frontend_ws.send_json(message.to_dict())
        except Exception as e:
            raise VoiceGatewayError(f"Output task error: {e}") from e

    async def _process_agent_response(
        self, session: VoiceSession, user_text: str
    ) -> None:
        """Process user text through C003 agent and send response to TTS.

        Args:
            session: The active voice session.
            user_text: The transcribed user input.
        """
        # Track user message
        self._state_manager.add_user_message(session.session_id, user_text)

        # TODO: Integrate with C003 agent pipeline
        # For now, echo the response
        agent_response = f"You said: {user_text}"

        # Track assistant message
        self._state_manager.add_assistant_message(session.session_id, agent_response)

        # Stream TTS with sentence splitting
        async def send_sentence(sentence: str) -> None:
            """Send a sentence to TTS."""
            if session.tts_ws:
                tts_message = KyutaiMessage(
                    type=KyutaiMessageType.TEXT,
                    data={"text": sentence, "action": "speak"},
                    sessionId=str(session.session_id),  # type: ignore[call-arg]
                    timestamp=datetime.now(timezone.utc).timestamp(),
                )
                await session.tts_ws.send(tts_message.to_json())  # type: ignore[union-attr]

        await self._text_handler.stream_tts_sentences(
            session.session_id, agent_response, send_sentence
        )

    async def _cleanup_session(self, session_id: UUID) -> None:
        """Clean up a voice session."""
        session = self._sessions.pop(session_id, None)
        if session:
            if session.stt_ws:
                await session.stt_ws.close()  # type: ignore[union-attr]
            if session.tts_ws:
                await session.tts_ws.close()  # type: ignore[union-attr]
        # Clean up text handler state
        self._text_handler.cleanup_session(session_id)

    async def check_kyutai_health(self) -> bool:
        """Check if kyutai server is available."""
        try:
            async with websockets.connect(self._config.stt_url) as _:
                return True
        except Exception:
            return False

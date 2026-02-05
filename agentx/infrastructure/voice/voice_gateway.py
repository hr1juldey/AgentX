"""Voice Gateway Service - WebSocket endpoint handler for voice sessions."""

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

import dspy

if TYPE_CHECKING:
    from agentx.infrastructure.memory.session_state_manager import SessionStateManager
    from agentx.infrastructure.voice.voice_adapter import VoiceSDKAdapter

logger = logging.getLogger(__name__)


class VoiceGatewayService:
    """WebSocket gateway service for voice interactions.

    Coordinates between WebSocket client, SessionStateManager,
    and VoiceSDKAdapter for STT → Agent → TTS flow.
    """

    def __init__(
        self,
        session_manager: "SessionStateManager",
        voice_adapter: "VoiceSDKAdapter",
    ) -> None:
        """Initialize the voice gateway service.

        Args:
            session_manager: Session state manager instance
            voice_adapter: Voice SDK adapter instance
        """
        from agentx.infrastructure.memory.session_state_manager import (
            SessionStateManager,
        )
        from agentx.infrastructure.voice.voice_adapter import VoiceSDKAdapter

        self._session_manager: SessionStateManager = session_manager
        self._voice_adapter: VoiceSDKAdapter = voice_adapter

    async def handle_session(self, websocket: Any, session_id: str) -> None:
        """Handle WebSocket voice session.

        Gets or creates session, routes messages through STT → Agent → TTS.

        Args:
            websocket: WebSocket connection
            session_id: Session identifier
        """
        session = self._session_manager.get_or_create_session(session_id)
        agent_callback = self._create_agent_callback(session_id, session)
        await self._voice_adapter.handle_session(websocket, session_id, agent_callback)

    def _create_agent_callback(
        self, session_id: str, session: Any
    ) -> Callable[[str], Any]:
        """Create agent callback for processing transcribed text.

        Args:
            session_id: Session identifier
            session: Session state with agent

        Returns:
            Async callback function that uses streaming internally
        """
        from agentx.application.agents.conversation import (
            create_streaming_agent,
        )

        # Create streaming wrapper for the agent
        streaming_agent = create_streaming_agent(session.agent)

        async def agent_callback(text: str) -> str:
            """Process transcribed text through streaming agent.

            Args:
                text: Transcribed user input

            Returns:
                Complete agent response text
            """
            final_prediction: dspy.Prediction | None = None

            # Iterate over streaming response
            async for chunk in streaming_agent(question=text):
                if isinstance(chunk, dspy.streaming.StreamResponse):
                    # Token chunk - could be sent to WebSocket for real-time streaming
                    logger.debug(f"Streaming token: {chunk.chunk}")
                elif isinstance(chunk, dspy.Prediction):
                    # Final prediction
                    final_prediction = chunk

            # Extract response from final prediction
            if final_prediction is None:
                # Fallback to sync forward if streaming failed
                final_prediction = session.agent.forward(question=text)

            response = self._extract_response(final_prediction)

            self._session_manager.add_assistant_message(
                session_id,
                text,
                final_prediction,  # type: ignore[arg-type]
            )

            return response

        return agent_callback

    def _extract_response(self, prediction: Any) -> str:
        """Extract answer text from DSPy Prediction.

        Args:
            prediction: DSPy Prediction object

        Returns:
            Response text string
        """
        answer = prediction.get("answer")  # type: ignore[no-untyped-call]
        return answer if answer is not None else str(prediction)

"""Voice Gateway Service - WebSocket endpoint handler for voice sessions."""


class VoiceGatewayService:
    """WebSocket gateway service for voice interactions."""

    def __init__(self) -> None:
        """Initialize the voice gateway service.

        Raises:
            NotImplementedError: If not yet implemented
        """
        raise NotImplementedError("VoiceGatewayService not yet implemented")

    async def handle_session(self, websocket: object, session_id: str) -> None:
        """Handle WebSocket voice session.

        Args:
            websocket: WebSocket connection
            session_id: Session identifier

        Raises:
            NotImplementedError: If not yet implemented
        """
        raise NotImplementedError(
            "VoiceGatewayService.handle_session() not yet implemented"
        )

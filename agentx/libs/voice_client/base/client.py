"""Base WebSocket client with auto-reconnection and protocol handling.

Provides the foundation for STT and TTS clients with connection management,
message encoding/decoding, and automatic reconnection.
"""

import types

from typing_extensions import Self

from voice_client.base.connection import ConnectionMixin
from voice_client.base.messaging import MessagingMixin


class BaseClient(ConnectionMixin, MessagingMixin):
    """Base WebSocket client with auto-reconnection and protocol handling.

    Attributes:
        DEFAULT_URL: Default WebSocket URL
        DEFAULT_TIMEOUT: Default connection timeout in seconds
        RECONNECT_INITIAL_DELAY: Initial reconnection delay in seconds
        RECONNECT_MAX_DELAY: Maximum reconnection delay in seconds
        HEARTBEAT_INTERVAL: Heartbeat interval in seconds
    """

    HEARTBEAT_INTERVAL = 60.0

    # Subclasses should define this
    endpoint: str = ""

    def __init__(
        self,
        url: str | None = None,
        api_key: str | None = None,
        encoding: str = "json",
        timeout: float = ConnectionMixin.DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the base client.

        Args:
            url: WebSocket server URL (without endpoint)
            api_key: Optional API key for authentication
            encoding: Message encoding ("json" or "msgpack")
            timeout: Connection timeout in seconds
        """
        base_url = url or self.DEFAULT_URL
        self.url = f"{base_url}/{self.endpoint}?encoding={encoding}"
        if api_key:
            self.url += f"&api_key={api_key}"

        ConnectionMixin.__init__(self, url, timeout)
        MessagingMixin.__init__(self, encoding)

    @property
    def session_id(self) -> str:
        """Get the current session ID, with empty string fallback.

        Returns:
            The session ID or empty string if not connected
        """
        return self._session_id or ""

    async def __aenter__(self) -> Self:
        """Enter the async context manager.

        Returns:
            The connected client instance
        """

        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Exit the async context manager.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        await self.disconnect()

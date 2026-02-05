"""WebSocket connection management with auto-reconnection."""

import asyncio
import uuid

import websockets
from agentx.libs.voice_client.exceptions import ConnectionError as VoiceConnectionError


class ConnectionMixin:
    """WebSocket connection management with automatic reconnection.

    Provides connect/disconnect functionality with exponential backoff retry.
    """

    DEFAULT_URL = "ws://localhost:16000/api/v1/ws"
    DEFAULT_TIMEOUT = 30.0
    RECONNECT_INITIAL_DELAY = 1.0
    RECONNECT_MAX_DELAY = 30.0

    def __init__(self, url: str | None, timeout: float) -> None:
        """Initialize connection parameters.

        Args:
            url: WebSocket server URL (without endpoint)
            timeout: Connection timeout in seconds
        """
        # URL is built by subclass BaseClient
        self.timeout = timeout
        self._ws: websockets.WebSocketClientProtocol | None = None
        self._session_id: str | None = None
        self._running = False
        self._message_task: asyncio.Task[None] | None = None

    async def connect(self) -> None:
        """Connect with automatic retry and exponential backoff.

        Raises:
            VoiceConnectionError: If connection fails after all retries
        """
        delay = self.RECONNECT_INITIAL_DELAY

        while True:
            try:
                self._ws = await asyncio.wait_for(
                    websockets.connect(self.url),
                    timeout=self.timeout,
                )
                self._session_id = str(uuid.uuid4())
                self._running = True

                # Start message handler task
                self._message_task = asyncio.create_task(self._message_loop())

                return

            except (OSError, asyncio.TimeoutError) as e:
                if delay >= self.RECONNECT_MAX_DELAY:
                    raise VoiceConnectionError(f"Failed to connect after {delay:.1f}s delay") from e

                # Wait before retrying
                await asyncio.sleep(delay)
                delay = min(delay * 2, self.RECONNECT_MAX_DELAY)

    async def disconnect(self) -> None:
        """Gracefully disconnect."""
        self._running = False

        if self._message_task:
            try:
                await asyncio.wait_for(self._message_task, timeout=1.0)
            except asyncio.TimeoutError:
                self._message_task.cancel()
            self._message_task = None

        if self._ws:
            await self._ws.close()
            self._ws = None

        self._session_id = None

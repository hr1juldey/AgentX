# =============================================================================
# AGENTX R014 - Real WebSocket Test Client
# =============================================================================

import json
import logging
from collections.abc import AsyncIterator

from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket

logger = logging.getLogger(__name__)


class WebSocketTestClient:
    """Real WebSocket client wrapper for testing WebSocket endpoints.

    This connects to actual WebSocket endpoints in the FastAPI test app,
    simulating real frontend WebSocket connections.
    """

    def __init__(self, app, endpoint: str):
        """Initialize WebSocket test client.

        Args:
            app: FastAPI application instance
            endpoint: WebSocket endpoint path (e.g., "/api/v1/ws/generate-widget")
        """
        from fastapi.testclient import TestClient

        self.app = app
        self.endpoint = endpoint
        self.client = TestClient(app)
        self.websocket: WebSocket | None = None
        self._connected = False

    async def connect(self) -> None:
        """Connect to the WebSocket endpoint."""
        logger.info(f"🔌 Connecting to WebSocket: {self.endpoint}")
        try:
            self.client = TestClient(self.app)
            # Enter websocket context
            self.websocket = self.client.websocket_connect(self.endpoint)
            self.websocket.__enter__()
            self._connected = True
            logger.info(f"✅ Connected to WebSocket: {self.endpoint}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to WebSocket: {e}")
            raise

    async def close(self) -> None:
        """Close the WebSocket connection."""
        if self.websocket and self._connected:
            try:
                self.websocket.__exit__(None, None, None)
                self._connected = False
                logger.info(f"🔌 Closed WebSocket: {self.endpoint}")
            except Exception as e:
                logger.error(f"❌ Error closing WebSocket: {e}")

    async def send_json(self, data: dict) -> None:
        """Send JSON data to the WebSocket.

        Args:
            data: Dictionary to send as JSON
        """
        if not self._connected:
            raise RuntimeError("WebSocket not connected. Call connect() first.")

        message = json.dumps(data)
        self.websocket.send_text(message)
        logger.debug(f"📤 Sent: {message[:200]}...")

    async def receive_json(self) -> AsyncIterator[dict]:
        """Receive JSON messages from WebSocket as async iterator.

        Yields:
            dict: Parsed JSON message

        Example:
            async for message in ws_client.receive_json():
                print(message)
        """
        if not self._connected:
            raise RuntimeError("WebSocket not connected. Call connect() first.")

        while True:
            try:
                text = self.websocket.receive_text()
                message = json.loads(text)
                logger.debug(f"📥 Received: {str(message)[:200]}...")
                yield message
            except Exception as e:
                logger.debug(f"📡 WebSocket receive ended: {e}")
                break

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

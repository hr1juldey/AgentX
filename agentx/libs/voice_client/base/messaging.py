"""Message handling and protocol support."""

import asyncio
from collections.abc import Callable
from typing import Any

import websockets

from agentx.libs.voice_client.protocol import Message, MessageType


class MessagingMixin:
    """Message handling for WebSocket communication.

    Provides send/receive functionality with message handler registration.
    """

    def __init__(self, encoding: str) -> None:
        """Initialize message handling.

        Args:
            encoding: Message encoding ("json" or "msgpack")
        """
        from agentx.libs.voice_client.protocol import get_encoder

        self.encoding = encoding
        self.encoder = get_encoder(encoding)
        self._message_handlers: dict[MessageType, list[Callable[[Message], Any]]] = {}

    async def send(self, message: Message) -> None:
        """Send a message.

        Args:
            message: The message to send

        Raises:
            VoiceConnectionError: If not connected
        """
        from agentx.libs.voice_client.exceptions import ConnectionError as VoiceConnectionError

        if not self._ws:
            raise VoiceConnectionError("Not connected")

        # Set session_id if not provided
        if message.session_id is None:
            message.session_id = self.session_id

        encoded = self.encoder.encode(message)
        # JSON encoding uses text frames, MessagePack uses binary frames
        if self.encoding == "json":
            await self._ws.send(encoded.decode("utf-8"))
        else:
            await self._ws.send(encoded)

    async def _message_loop(self) -> None:
        """Background task to receive and handle messages."""
        while self._running and self._ws:
            try:
                raw = await asyncio.wait_for(self._ws.recv(), timeout=1.0)
                # Convert text to bytes for decoding if needed
                if isinstance(raw, str):
                    raw = raw.encode("utf-8")
                message = self.encoder.decode(raw)

                # Call registered handlers
                handlers = self._message_handlers.get(message.type, [])
                for handler in handlers:
                    result = handler(message)
                    if asyncio.iscoroutine(result):
                        await result

            except asyncio.TimeoutError:
                continue
            except websockets.exceptions.ConnectionClosed:
                self._running = False
                break

    def on_message(
        self,
        msg_type: MessageType,
        handler: Callable[[Message], Any],
    ) -> None:
        """Register a message handler.

        Args:
            msg_type: The message type to handle
            handler: The handler function (sync or async)
        """
        if msg_type not in self._message_handlers:
            self._message_handlers[msg_type] = []
        self._message_handlers[msg_type].append(handler)

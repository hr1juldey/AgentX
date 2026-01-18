# =============================================================================
# AGENTX R013 - WebSocket Streaming Utilities
# =============================================================================
# Shared utilities for WebSocket streaming tests
# =============================================================================

import asyncio
import json

import websockets


# Constants
CHAIN_ENDPOINT = "ws://localhost:8013/api/v1/ws/travel"
STREAM_ENDPOINT = "ws://localhost:8013/api/v1/ws/travel/stream"
WORD_DELAY = 0.2


async def stream_input(ws: websockets.WebSocketClientProtocol, question: str) -> None:
    """Stream input word-by-word to simulate speech.

    Args:
        ws: WebSocket connection
        question: Question to stream
    """
    words = question.split()

    print("Streaming input...")
    for word in words:
        payload = json.dumps({"type": "chunk", "text": word + " "})
        await ws.send(payload)
        print(f"  Sent: {word}")
        await asyncio.sleep(WORD_DELAY)


async def signal_end(ws: websockets.WebSocketClientProtocol) -> None:
    """Signal end of input stream.

    Args:
        ws: WebSocket connection
    """
    payload = json.dumps({"type": "end"})
    await ws.send(payload)
    print("\nInput complete. Waiting for response...\n")


def print_header(title: str) -> None:
    """Print test header.

    Args:
        title: Test title
    """
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

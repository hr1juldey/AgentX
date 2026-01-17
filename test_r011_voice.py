#!/usr/bin/env python3
"""Test R011 backend voice WebSocket with WAV file."""

import asyncio
import base64
import websockets
import json

WAV_FILE = "/home/riju279/Documents/Code/XRIG/AgentX/silero_test.wav"
WS_URL = "ws://localhost:8011/ws/voice"


async def test_voice_websocket():
    """Test voice WebSocket with WAV file."""
    # Read WAV file
    with open(WAV_FILE, "rb") as f:
        audio_data = f.read()

    # Encode to base64
    audio_b64 = base64.b64encode(audio_data).decode()

    print(f"Audio file size: {len(audio_data)} bytes")
    print(f"Connecting to {WS_URL}...")

    try:
        async with websockets.connect(WS_URL) as ws:
            # Wait for connection message
            msg = json.loads(await ws.recv())
            print(f"Connected: {msg}")

            # Send audio chunk
            print("Sending audio chunk...")
            await ws.send(json.dumps({"type": "audio_chunk", "audio_data": audio_b64}))

            # Receive responses
            timeout = 30
            start_time = asyncio.get_event_loop().time()

            while asyncio.get_event_loop().time() - start_time < timeout:
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=30.0)
                    msg = json.loads(response)
                    print(f"\n[{msg['type']}]")

                    if msg["type"] == "transcription":
                        print(f"  Text: {msg['text']}")
                    elif msg["type"] == "response_chunk":
                        print(f"  Chunk: {msg['text']}")
                    elif msg["type"] == "audio":
                        print(f"  Audio: {len(msg['data'])} bytes")
                    elif msg["type"] == "listening":
                        print("  Ready for more input")
                        break

                except asyncio.TimeoutError:
                    print("\nNo more responses (timeout)")
                    break

    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(test_voice_websocket())

#!/usr/bin/env python3
"""E2E test script for AgentX backend divergence analysis."""

import asyncio
import json
import sys
import websockets
import uuid
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


async def test_websocket_query():
    """Test WebSocket query endpoint."""
    uri = "ws://localhost:8015/api/v1/ws"
    session_id = str(uuid.uuid4())
    query = "What is the capital of France?"

    print(f"[{datetime.now()}] Connecting to {uri}")
    print(f"[{datetime.now()}] Session ID: {session_id}")
    print(f"[{datetime.now()}] Query: {query}")

    try:
        async with websockets.connect(uri) as ws:
            # Wait for connection message
            init_msg = await ws.recv()
            print(f"[{datetime.now()}] Initial message: {init_msg}")

            # Send query message
            query_msg = {
                "message_id": str(uuid.uuid4()),
                "message_type": "query",
                "session_id": session_id,
                "timestamp": datetime.now().timestamp(),
                "data": {"query": query},
            }

            print(f"[{datetime.now()}] Sending query...")
            await ws.send(json.dumps(query_msg))

            # Receive response
            response_count = 0
            while response_count < 10:  # Limit to avoid infinite loop
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=60)
                    print(f"[{datetime.now()}] Received: {msg[:300]}...")

                    data = json.loads(msg)
                    if data.get("data", {}).get("is_complete"):
                        print(f"[{datetime.now()}] Response complete!")
                        break

                    response_count += 1
                except asyncio.TimeoutError:
                    print(f"[{datetime.now()}] Timeout waiting for response")
                    break

    except Exception as e:
        print(f"[{datetime.now()}] Error: {e}")


async def test_voice_health():
    """Test voice health endpoint."""
    import httpx

    print(f"\n[{datetime.now()}] Testing voice health endpoint...")

    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8015/api/v1/voice/kyutai/status")
        print(f"[{datetime.now()}] Voice health: {response.json()}")


async def test_thread_create():
    """Test thread creation endpoint."""
    import httpx

    print(f"\n[{datetime.now()}] Testing thread creation...")

    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8015/api/v1/threads")
        print(f"[{datetime.now()}] Thread created: {response.json()}")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("AgentX Backend E2E Test")
    print("=" * 60)

    await test_voice_health()
    await test_thread_create()
    await test_websocket_query()

    print("\n" + "=" * 60)
    print("Test complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

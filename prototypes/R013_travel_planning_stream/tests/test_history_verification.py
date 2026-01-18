#!/usr/bin/env python3
"""
Simple test to verify conversation history is working.

This test asks questions that depend on previous context.
If history is working, the agent should remember previous turns.
"""

import asyncio
import json
import websockets


STREAM_ENDPOINT = "ws://localhost:8013/api/v1/ws/travel/stream"


async def stream_input(ws, question: str) -> None:
    """Stream input word by word."""
    words = question.split()
    for word in words:
        payload = json.dumps({"type": "chunk", "text": word + " "})
        await ws.send(payload)
        await asyncio.sleep(0.05)
    await ws.send(json.dumps({"type": "end"}))


async def test_conversation_memory():
    """Test that agent remembers context from previous turns."""

    print("=" * 70)
    print("CONVERSATION MEMORY TEST")
    print("=" * 70)

    session_id = None
    questions = [
        "What are the top 3 places to visit in India?",
        "Which of those places has the best weather in January?",  # References "those places"
        "Can you suggest budget hotels specifically in the first place you mentioned?",  # References "first place"
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n[Turn {i}] {question}")
        print("-" * 60)

        # Build URL with session_id
        url = STREAM_ENDPOINT
        if session_id:
            url = f"{STREAM_ENDPOINT}?session_id={session_id}"

        try:
            async with websockets.connect(url, close_timeout=60) as ws:
                # Get session info
                msg = json.loads(await ws.recv())
                if msg.get("type") == "session":
                    session_id = msg.get("session_id")
                    turn_count = msg.get("turn_count", 0)
                    print(f"Session: {session_id} | Previous turns: {turn_count}")

                # Stream input
                await stream_input(ws, question)

                # Collect response
                response_text = []
                async for message in ws:
                    data = json.loads(message)
                    msg_type = data.get("type")

                    if msg_type == "token":
                        response_text.append(data.get("chunk", ""))

                    elif msg_type == "done":
                        full_response = "".join(response_text)
                        print(f"Response: {full_response[:300]}...")
                        break

                    elif msg_type == "error":
                        print(f"ERROR: {data.get('msg')}")
                        break

        except Exception as e:
            print(f"ERROR: {e}")

    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    print("If the agent has memory:")
    print("- Turn 2 should mention specific places from Turn 1")
    print("- Turn 3 should reference the 'first place' from Turn 1")
    print("\nIf the agent has NO memory:")
    print("- Turn 2 will give generic weather advice")
    print("- Turn 3 will ask 'which place?' or give generic hotel advice")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_conversation_memory())

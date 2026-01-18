#!/usr/bin/env python3
"""
Simple robust test for conversation history.

This test ensures session continuity by:
1. Getting session_id from first successful connection
2. Using that session_id for all subsequent connections
3. Handling connection errors gracefully
"""

import asyncio
import json
import websockets


STREAM_ENDPOINT = "ws://localhost:8013/api/v1/ws/travel/stream"


async def ask_question(
    session_id: str | None, question: str, timeout: float = 30.0
) -> tuple[str | None, str, int]:
    """Ask a single question, returning (session_id, response, turn_number)."""
    url = STREAM_ENDPOINT
    if session_id:
        url = f"{STREAM_ENDPOINT}?session_id={session_id}"

    try:
        async with websockets.connect(
            url, close_timeout=timeout, ping_timeout=timeout
        ) as ws:
            # Get session info (first message)
            msg = json.loads(await ws.recv())
            if msg.get("type") == "session":
                session_id = msg.get("session_id")

            # Stream input
            words = question.split()
            for word in words:
                await ws.send(json.dumps({"type": "chunk", "text": word + " "}))
                await asyncio.sleep(0.05)
            await ws.send(json.dumps({"type": "end"}))

            # Collect response
            response_parts = []
            final_turn = 0
            async for message in ws:
                data = json.loads(message)
                msg_type = data.get("type")

                if msg_type == "token":
                    response_parts.append(data.get("chunk", ""))

                elif msg_type == "done":
                    final_turn = data.get("turn_number", 0)
                    break

                elif msg_type == "error":
                    return session_id, f"ERROR: {data.get('msg')}", 0

            return session_id, "".join(response_parts), final_turn

    except Exception as e:
        return session_id, f"CONNECTION ERROR: {e}", 0


async def test_history():
    """Test conversation history with context-dependent questions."""

    print("=" * 70)
    print("CONVERSATION HISTORY TEST")
    print("=" * 70)

    session_id: str | None = None

    # Questions that test context memory
    questions = [
        (
            "Context setting",
            "I want to visit Goa in India. What are the top attractions there?",
        ),
        (
            "Context reference",
            "How much does it cost to visit the first attraction you mentioned?",
        ),
        (
            "Context verification",
            "Is the first attraction good for families with children?",
        ),
    ]

    for desc, question in questions:
        print(f"\n[{desc}]")
        print(f"Q: {question}")
        print("-" * 60)

        session_id, response, turn_num = await ask_question(session_id, question)
        print(f"Session: {session_id[:8]}... | Turn #{turn_num}")
        print(f"A: {response[:200]}...")

        # Brief pause between turns
        await asyncio.sleep(1)

    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    print("✅ History working if:")
    print("  - Turn 2 asks about cost of a SPECIFIC Goa attraction (not generic)")
    print("  - Turn 3 mentions a SPECIFIC attraction's family-friendliness")
    print("\n❌ History NOT working if:")
    print("  - Turn 2 says 'which attraction?' or gives generic cost info")
    print("  - Turn 3 gives generic family travel advice")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_history())

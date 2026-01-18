# =============================================================================
# AGENTX R013 - Streaming Endpoint Test
# =============================================================================
# Test the ReAct agent with dspy.streamify for real-time token streaming
# =============================================================================

import json

import websockets

from client.streaming_utils import (
    STREAM_ENDPOINT,
    print_header,
    signal_end,
    stream_input,
)


async def test_streaming_endpoint() -> None:
    """Test the ReAct agent with dspy.streamify for real-time token streaming."""
    try:
        async with websockets.connect(STREAM_ENDPOINT) as ws:
            print_header("TEST 2: ReAct Streaming (Real-time Tokens)")
            print("Connected to R013 travel planning server (streaming mode)")

            # Simulate speech stream (word by word)
            question = "What are the top places to visit in India"
            await stream_input(ws, question)

            # Signal end of input
            await signal_end(ws)

            # Receive real-time streaming response
            token_count = 0
            async for message in ws:
                data = json.loads(message)
                msg_type = data.get("type")

                if msg_type == "ack":
                    print(f"[Ack] Received {data['received']} chunks")

                elif msg_type == "status":
                    print(f"[Status] {data['msg']}")

                elif msg_type == "token":
                    # Real-time token streaming
                    token_count += 1
                    field = data.get("field", "unknown")
                    chunk = data.get("chunk", "")
                    print(
                        f"[Token #{token_count}] ({field}): {chunk}", end="", flush=True
                    )

                elif msg_type == "prediction":
                    print(f"\n\n[Final Prediction] {data['data'][:400]}...")

                elif msg_type == "done":
                    print(f"\n\n[Done] {data['final']}")
                    print(f"\nTotal tokens received: {token_count}")
                    break

                elif msg_type == "error":
                    print(f"\n[Error] {data['msg']}")
                    break

    except OSError:
        print("Error: Could not connect to server. Is it running on port 8013?")
    except Exception as e:
        print(f"Error: {e}")

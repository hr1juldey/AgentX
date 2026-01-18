# =============================================================================
# AGENTX R013 - Chain Endpoint Test
# =============================================================================
# Test the chain-based travel planning endpoint
# =============================================================================

import json

import websockets

from client.streaming_utils import (
    CHAIN_ENDPOINT,
    print_header,
    signal_end,
    stream_input,
)


async def test_chain_endpoint() -> None:
    """Test the chain-based travel planning endpoint."""
    try:
        async with websockets.connect(CHAIN_ENDPOINT) as ws:
            print_header("TEST 1: Chain-based Travel Planning")
            print("Connected to R013 travel planning server (chain mode)")

            # Simulate speech stream (word by word)
            question = "What are the top places to visit in India"
            await stream_input(ws, question)

            # Signal end of input
            await signal_end(ws)

            # Receive streaming response
            async for message in ws:
                data = json.loads(message)
                msg_type = data.get("type")

                if msg_type == "ack":
                    print(f"[Ack] Received {data['received']} chunks")

                elif msg_type == "status":
                    print(f"[Status] {data['msg']}")

                elif msg_type == "partial":
                    print(f"[Partial] {data['data'][:400]}...")

                elif msg_type == "done":
                    print(f"\n[Done] {data['final']}")
                    break

                elif msg_type == "error":
                    print(f"[Error] {data['msg']}")
                    break

    except OSError:
        print("Error: Could not connect to server. Is it running on port 8013?")
    except Exception as e:
        print(f"Error: {e}")

# =============================================================================
# AGENTX R013 - Test Client
# =============================================================================
# Tests both chain-based and streaming ReAct endpoints
# =============================================================================

import asyncio
import json

import websockets

# =============================================================================
# Test 1: Chain-based Travel Planning
# =============================================================================


async def test_chain_endpoint() -> None:
    """Test the chain-based travel planning endpoint."""
    uri = "ws://localhost:8013/api/v1/ws/travel"

    try:
        async with websockets.connect(uri) as ws:
            print("=" * 60)
            print("TEST 1: Chain-based Travel Planning")
            print("=" * 60)
            print("Connected to R013 travel planning server (chain mode)")

            # Simulate speech stream (word by word)
            question = "What are the top places to visit in India"
            words = question.split()

            print("\nStreaming input...")
            for word in words:
                payload = json.dumps({"type": "chunk", "text": word + " "})
                await ws.send(payload)
                print(f"  Sent: {word}")
                await asyncio.sleep(0.2)  # Simulate speech pace

            # Signal end of input
            payload = json.dumps({"type": "end"})
            await ws.send(payload)
            print("\nInput complete. Waiting for response...\n")

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


# =============================================================================
# Test 2: ReAct Streaming with Real-time Tokens
# =============================================================================


async def test_streaming_endpoint() -> None:
    """Test the ReAct agent with dspy.streamify for real-time token streaming."""
    uri = "ws://localhost:8013/api/v1/ws/travel/stream"

    try:
        async with websockets.connect(uri) as ws:
            print("\n" + "=" * 60)
            print("TEST 2: ReAct Streaming (Real-time Tokens)")
            print("=" * 60)
            print("Connected to R013 travel planning server (streaming mode)")

            # Simulate speech stream (word by word)
            question = "What are the top places to visit in India"
            words = question.split()

            print("\nStreaming input...")
            for word in words:
                payload = json.dumps({"type": "chunk", "text": word + " "})
                await ws.send(payload)
                print(f"  Sent: {word}")
                await asyncio.sleep(0.2)  # Simulate speech pace

            # Signal end of input
            payload = json.dumps({"type": "end"})
            await ws.send(payload)
            print("\nInput complete. Waiting for streaming response...\n")

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


# =============================================================================
# Main Menu
# =============================================================================


async def main() -> None:
    """Run test menu."""
    while True:
        print("\n" + "=" * 60)
        print("R013 Travel Planning Test Client")
        print("=" * 60)
        print("1. Test Chain-based Travel Planning")
        print("2. Test ReAct Streaming (Real-time Tokens)")
        print("3. Run Both Tests")
        print("0. Exit")
        print("=" * 60)

        choice = input("\nSelect test (0-3): ").strip()

        if choice == "1":
            await test_chain_endpoint()

        elif choice == "2":
            await test_streaming_endpoint()

        elif choice == "3":
            await test_chain_endpoint()
            await asyncio.sleep(2)  # Brief pause between tests
            await test_streaming_endpoint()

        elif choice == "0":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please select 0-3.")


if __name__ == "__main__":
    asyncio.run(main())

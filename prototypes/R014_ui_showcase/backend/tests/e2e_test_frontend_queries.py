#!/usr/bin/env python3
"""
End-to-End (E2E) Test: Simulating Human Queries from Frontend

This script tests the backend as if a human user is querying from the frontend.
Tests both REST and WebSocket endpoints with realistic user queries.
"""

import asyncio
import json
import sys
from pathlib import Path

import httpx
import websockets

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


# Backend configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test queries that simulate real human usage
HUMAN_QUERIES = [
    {
        "name": "Simple Widget Request",
        "query": "Show me a chart of Apple stock prices for the last month",
        "device_context": "desktop",
        "expected_widgets": ["chart"],
    },
    {
        "name": "Dashboard with Multiple Widgets",
        "query": "Create a dashboard showing tech company stocks: AAPL, GOOGL, MSFT",
        "device_context": "desktop",
        "expected_widgets": ["chart", "card"],
    },
    {
        "name": "Informational Query",
        "query": "What is the current state of AI adoption in healthcare?",
        "device_context": "desktop",
        "expected_widgets": ["markdown"],
    },
    {
        "name": "Mobile-Optimized Query",
        "query": "Show me the weather forecast for this week",
        "device_context": "mobile",
        "expected_widgets": ["card", "markdown"],
    },
    {
        "name": "Complex Research Query",
        "query": "Research and summarize the latest developments in quantum computing",
        "device_context": "desktop",
        "expected_widgets": ["markdown", "opengraph-card"],
    },
]


async def test_health_check() -> bool:
    """Test that the backend is running."""
    print("\n=== Test: Health Check ===")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/")
            response.raise_for_status()
            data = response.json()

            print("  ✓ Backend is running")
            print(f"    App: {data.get('app', 'Unknown')}")
            print(f"    Version: {data.get('version', 'Unknown')}")
            print(f"    Status: {data.get('status', 'Unknown')}")

            return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        print("  💡 Make sure the backend is running: python main.py")
        return False


async def test_rest_search(query: str) -> bool:
    """Test the REST search endpoint."""
    print("\n=== Test: REST Search ===")
    print(f"  Query: '{query[:60]}...'")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{API_BASE}/search",
                json={"query": query},
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            data = response.json()

            answer = data.get("answer", "")
            confidence = data.get("confidence", "unknown")

            print("  ✓ Search completed")
            print(f"    Confidence: {confidence}")
            print(f"    Answer preview: '{answer[:100]}...'")

            return True

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        return False


async def test_websocket_widget_generation(
    query: str,
    device_context: str = "desktop",
    timeout: int = 180,
) -> dict:
    """Test WebSocket widget generation with streaming."""
    print("\n=== Test: WebSocket Widget Generation ===")
    print(f"  Query: '{query[:80]}...'")
    print(f"  Device: {device_context}")
    print(f"  Timeout: {timeout}s")

    results = {
        "widgets": [],
        "qa_checkpoints": [],
        "complete": False,
        "error": None,
    }

    try:
        uri = "ws://localhost:8000/api/v1/ws/generate-widget"
        async with websockets.connect(uri, close_timeout=timeout) as ws:
            # Send request
            payload = {
                "query": query,
                "device_context": device_context,
            }
            await ws.send(json.dumps(payload))
            print("  → Request sent")

            # Receive streaming responses
            start_time = asyncio.get_event_loop().time()
            while True:
                try:
                    message = await asyncio.wait_for(
                        ws.recv(), timeout=5.0
                    )
                except asyncio.TimeoutError:
                    # Check if we've received complete signal
                    if results["complete"]:
                        break
                    # No message for 5s but not complete - check timeout
                    elapsed = asyncio.get_event_loop().time() - start_time
                    if elapsed > timeout:
                        print(f"  ⚠ Timeout after {elapsed:.1f}s")
                        break
                    continue

                data = json.loads(message)
                msg_type = data.get("type", "unknown")

                if msg_type == "widget":
                    widget = data.get("data", {})
                    widget_type = widget.get("type", widget.get("descriptor_type", "unknown"))
                    results["widgets"].append(widget)
                    print(f"  📦 Widget: {widget_type}")

                elif msg_type == "qa_progress":
                    checkpoint = data.get("data", {}).get("checkpoint", "unknown")
                    status = data.get("data", {}).get("status", "unknown")
                    results["qa_checkpoints"].append(checkpoint)
                    print(f"  ✓ QA: [{checkpoint}] {status}")

                elif msg_type == "complete":
                    results["complete"] = True
                    delivery_plan = data.get("data", {}).get("delivery_plan", {})
                    widgets = delivery_plan.get("widgets", [])
                    print(f"  ✅ Complete! Total widgets: {len(widgets)}")
                    break

                elif msg_type == "error":
                    error_msg = data.get("message", "Unknown error")
                    results["error"] = error_msg
                    print(f"  ✗ Error: {error_msg}")
                    break

    except websockets.exceptions.WebSocketException as e:
        results["error"] = str(e)
        print(f"  ✗ WebSocket error: {e}")
    except Exception as e:
        results["error"] = str(e)
        print(f"  ✗ FAILED: {e}")

    # Print summary
    print("\n  Summary:")
    print(f"    Widgets received: {len(results['widgets'])}")
    print(f"    QA checkpoints: {len(results['qa_checkpoints'])}")
    print(f"    Complete: {results['complete']}")
    if results['error']:
        print(f"    Error: {results['error']}")

    return results


async def test_websocket_search(query: str, max_hops: int = 3, timeout: int = 120) -> dict:
    """Test WebSocket search with streaming."""
    print("\n=== Test: WebSocket Multi-Hop Search ===")
    print(f"  Query: '{query[:80]}...'")
    print(f"  Max hops: {max_hops}")
    print(f"  Timeout: {timeout}s")

    results = {
        "hop_events": [],
        "final_result": None,
        "complete": False,
        "error": None,
    }

    try:
        uri = "ws://localhost:8000/api/v1/ws/search"
        async with websockets.connect(uri, close_timeout=timeout) as ws:
            # Send request
            payload = {
                "query": query,
                "max_hops": max_hops,
            }
            await ws.send(json.dumps(payload))
            print("  → Request sent")

            # Receive streaming responses
            start_time = asyncio.get_event_loop().time()
            while True:
                try:
                    message = await asyncio.wait_for(
                        ws.recv(), timeout=5.0
                    )
                except asyncio.TimeoutError:
                    if results["complete"]:
                        break
                    elapsed = asyncio.get_event_loop().time() - start_time
                    if elapsed > timeout:
                        print(f"  ⚠ Timeout after {elapsed:.1f}s")
                        break
                    continue

                data = json.loads(message)
                msg_type = data.get("type", "unknown")

                if msg_type == "hop_event":
                    event = data.get("data", {})
                    hop = event.get("hop", "?")
                    results["hop_events"].append(event)
                    print(f"  → Hop {hop}: {event.get('status', 'processing')}")

                elif msg_type == "final_result":
                    results["complete"] = True
                    results["final_result"] = data.get("data", {})
                    answer = results["final_result"].get("answer", "")[:100]
                    print(f"  ✅ Complete! Answer: '{answer}...'")
                    break

                elif msg_type == "error":
                    error_msg = data.get("message", "Unknown error")
                    results["error"] = error_msg
                    print(f"  ✗ Error: {error_msg}")
                    break

    except websockets.exceptions.WebSocketException as e:
        results["error"] = str(e)
        print(f"  ✗ WebSocket error: {e}")
    except Exception as e:
        results["error"] = str(e)
        print(f"  ✗ FAILED: {e}")

    # Print summary
    print("\n  Summary:")
    print(f"    Hop events: {len(results['hop_events'])}")
    print(f"    Complete: {results['complete']}")
    if results['error']:
        print(f"    Error: {results['error']}")

    return results


async def run_e2e_tests():
    """Run all E2E tests simulating human frontend queries."""
    print("=" * 70)
    print("E2E TEST: Simulating Human Queries from Frontend")
    print("=" * 70)
    print(f"\nBackend URL: {BASE_URL}")

    # First check if backend is running
    if not await test_health_check():
        print("\n❌ Cannot proceed - backend is not running!")
        print("\n💡 Start the backend with:")
        print("   cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend")
        print("   python main.py")
        return False

    results = {
        "passed": 0,
        "failed": 0,
        "tests": [],
    }

    # Test 1: REST Search endpoint
    print("\n" + "=" * 70)
    print("TEST SUITE 1: REST Search Endpoint")
    print("=" * 70)

    test_result = await test_rest_search(
        "What are the latest developments in AI?"
    )
    if test_result:
        results["passed"] += 1
        results["tests"].append(("REST Search", "PASSED"))
    else:
        results["failed"] += 1
        results["tests"].append(("REST Search", "FAILED"))

    # Test 2: WebSocket Widget Generation (simple query)
    print("\n" + "=" * 70)
    print("TEST SUITE 2: WebSocket Widget Generation")
    print("=" * 70)

    widget_result = await test_websocket_widget_generation(
        query="Show me a chart with recent tech stock prices",
        device_context="desktop",
        timeout=120,
    )

    if widget_result["complete"] and len(widget_result["widgets"]) > 0:
        results["passed"] += 1
        results["tests"].append(("Widget Generation", "PASSED"))
    else:
        results["failed"] += 1
        results["tests"].append(("Widget Generation", "FAILED"))

    # Test 3: WebSocket Search (multi-hop)
    print("\n" + "=" * 70)
    print("TEST SUITE 3: WebSocket Multi-Hop Search")
    print("=" * 70)

    search_result = await test_websocket_search(
        query="What is the economic impact of climate change?",
        max_hops=2,  # Use 2 hops for faster testing
        timeout=120,
    )

    if search_result["complete"]:
        results["passed"] += 1
        results["tests"].append(("Multi-Hop Search", "PASSED"))
    else:
        results["failed"] += 1
        results["tests"].append(("Multi-Hop Search", "FAILED"))

    # Print final summary
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)

    for test_name, status in results["tests"]:
        symbol = "✓" if status == "PASSED" else "✗"
        print(f"{symbol} {test_name}: {status}")

    print(f"\nTotal: {results['passed']} passed, {results['failed']} failed")

    return results["failed"] == 0


if __name__ == "__main__":
    try:
        success = asyncio.run(run_e2e_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Tests interrupted by user")
        sys.exit(1)

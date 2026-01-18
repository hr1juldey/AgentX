# =============================================================================
# AGENTX R013 - Test Client Main
# =============================================================================
# Menu-driven test client for R013 travel planning endpoints
# =============================================================================

import asyncio

from client.chain_test import test_chain_endpoint
from client.streaming_test import test_streaming_endpoint


def print_menu() -> None:
    """Print test menu."""
    print("\n" + "=" * 60)
    print("R013 Travel Planning Test Client")
    print("=" * 60)
    print("1. Test Chain-based Travel Planning")
    print("2. Test ReAct Streaming (Real-time Tokens)")
    print("3. Run Both Tests")
    print("0. Exit")
    print("=" * 60)


async def run_tests(choice: str) -> bool:
    """Run selected test(s).

    Args:
        choice: User's menu choice

    Returns:
        False if user wants to exit, True otherwise
    """
    if choice == "1":
        await test_chain_endpoint()

    elif choice == "2":
        await test_streaming_endpoint()

    elif choice == "3":
        await test_chain_endpoint()
        await asyncio.sleep(2)
        await test_streaming_endpoint()

    elif choice == "0":
        print("Exiting...")
        return False

    else:
        print("Invalid choice. Please select 0-3.")

    return True


async def main() -> None:
    """Run test menu."""
    while True:
        print_menu()
        choice = input("\nSelect test (0-3): ").strip()

        should_continue = await run_tests(choice)
        if not should_continue:
            break


if __name__ == "__main__":
    asyncio.run(main())

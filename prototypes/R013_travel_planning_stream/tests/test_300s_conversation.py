#!/usr/bin/env python3
"""
R013 Extended Conversation Test
Tests the full 300-second conversation flow per plan requirements.

Conversation Flow (from plan):
1. Top places inquiry
2. Details inquiry (festivals/activities)
3. Sub-regions (popular vs hidden gems)
4. Transport options
5. Banter phase (negotiate food, transport, lodging with budget/constraints)
6. Variations
7. Headcount change (forces replanning)
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import websockets


STREAM_ENDPOINT = "ws://localhost:8013/api/v1/ws/travel/stream"


@dataclass
class ConversationTurn:
    """Single conversation turn."""

    turn_number: int
    question: str
    success: bool = False
    duration: float = 0.0
    token_count: int = 0
    response_preview: str = ""
    error_message: str | None = None


@dataclass
class ConversationSummary:
    """Summary of full conversation."""

    total_turns: int = 0
    total_duration: float = 0.0
    successful_turns: int = 0
    total_tokens: int = 0
    conversation_log: list[ConversationTurn] = field(default_factory=list)

    def __str__(self) -> str:
        success_rate = (
            (self.successful_turns / self.total_turns * 100) if self.total_turns else 0
        )
        return f"""
Conversation Summary
====================
Total Turns:      {self.total_turns}
Successful:       {self.successful_turns} ({success_rate:.1f}%)
Total Duration:   {self.total_duration:.1f}s ({self.total_duration / 60:.1f} minutes)
Total Tokens:     {self.total_tokens}
Avg Tokens/Turn:  {self.total_tokens / self.total_turns if self.total_turns else 0:.0f}
"""


class ExtendedConversationTest:
    """Test extended 300-second conversation flow."""

    def __init__(self, max_duration_seconds: int = 300):
        self.max_duration = max_duration_seconds
        self.summary = ConversationSummary()
        self.start_time = 0.0

        # Conversation flow from plan
        self.conversation_script = [
            # Phase 1: Initial inquiry
            "What are the top places to visit in India as of January 2026?",
            # Phase 2: Details inquiry
            "What should I see there? What festivals and activities are currently going on?",
            # Phase 3: Sub-regions
            "Which regions are most popular vs hidden gems that nobody visits?",
            # Phase 4: Transport
            "What transport options are available?",
            # Phase 5: Banter phase - budget constraint
            "I have a limited budget of 50000 INR. Can you suggest affordable options?",
            # Phase 5: Banter phase - food preferences
            "I'm vegetarian and prefer local street food. Any recommendations?",
            # Phase 5: Banter phase - lodging
            "What about budget-friendly homestays or hostels instead of hotels?",
            # Phase 6: Variations
            "Can you suggest variations of this plan for a solo female traveler?",
            # Phase 7: Headcount change (critical - forces replanning)
            "Actually, my group size just changed from 2 people to 6 people. Can you replan everything?",
            # Follow-up on headcount change
            "With 6 people, how does this affect our transportation and lodging options?",
        ]

    async def stream_input(self, ws: Any, question: str) -> None:
        """Stream input word by word to simulate speech."""
        words = question.split()
        for i, word in enumerate(words):
            chunk_delay = 0.1 if i < len(words) - 1 else 0
            payload = json.dumps({"type": "chunk", "text": word + " "})
            await ws.send(payload)
            await asyncio.sleep(chunk_delay)
        await ws.send(json.dumps({"type": "end"}))

    async def ask_question(self, turn_number: int, question: str) -> ConversationTurn:
        """Ask a single question in the conversation."""
        turn = ConversationTurn(turn_number=turn_number, question=question)
        start = time.time()

        print(f"\n[Turn {turn_number}]")
        print("-" * 60)
        print(f"Question: {question}")

        try:
            async with websockets.connect(STREAM_ENDPOINT, close_timeout=300) as ws:
                # Stream input
                await self.stream_input(ws, question)

                # Collect response
                token_count = 0
                response_parts = []

                async for message in ws:
                    data = json.loads(message)
                    msg_type = data.get("type")

                    if msg_type == "token":
                        token_count += 1
                        chunk = data.get("chunk", "")
                        response_parts.append(chunk)

                    elif msg_type == "done":
                        turn.success = True
                        turn.duration = time.time() - start
                        turn.token_count = token_count
                        turn.response_preview = "".join(response_parts)[:200]
                        break

                    elif msg_type == "error":
                        turn.error_message = data.get("msg")
                        turn.duration = time.time() - start
                        break

        except Exception as e:
            turn.error_message = str(e)
            turn.duration = time.time() - start

        # Display result
        if turn.success:
            print(
                f"✓ Response received ({turn.duration:.1f}s, {turn.token_count} tokens)"
            )
            print(f"Preview: {turn.response_preview}...")
        else:
            print(f"✗ Error: {turn.error_message}")

        return turn

    async def run_conversation(self) -> None:
        """Run the full conversation flow."""
        self.start_time = time.time()

        print("=" * 70)
        print("R013 Extended Conversation Test (300-second)")
        print("=" * 70)
        print(
            f"Max Duration: {self.max_duration} seconds ({self.max_duration / 60:.1f} minutes)"
        )
        print(f"Questions: {len(self.conversation_script)}")
        print("=" * 70)

        for i, question in enumerate(self.conversation_script, 1):
            # Check time limit
            elapsed = time.time() - self.start_time
            if elapsed >= self.max_duration:
                print(f"\n⏱ Time limit reached ({elapsed:.1f}s)")
                break

            print(f"\n[Elapsed: {elapsed:.1f}s / {self.max_duration}s]")

            # Ask question
            turn = await self.ask_question(i, question)
            self.summary.conversation_log.append(turn)

            # Update summary
            self.summary.total_turns += 1
            if turn.success:
                self.summary.successful_turns += 1
                self.summary.total_tokens += turn.token_count
            self.summary.total_duration = time.time() - self.start_time

            # Brief pause between turns
            await asyncio.sleep(1)

        # Final summary
        print("\n" + "=" * 70)
        print("CONVERSATION COMPLETE")
        print("=" * 70)
        print(str(self.summary))

    def save_results(self) -> None:
        """Save conversation results to file."""
        output_dir = Path("test_results")
        output_dir.mkdir(exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"r013_conversation_{timestamp}.json"

        data = {
            "metadata": {
                "max_duration_seconds": self.max_duration,
                "actual_duration_seconds": self.summary.total_duration,
                "timestamp": timestamp,
                "endpoint": STREAM_ENDPOINT,
            },
            "summary": {
                "total_turns": self.summary.total_turns,
                "successful_turns": self.summary.successful_turns,
                "total_duration": self.summary.total_duration,
                "total_tokens": self.summary.total_tokens,
                "success_rate": (
                    self.summary.successful_turns / self.summary.total_turns * 100
                    if self.summary.total_turns
                    else 0
                ),
            },
            "turns": [
                {
                    "turn_number": t.turn_number,
                    "question": t.question,
                    "success": t.success,
                    "duration": t.duration,
                    "token_count": t.token_count,
                    "response_preview": t.response_preview,
                    "error_message": t.error_message,
                }
                for t in self.summary.conversation_log
            ],
        }

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        print(f"\nResults saved to: {output_file}")

    def print_detailed_log(self) -> None:
        """Print detailed conversation log."""
        print("\n" + "=" * 70)
        print("DETAILED CONVERSATION LOG")
        print("=" * 70)

        for turn in self.summary.conversation_log:
            status = "✅" if turn.success else "❌"
            print(
                f"\n[{status}] Turn {turn.turn_number} ({turn.duration:.1f}s, {turn.token_count} tokens)"
            )
            print(f"Q: {turn.question}")
            if turn.success:
                print(f"A: {turn.response_preview}...")
            else:
                print(f"ERROR: {turn.error_message}")


async def main() -> None:
    """Run extended conversation test."""
    import sys

    # Parse max duration from command line
    max_duration = 300
    if len(sys.argv) > 1:
        try:
            max_duration = int(sys.argv[1])
        except ValueError:
            pass

    tester = ExtendedConversationTest(max_duration_seconds=max_duration)
    await tester.run_conversation()
    tester.print_detailed_log()
    tester.save_results()


if __name__ == "__main__":
    asyncio.run(main())

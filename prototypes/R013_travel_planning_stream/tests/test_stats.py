#!/usr/bin/env python3
"""
R013 Statistical Testing Suite
Run multiple iterations to capture performance trends and behavior patterns.
"""

import asyncio
import json
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import websockets


STREAM_ENDPOINT = "ws://localhost:8013/api/v1/ws/travel/stream"


@dataclass
class TestResult:
    """Single test result."""

    iteration: int
    question: str
    success: bool = False
    duration: float = 0.0
    token_count: int = 0
    first_token_time: float | None = None
    error_message: str | None = None
    tool_calls: int = 0
    search_used: bool = False


@dataclass
class TestStats:
    """Aggregated statistics across all runs."""

    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    avg_duration: float = 0.0
    avg_tokens: float = 0.0
    avg_first_token: float = 0.0
    success_rate: float = 0.0
    tool_call_rate: float = 0.0
    search_rate: float = 0.0

    def __str__(self) -> str:
        return f"""
Test Statistics
===============
Total Runs:      {self.total_runs}
Successful:      {self.successful_runs} ({self.success_rate:.1f}%)
Failed:          {self.failed_runs}

Duration (avg):  {self.avg_duration:.2f}s
Tokens (avg):    {self.avg_tokens:.0f}
First Token:     {self.avg_first_token:.2f}s
Tool Calls (avg):{self.tool_call_rate:.1f} / run
Search Used:     {self.search_rate:.1f}% of runs
"""


class StatisticalTestRunner:
    """Run statistical tests on R013 streaming endpoint."""

    def __init__(self, iterations: int = 30):
        self.iterations = iterations
        self.results: list[TestResult] = []
        self.questions = [
            "What are the top places to visit in India",
            "What festivals and activities are currently going on there",
            "Which regions are most popular vs hidden gems",
            "What transport options are available",
        ]

    async def stream_input(self, ws: Any, question: str) -> None:
        """Stream input word by word to simulate speech."""
        words = question.split()
        for word in words:
            payload = json.dumps({"type": "chunk", "text": word + " "})
            await ws.send(payload)
            await asyncio.sleep(0.1)
        await ws.send(json.dumps({"type": "end"}))

    async def run_single_test(self, iteration: int, question: str) -> TestResult:
        """Run a single test and collect metrics."""
        result = TestResult(iteration=iteration, question=question)
        start_time = time.time()
        first_token_time = None

        try:
            async with websockets.connect(STREAM_ENDPOINT) as ws:
                # Stream input
                await self.stream_input(ws, question)

                # Collect metrics
                token_count = 0
                tool_calls = 0
                search_used = False

                async for message in ws:
                    data = json.loads(message)
                    msg_type = data.get("type")

                    if msg_type == "token":
                        token_count += 1
                        if first_token_time is None:
                            first_token_time = time.time() - start_time

                    elif msg_type == "done":
                        result.success = True
                        result.duration = time.time() - start_time
                        result.token_count = token_count
                        result.first_token_time = first_token_time
                        result.tool_calls = tool_calls
                        result.search_used = search_used
                        break

                    elif msg_type == "error":
                        result.error_message = data.get("msg")
                        result.duration = time.time() - start_time
                        break

        except Exception as e:
            result.error_message = str(e)
            result.duration = time.time() - start_time

        return result

    async def run_all_tests(self) -> None:
        """Run all test iterations."""
        print(f"Running {self.iterations} iterations of statistical tests...")
        print("=" * 70)

        for i in range(self.iterations):
            # Cycle through questions
            question = self.questions[i % len(self.questions)]

            result = await self.run_single_test(i + 1, question)
            self.results.append(result)

            # Progress indicator
            status = "✅" if result.success else "❌"
            tokens = result.token_count if result.success else "ERR"
            duration = f"{result.duration:.1f}s"
            token_str = f"{tokens}" if isinstance(tokens, int) else tokens
            print(
                f"[{i + 1:3d}/{self.iterations}] {status} | {token_str:>4} tokens | {duration:>6} | {question[:40]}..."
            )

            # Brief pause between runs
            await asyncio.sleep(0.5)

    def calculate_stats(self) -> TestStats:
        """Calculate aggregated statistics."""
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]

        stats = TestStats(
            total_runs=len(self.results),
            successful_runs=len(successful),
            failed_runs=len(failed),
        )

        if successful:
            stats.avg_duration = statistics.mean(r.duration for r in successful)
            stats.avg_tokens = statistics.mean(r.token_count for r in successful)
            stats.avg_first_token = statistics.mean(
                r.first_token_time for r in successful if r.first_token_time
            )
            stats.success_rate = (len(successful) / len(self.results)) * 100
            stats.tool_call_rate = statistics.mean(r.tool_calls for r in successful)
            stats.search_rate = (
                sum(1 for r in successful if r.search_used) / len(successful)
            ) * 100

        return stats

    def print_detailed_results(self) -> None:
        """Print detailed results table."""
        print("\n" + "=" * 70)
        print("DETAILED RESULTS")
        print("=" * 70)
        print(
            f"{'Iter':>4} | {'Status':^6} | {'Tokens':>6} | {'Duration':>8} | {'First Token':>10} | {'Question':^30}"
        )
        print("-" * 70)

        for r in self.results:
            status = "✅ OK" if r.success else "❌ ERR"
            tokens = f"{r.token_count}" if r.success else "N/A"
            duration = f"{r.duration:.2f}s"
            first_token = f"{r.first_token_time:.2f}s" if r.first_token_time else "N/A"
            question = r.question[:28] + ".." if len(r.question) > 30 else r.question

            print(
                f"{r.iteration:>4} | {status:^6} | {tokens:>6} | {duration:>8} | {first_token:>10} | {question:^30}"
            )

    def save_results(self) -> None:
        """Save results to JSON file."""
        output_dir = Path("test_results")
        output_dir.mkdir(exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"r013_stats_{timestamp}.json"

        data = {
            "metadata": {
                "iterations": self.iterations,
                "timestamp": timestamp,
                "endpoint": STREAM_ENDPOINT,
            },
            "results": [
                {
                    "iteration": r.iteration,
                    "question": r.question,
                    "success": r.success,
                    "duration": r.duration,
                    "token_count": r.token_count,
                    "first_token_time": r.first_token_time,
                    "error_message": r.error_message,
                    "tool_calls": r.tool_calls,
                    "search_used": r.search_used,
                }
                for r in self.results
            ],
        }

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        print(f"\nResults saved to: {output_file}")


async def main() -> None:
    """Run statistical tests."""
    import sys

    # Parse iterations from command line
    iterations = 30
    if len(sys.argv) > 1:
        try:
            iterations = int(sys.argv[1])
        except ValueError:
            pass

    runner = StatisticalTestRunner(iterations=iterations)
    await runner.run_all_tests()

    # Calculate and display statistics
    stats = runner.calculate_stats()
    print("\n" + "=" * 70)
    print(str(stats))

    # Detailed results
    runner.print_detailed_results()

    # Save results
    runner.save_results()

    # Additional analysis
    if stats.successful_runs > 0:
        print("\n" + "=" * 70)
        print("TREND ANALYSIS")
        print("=" * 70)

        successful = [r for r in runner.results if r.success]
        durations = [r.duration for r in successful]
        tokens = [r.token_count for r in successful]

        if len(durations) > 1:
            print(f"Duration Std Dev:  {statistics.stdev(durations):.2f}s")
            print(f"Duration Range:    {min(durations):.2f}s - {max(durations):.2f}s")
            print(f"Duration Median:   {statistics.median(durations):.2f}s")

        if len(tokens) > 1:
            print(f"Tokens Std Dev:    {statistics.stdev(tokens):.0f}")
            print(f"Tokens Range:      {min(tokens)} - {max(tokens)}")
            print(f"Tokens Median:     {statistics.median(tokens):.0f}")


if __name__ == "__main__":
    asyncio.run(main())

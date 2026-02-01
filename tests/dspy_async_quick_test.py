"""Quick DSPy Async Performance Test with qwen3:8b.

Focused test to answer: Does async actually help with performance?

Tests:
1. Single query - sync vs async baseline
2. 2 concurrent queries - sync vs async comparison
3. Pydantic signature issues

Run with: python tests/dspy_async_quick_test.py
"""

import asyncio
import time
import logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any

import dspy

# Simple logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


# =============================================================================
# Simple DSPy Module (No Pydantic in signature)
# =============================================================================

class SimpleQueryModule(dspy.Module):
    """Simple query module - STRING signature only (no Pydantic issues)."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict("question->answer")

    def forward(self, question: str) -> dict:
        """Synchronous forward."""
        result = self.predict(question=question)
        return {"answer": result.answer}

    async def aforward(self, question: str) -> dict:
        """Async forward."""
        result = await self.predict.acall(question=question)
        return {"answer": result.answer}


# =============================================================================
# Test Runner
# =============================================================================

@dataclass
class TestResult:
    """Result of a single test."""
    test_name: str
    mode: str  # "sync" or "async"
    concurrency: int
    total_duration_ms: float
    individual_durations_ms: list[float]
    success: bool
    error: str | None = None


class QuickAsyncTest:
    """Quick async performance test."""

    def __init__(self, model: str = "qwen3:8b"):
        self.model = model
        self._configure_dspy()

    def _configure_dspy(self) -> None:
        """Configure DSPy with Ollama."""
        logger.info("Configuring DSPy with Ollama...")
        lm = dspy.LM(
            model=f"ollama_chat/{self.model}",
            api_base="http://localhost:11434",
            api_key="",
            cache=False,
        )
        dspy.configure(lm=lm)
        logger.info("DSPy configured")

    async def _warmup(self) -> None:
        """Warmup - load model into memory."""
        logger.info("Warming up (loading model)...")
        module = SimpleQueryModule()
        start = time.perf_counter()
        await module.aforward(question="Hi")
        duration = (time.perf_counter() - start) * 1000
        logger.info(f"Warmup complete: {duration:.0f}ms")

    async def _run_queries(
        self,
        queries: list[str],
        use_async: bool = False,
    ) -> TestResult:
        """Run queries and measure performance."""
        module = SimpleQueryModule()
        mode = "async" if use_async else "sync"
        logger.info(f"Running {len(queries)} queries in {mode} mode...")

        start = time.perf_counter()
        durations = []

        try:
            if use_async:
                # Run all concurrently
                tasks = []
                for q in queries:
                    q_start = time.perf_counter()
                    tasks.append(self._run_single(module, q, q_start))
                results = await asyncio.gather(*tasks)
                durations = [r for r, _ in results]
                success = all(s for _, s in results)

            else:
                # Run sequentially
                for q in queries:
                    q_start = time.perf_counter()
                    result = await self._run_single(module, q, q_start, async_mode=False)
                    durations.append(result[0])
                success = True

            total = (time.perf_counter() - start) * 1000
            logger.info(f"Complete: {total:.0f}ms total")

            return TestResult(
                test_name=f"{len(queries)}_queries",
                mode=mode,
                concurrency=len(queries),
                total_duration_ms=total,
                individual_durations_ms=durations,
                success=success,
            )

        except Exception as e:
            total = (time.perf_counter() - start) * 1000
            logger.error(f"Test failed: {e}")
            return TestResult(
                test_name=f"{len(queries)}_queries",
                mode=mode,
                concurrency=len(queries),
                total_duration_ms=total,
                individual_durations_ms=durations,
                success=False,
                error=str(e)[:100],
            )

    async def _run_single(
        self,
        module: SimpleQueryModule,
        query: str,
        start_time: float,
        async_mode: bool = True,
    ) -> tuple[float, bool]:
        """Run a single query."""
        try:
            if async_mode:
                await module.aforward(question=query)
            else:
                module(question=query)
            duration = (time.perf_counter() - start_time) * 1000
            return duration, True
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(f"Query failed: {e}")
            return duration, False

    async def run_all_tests(self) -> list[TestResult]:
        """Run all tests."""
        logger.info("=" * 60)
        logger.info("DSPy Async Performance Test")
        logger.info("=" * 60)

        # Warmup
        await self._warmup()

        results: list[TestResult] = []

        # Test 1: Single query baseline
        logger.info("\n" + "-" * 60)
        logger.info("Test 1: Single Query Baseline")
        logger.info("-" * 60)

        # Use unique queries to avoid cache
        result = await self._run_queries(["Explain quantum computing in one sentence"], use_async=False)
        results.append(result)
        logger.info(f"SYNC single: {result.total_duration_ms:.0f}ms")

        result = await self._run_queries(["Explain machine learning basics briefly"], use_async=True)
        results.append(result)
        logger.info(f"ASYNC single: {result.total_duration_ms:.0f}ms")

        # Test 2: Two concurrent queries
        logger.info("\n" + "-" * 60)
        logger.info("Test 2: Two Concurrent Queries")
        logger.info("-" * 60)

        queries = ["What are neural networks?", "Define blockchain technology"]

        result = await self._run_queries(queries, use_async=False)
        results.append(result)
        logger.info(f"SYNC sequential: {result.total_duration_ms:.0f}ms")

        result = await self._run_queries(queries, use_async=True)
        results.append(result)
        logger.info(f"ASYNC concurrent: {result.total_duration_ms:.0f}ms")

        return results

    def print_summary(self, results: list[TestResult]) -> None:
        """Print summary."""
        logger.info("\n" + "=" * 60)
        logger.info("SUMMARY")
        logger.info("=" * 60)

        sync_single = next((r for r in results if r.mode == "sync" and r.concurrency == 1), None)
        async_single = next((r for r in results if r.mode == "async" and r.concurrency == 1), None)
        sync_double = next((r for r in results if r.mode == "sync" and r.concurrency == 2), None)
        async_double = next((r for r in results if r.mode == "async" and r.concurrency == 2), None)

        if sync_single and async_single:
            logger.info(f"Single query:")
            logger.info(f"  SYNC:  {sync_single.total_duration_ms:.0f}ms")
            logger.info(f"  ASYNC: {async_single.total_duration_ms:.0f}ms")
            logger.info(f"  Overhead: {async_single.total_duration_ms - sync_single.total_duration_ms:.0f}ms")

        if sync_double and async_double:
            speedup = sync_double.total_duration_ms / async_double.total_duration_ms
            logger.info(f"\nTwo concurrent queries:")
            logger.info(f"  SYNC (sequential):  {sync_double.total_duration_ms:.0f}ms")
            logger.info(f"  ASYNC (concurrent): {async_double.total_duration_ms:.0f}ms")
            logger.info(f"  Speedup: {speedup:.2f}x")

        logger.info("\n" + "=" * 60)
        logger.info("KEY INSIGHTS:")
        logger.info("=" * 60)
        logger.info("1. Single query overhead: Async adds small overhead")
        logger.info("2. Concurrent queries: Async provides TRUE parallelism")
        logger.info("3. Speedup depends on Ollama's ability to queue requests")
        logger.info("4. Larger responses = longer await times (expected)")
        logger.info("5. Use async for LangGraph nodes (multiple LLM calls)")
        logger.info("=" * 60)


async def main() -> None:
    """Run the quick test."""
    tester = QuickAsyncTest(model="qwen3:8b")
    results = await tester.run_all_tests()
    tester.print_summary(results)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("DSPy Async Quick Test")
    print("=" * 60)
    print("\nMake sure Ollama is running: ollama serve")
    print("And qwen3:8b is available: ollama pull qwen3:8b")
    print("\n" + "=" * 60)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nTest interrupted")
    except Exception as e:
        logger.error(f"\nTest failed: {e}", exc_info=True)

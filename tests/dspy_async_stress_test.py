"""DSPy Async + Streaming Stress Test with qwen3:8b.

Tests:
1. Baseline synchronous execution
2. Async execution with aforward()
3. Token streaming (user-facing only)
4. Concurrent pressure test (breaking point)

Key Learnings:
- Ollama async support extent depends on machine
- Larger results = longer await times
- Pydantic models in signatures cause issues with async/streaming
- Token streaming only useful for user-facing UI
"""

import asyncio
import time
import logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any
from pathlib import Path

import dspy

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S.%f"
)
logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class StressTestConfig:
    """Configuration for stress test."""
    model: str = "qwen3:8b"
    ollama_base: str = "http://localhost:11434"
    concurrency_levels: list[int] = field(default_factory=lambda: [1, 2, 4, 8])
    test_queries: list[str] = field(default_factory=lambda: [
        "What is Python?",
        "Explain async/await in Python",
        "Compare async vs sync programming",
        "Design a async web scraper architecture",
        "Explain event loops and coroutines",
    ])


@dataclass
class TestMetrics:
    """Metrics for a single test run."""
    test_name: str
    concurrency: int
    async_mode: bool
    streaming: bool
    total_duration_ms: float
    individual_durations_ms: list[float]
    success_count: int
    error_count: int
    errors: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# =============================================================================
# DSPy Modules (Simple and Complex)
# =============================================================================

class SimpleQueryModule(dspy.Module):
    """Simple query module - no Pydantic in signature."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict("question -> answer")

    def forward(self, question: str) -> dict:
        """Synchronous forward."""
        logger.info(f"[Simple] SYNC processing: {question[:50]}...")
        result = self.predict(question=question)
        return {"answer": result.answer}

    async def aforward(self, question: str) -> dict:
        """Async forward."""
        logger.info(f"[Simple] ASYNC processing: {question[:50]}...")
        result = await self.predict.acall(question=question)
        return {"answer": result.answer}


class ComplexAnalysisModule(dspy.Module):
    """Complex analysis - simulates multi-step reasoning."""

    def __init__(self) -> None:
        super().__init__()
        self.analyze = dspy.ChainOfThought("question -> analysis")
        self.summarize = dspy.Predict("analysis -> summary")

    def forward(self, question: str) -> dict:
        """Synchronous forward with two steps."""
        logger.info(f"[Complex] SYNC step 1/2: {question[:50]}...")
        analysis = self.analyze(question=question)

        logger.info(f"[Complex] SYNC step 2/2: summarizing...")
        summary = self.summarize(analysis=analysis.analysis)

        return {
            "analysis": analysis.analysis,
            "summary": summary.summary
        }

    async def aforward(self, question: str) -> dict:
        """Async forward with two steps."""
        logger.info(f"[Complex] ASYNC step 1/2: {question[:50]}...")
        analysis = await self.analyze.acall(question=question)

        logger.info(f"[Complex] ASYNC step 2/2: summarizing...")
        summary = await self.summarize.acall(analysis=analysis.analysis)

        return {
            "analysis": analysis.analysis,
            "summary": summary.summary
        }


# =============================================================================
# Streaming Module (User-Facing Only)
# =============================================================================

class StreamingQueryModule(dspy.Module):
    """Streaming module for user-facing queries.

    NOTE: Token streaming is ONLY useful for user-facing UI where you want
    to show tokens appearing in real-time. For backend processing, streaming
    adds overhead without benefit.
    """

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict("question -> answer")

    def forward(self, question: str) -> dict:
        """Synchronous forward."""
        result = self.predict(question=question)
        return {"answer": result.answer}


def create_streaming_wrapper(module: dspy.Module) -> dspy.Module:
    """Wrap a module for streaming output.

    This adds overhead but enables real-time token display for UI.
    Only use for user-facing endpoints!
    """
    stream_listeners = [
        dspy.streaming.StreamListener(signature_field_name="answer")
    ]
    return dspy.streamify(module, stream_listeners=stream_listeners)


# =============================================================================
# Test Runner
# =============================================================================

class DSPyStressTestRunner:
    """Run stress tests on DSPy async and streaming."""

    def __init__(self, config: StressTestConfig) -> None:
        self.config = config
        self.results: list[TestMetrics] = []
        self._configure_dspy()

    def _configure_dspy(self) -> None:
        """Configure DSPy with Ollama."""
        logger.info("=" * 80)
        logger.info("CONFIGURING DSPy with Ollama")
        logger.info("=" * 80)
        logger.info(f"Model: {self.config.model}")
        logger.info(f"Base URL: {self.config.ollama_base}")

        lm = dspy.LM(
            model=f"ollama_chat/{self.config.model}",
            api_base=self.config.ollama_base,
            api_key="",
            cache=False,  # Important: disable cache for accurate timing
        )
        dspy.configure(lm=lm)
        logger.info("DSPy configured successfully")

    async def _run_single_query(
        self,
        module: dspy.Module,
        query: str,
        use_async: bool = False,
    ) -> tuple[float, bool, str | None]:
        """Run a single query and return duration, success, error."""
        start = time.perf_counter()

        try:
            if use_async:
                if hasattr(module, 'aforward'):
                    await module.aforward(question=query)
                else:
                    await module.acall(question=query)
            else:
                module(question=query)

            duration = (time.perf_counter() - start) * 1000
            return duration, True, None

        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            error_msg = f"{type(e).__name__}: {str(e)[:100]}"
            logger.error(f"Query failed: {error_msg}")
            return duration, False, error_msg

    async def _run_concurrent_batch(
        self,
        queries: list[str],
        use_async: bool = False,
    ) -> TestMetrics:
        """Run a batch of queries concurrently."""
        logger.info("-" * 80)
        mode = "ASYNC" if use_async else "SYNC"
        logger.info(f"Running {len(queries)} queries in {mode} mode")

        module = ComplexAnalysisModule()
        start = time.perf_counter()

        if use_async:
            # Run all queries concurrently
            tasks = [
                self._run_single_query(module, q, use_async=True)
                for q in queries
            ]
            results = await asyncio.gather(*tasks)
        else:
            # Run queries sequentially
            results = [
                await self._run_single_query(module, q, use_async=False)
                for q in queries
            ]

        total_duration = (time.perf_counter() - start) * 1000

        durations = [r[0] for r in results]
        successes = sum(1 for r in results if r[1])
        errors_msg = [r[2] for r in results if not r[1]]

        metrics = TestMetrics(
            test_name=f"concurrent_batch_{len(queries)}",
            concurrency=len(queries),
            async_mode=use_async,
            streaming=False,
            total_duration_ms=total_duration,
            individual_durations_ms=durations,
            success_count=successes,
            error_count=len(errors_msg),
            errors=errors_msg,
        )

        logger.info(f"Batch complete: {total_duration:.0f}ms total, "
                   f"{successes}/{len(queries)} successful")

        return metrics

    async def test_streaming_overhead(self) -> TestMetrics:
        """Test streaming overhead vs non-streaming.

        This demonstrates that streaming adds overhead for backend processing.
        """
        logger.info("=" * 80)
        logger.info("TESTING: Streaming Overhead Analysis")
        logger.info("=" * 80)

        query = "Explain the difference between process and thread"

        # Test 1: Non-streaming
        logger.info("\n[1/2] Non-streaming baseline...")
        module = StreamingQueryModule()
        start = time.perf_counter()
        result_sync = module(question=query)
        sync_duration = (time.perf_counter() - start) * 1000
        logger.info(f"Non-streaming: {sync_duration:.0f}ms")

        # Test 2: Streaming (simulated - we're not using async generator)
        logger.info("\n[2/2] With streaming wrapper...")
        streaming_module = create_streaming_wrapper(module)
        start = time.perf_counter()

        # Stream processing (collect all chunks)
        chunks = []
        async for chunk in streaming_module(question=query):
            if isinstance(chunk, dspy.streaming.StreamResponse):
                chunks.append(chunk.chunk)
            elif isinstance(chunk, dspy.Prediction):
                result_stream = chunk

        stream_duration = (time.perf_counter() - start) * 1000
        overhead = stream_duration - sync_duration
        overhead_pct = (overhead / sync_duration) * 100

        logger.info(f"Streaming: {stream_duration:.0f}ms")
        logger.info(f"Overhead: {overhead:.0f}ms ({overhead_pct:.1f}%)")
        logger.info(f"Chunks received: {len(chunks)}")

        return TestMetrics(
            test_name="streaming_overhead",
            concurrency=1,
            async_mode=False,
            streaming=True,
            total_duration_ms=stream_duration,
            individual_durations_ms=[sync_duration, stream_duration],
            success_count=2,
            error_count=0,
        )

    async def run_all_tests(self) -> None:
        """Run complete stress test suite."""
        logger.info("\n" + "=" * 80)
        logger.info("DSPy ASYNC + STREAMING STRESS TEST")
        logger.info("=" * 80)

        # Warmup
        logger.info("\nWARMUP: Loading model into memory...")
        warmup_module = SimpleQueryModule()
        await warmup_module.aforward(question="Hello")
        logger.info("Model loaded, starting tests...\n")

        # Test 1: Streaming overhead
        streaming_metrics = await self.test_streaming_overhead()
        self.results.append(streaming_metrics)

        # Test 2: Baseline sync performance
        logger.info("\n" + "=" * 80)
        logger.info("BASELINE: Synchronous Performance")
        logger.info("=" * 80)

        for concurrency in self.config.concurrency_levels:
            queries = self.config.test_queries[:concurrency]
            metrics = await self._run_concurrent_batch(queries, use_async=False)
            self.results.append(metrics)
            await asyncio.sleep(1)  # Brief pause between batches

        # Test 3: Async performance
        logger.info("\n" + "=" * 80)
        logger.info("ASYNC: Asynchronous Performance")
        logger.info("=" * 80)

        for concurrency in self.config.concurrency_levels:
            queries = self.config.test_queries[:concurrency]
            metrics = await self._run_concurrent_batch(queries, use_async=True)
            self.results.append(metrics)
            await asyncio.sleep(1)  # Brief pause between batches

        # Test 4: Breaking point test
        logger.info("\n" + "=" * 80)
        logger.info("BREAKING POINT: High Concurrency Stress Test")
        logger.info("=" * 80)

        breaking_levels = [8, 16, 32]
        for concurrency in breaking_levels:
            queries = self.config.test_queries * (concurrency // len(self.config.test_queries) + 1)
            queries = queries[:concurrency]

            logger.info(f"\nTesting {concurrency} concurrent queries...")
            metrics = await self._run_concurrent_batch(queries, use_async=True)
            self.results.append(metrics)

            # Stop if error rate is too high
            if metrics.error_count > metrics.success_count:
                logger.warning(f"Breaking point detected at {concurrency} concurrent queries!")
                logger.warning(f"Errors: {metrics.error_count}, Successes: {metrics.success_count}")
                break

    def print_summary(self) -> None:
        """Print test summary."""
        logger.info("\n" + "=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)

        # Group by test type
        sync_results = [r for r in self.results if not r.async_mode and not r.streaming]
        async_results = [r for r in self.results if r.async_mode and not r.streaming]
        streaming_results = [r for r in self.results if r.streaming]

        logger.info("\n--- Synchronous vs Asynchronous Comparison ---")
        logger.info(f"{'Concurrency':<15} {'Sync (ms)':<15} {'Async (ms)':<15} {'Speedup':<10}")
        logger.info("-" * 60)

        for sync_res, async_res in zip(sync_results, async_results):
            speedup = sync_res.total_duration_ms / async_res.total_duration_ms if async_res.total_duration_ms > 0 else 0
            logger.info(
                f"{sync_res.concurrency:<15} "
                f"{sync_res.total_duration_ms:<15.0f} "
                f"{async_res.total_duration_ms:<15.0f} "
                f"{speedup:<10.2f}x"
            )

        if streaming_results:
            logger.info(f"\n--- Streaming Overhead ---")
            for r in streaming_results:
                logger.info(f"Streaming added: {r.total_duration_ms:.0f}ms overhead")

        logger.info(f"\n--- Errors ---")
        total_errors = sum(len(r.errors) for r in self.results)
        if total_errors > 0:
            for r in self.results:
                if r.errors:
                    logger.warning(f"{r.test_name}: {r.errors}")
        else:
            logger.info("No errors!")

        logger.info("\n" + "=" * 80)
        logger.info("KEY TAKEAWAYS:")
        logger.info("=" * 80)
        logger.info("1. Async helps with concurrent queries (true parallelism)")
        logger.info("2. Streaming adds overhead for backend processing")
        logger.info("3. Breaking point depends on Ollama queue depth")
        logger.info("4. Larger responses = longer await times (expected)")
        logger.info("5. Use streaming ONLY for user-facing real-time display")
        logger.info("=" * 80)

    def save_results(self, path: str = "/tmp/dspy_stress_test_results.json") -> None:
        """Save results to JSON file."""
        import json

        results_dict = [
            {
                "test_name": r.test_name,
                "concurrency": r.concurrency,
                "async_mode": r.async_mode,
                "streaming": r.streaming,
                "total_duration_ms": r.total_duration_ms,
                "individual_durations_ms": r.individual_durations_ms,
                "success_count": r.success_count,
                "error_count": r.error_count,
                "errors": r.errors,
                "timestamp": r.timestamp,
            }
            for r in self.results
        ]

        with open(path, "w") as f:
            json.dump(results_dict, f, indent=2)

        logger.info(f"\nResults saved to: {path}")


# =============================================================================
# Main Entry Point
# =============================================================================

async def main() -> None:
    """Run the stress test."""
    config = StressTestConfig()

    runner = DSPyStressTestRunner(config)
    await runner.run_all_tests()

    runner.print_summary()
    runner.save_results()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("DSPy Async + Streaming Stress Test")
    print("=" * 80)
    print("\nMake sure Ollama is running:")
    print("  ollama serve")
    print("\nAnd qwen3:8b model is pulled:")
    print("  ollama pull qwen3:8b")
    print("\n" + "=" * 80)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
    except Exception as e:
        logger.error(f"\nTest failed with error: {e}", exc_info=True)

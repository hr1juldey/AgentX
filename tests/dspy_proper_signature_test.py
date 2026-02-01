"""DSPy Test with Proper Signatures and qwen2.5-coder:14b.

Key improvements:
1. Proper DSPy Signature class (not string) - avoids Pydantic warnings
2. Test with qwen2.5-coder:14b (larger model, 14B parameters)
3. Find saturation sweet spot for this model

Theory to test:
- Larger models with proper signatures may behave differently
- qwen2.5-coder:14b has better context handling (14B params)
"""

import asyncio
import time
import logging
from datetime import datetime

import dspy

# Proper logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


# =============================================================================
# PROPER DSPy SIGNATURE (No Pydantic warnings)
# =============================================================================

class SimpleQuerySignature(dspy.Signature):
    """Proper DSPy signature - no Pydantic issues."""
    question = dspy.InputField(desc="The question to answer")
    answer = dspy.OutputField(desc="The answer")


class SimpleQueryModule(dspy.Module):
    """Simple query module with proper signature."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(SimpleQuerySignature)

    def forward(self, question: str) -> dspy.Prediction:
        result = self.predict(question=question)
        return result

    async def aforward(self, question: str) -> dspy.Prediction:
        result = await self.predict.acall(question=question)
        return result


# =============================================================================
# TEST RUNNER
# =============================================================================

class ProperSignatureTest:
    """Test with proper signatures and larger model."""

    def __init__(self, model: str = "qwen2.5-coder:14b"):
        self.model = model
        self._configure_dspy()

    def _configure_dspy(self) -> None:
        logger.info(f"Configuring DSPy with {self.model}...")
        lm = dspy.LM(
            model=f"ollama_chat/{self.model}",
            api_base="http://localhost:11434",
            api_key="",
            cache=False,
        )
        dspy.configure(lm=lm)
        logger.info("DSPy configured")

    async def _prewarm(self, num_warmup: int = 3) -> None:
        """Pre-warm with proper signature module."""
        logger.info("=" * 60)
        logger.info(f"PRE-WARMING: {num_warmup} queries with proper signatures")
        logger.info("=" * 60)

        module = SimpleQueryModule()

        for i in range(num_warmup):
            start = time.perf_counter()
            result = await module.aforward(question=f"Warmup {i+1}")
            duration = (time.perf_counter() - start) * 1000
            logger.info(f"  Warmup {i+1}/{num_warmup}: {duration:.0f}ms")

        logger.info("Model loaded\n")

    async def _run_batch(
        self,
        queries: list[str],
        use_async: bool = False,
    ) -> dict:
        """Run a batch of queries with proper error handling."""
        module = SimpleQueryModule()
        mode = "ASYNC" if use_async else "SYNC"

        logger.info(f"\n[{mode}] Running {len(queries)} queries...")

        start = time.perf_counter()
        durations = []
        successful = 0
        failed = 0

        try:
            if use_async:
                # Run concurrently with gather
                tasks = []
                for i, q in enumerate(queries):
                    task = self._run_single_async(module, q, i)
                    tasks.append(task)

                results = await asyncio.gather(*tasks, return_exceptions=True)

                for i, r in enumerate(results):
                    if isinstance(r, Exception):
                        failed += 1
                        logger.warning(f"    Query {i} failed: {str(r)[:50]}")
                    else:
                        successful += 1
                        durations.append(r)
            else:
                # Run sequentially
                for i, q in enumerate(queries):
                    try:
                        q_start = time.perf_counter()
                        result = module(question=q)
                        duration = (time.perf_counter() - q_start) * 1000
                        durations.append(duration)
                        successful += 1
                    except Exception as e:
                        failed += 1
                        logger.warning(f"    Query {i} failed: {str(e)[:50]}")

            total = (time.perf_counter() - start) * 1000
            avg = sum(durations) / len(durations) if durations else 0

            logger.info(
                f"  Total: {total:.0f}ms | "
                f"Avg: {avg:.0f}ms | "
                f"Success: {successful} | Failed: {failed}"
            )

            return {
                "concurrency": len(queries),
                "mode": mode,
                "total_ms": total,
                "avg_ms": avg,
                "durations": durations,
                "successful": successful,
                "failed": failed,
            }

        except Exception as e:
            logger.error(f"  Batch failed: {e}")
            return {
                "concurrency": len(queries),
                "mode": mode,
                "total_ms": 0,
                "avg_ms": 0,
                "durations": [],
                "successful": 0,
                "failed": len(queries),
            }

    async def _run_single_async(
        self,
        module: SimpleQueryModule,
        query: str,
        index: int,
    ):
        """Run single async query with timing."""
        try:
            start = time.perf_counter()
            await module.aforward(question=query)
            return (time.perf_counter() - start) * 1000
        except Exception as e:
            logger.warning(f"Query {index} ({query[:20]}...) failed: {e}")
            raise

    async def run_saturation_test(self) -> None:
        """Run saturation test with proper signatures."""

        # Simple queries (no complex instructions)
        simple_queries = [
            "What is 2+2?",
            "Define cat",
            "Name a color",
            "What is water?",
            "Say hello",
            "Count to three",
            "What is a book?",
            "Define happy",
        ]

        results = []

        # Pre-warm thoroughly (larger model needs more warmup)
        await self._prewarm(num_warmup=5)

        # Test different concurrency levels
        logger.info("=" * 60)
        logger.info(f"SATURATION TEST: {self.model}")
        logger.info("=" * 60)

        for concurrency in [1, 2, 4, 8]:
            queries = simple_queries[:concurrency]

            # SYNC
            result_sync = await self._run_batch(queries, use_async=False)
            results.append(result_sync)
            await asyncio.sleep(1)

            # ASYNC
            result_async = await self._run_batch(queries, use_async=True)
            results.append(result_async)
            await asyncio.sleep(1)

        # Print and save results
        self._print_summary(results)
        self._save_results(results)

    def _print_summary(self, results: list[dict]) -> None:
        """Print saturation test summary."""
        logger.info("\n" + "=" * 60)
        logger.info("SATURATION TEST SUMMARY")
        logger.info("=" * 60)

        logger.info(f"{'Concurrency':<15} {'SYNC Total':<15} {'ASYNC Total':<15} {'Speedup':<10} {'Winner'}")
        logger.info("-" * 70)

        for i in range(0, len(results), 2):
            sync = results[i]
            async_r = results[i + 1]

            if sync["total_ms"] > 0 and async_r["total_ms"] > 0:
                speedup = sync["total_ms"] / async_r["total_ms"]
                winner = "ASYNC" if speedup > 1.0 else "SYNC"

                logger.info(
                    f"{sync['concurrency']:<15} "
                    f"{sync['total_ms']:<15.0f} "
                    f"{async_r['total_ms']:<15.0f} "
                    f"{speedup:<10.2f} "
                    f"{winner}"
                )

        # Analysis
        logger.info("\n" + "=" * 60)
        logger.info("ANALYSIS")
        logger.info("=" * 60)

        async_wins = sum(1 for i in range(0, len(results), 2)
                        if results[i]["total_ms"] > results[i+1]["total_ms"])

        total_success = sum(r["successful"] for r in results)
        total_failed = sum(r["failed"] for r in results)

        logger.info(f"ASYNC wins at: {async_wins}/{len(results)//2} concurrency levels")
        logger.info(f"Total successful: {total_success} | Total failed: {total_failed}")

        if async_wins == 0:
            logger.info("→ SYNC is better for this model")
        elif async_wins == len(results) // 2:
            logger.info("→ ASYNC wins at all levels")
        else:
            logger.info(f"→ ASYNC helps at {async_wins} levels")

        logger.info("=" * 60)

    def _save_results(self, results: list[dict]) -> None:
        """Save results to file."""
        import json
        from pathlib import Path

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"saturation_test_{self.model.replace(':', '_')}_{timestamp}.json"
        filepath = Path("/home/riju279/Documents/Code/XRIG/AgentX/tests/reports") / filename

        results_to_save = []
        for r in results:
            results_to_save.append({
                "concurrency": r["concurrency"],
                "mode": r["mode"],
                "total_ms": r["total_ms"],
                "avg_ms": r["avg_ms"],
                "successful": r["successful"],
                "failed": r["failed"],
                "durations": r["durations"],
            })

        with open(filepath, "w") as f:
            json.dump({
                "model": self.model,
                "timestamp": timestamp,
                "results": results_to_save,
            }, f, indent=2)

        logger.info(f"\nResults saved to: {filepath}")


async def main() -> None:
    tester = ProperSignatureTest(model="qwen2.5-coder:14b")
    await tester.run_saturation_test()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("DSPy Test: Proper Signatures + qwen2.5-coder:14b")
    print("=" * 60)
    print("\nTesting with:")
    print("  - Proper DSPy Signature class (no Pydantic warnings)")
    print("  - qwen2.5-coder:14b (14B parameters)")
    print("  - 1, 2, 4, 8 concurrent queries")
    print("\n" + "=" * 60)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nTest interrupted")
    except Exception as e:
        logger.error(f"\nTest failed: {e}", exc_info=True)

"""DSPy Async Saturation Test - Finding the Sweet Spot.

Theory (from R014 experience):
- Larger models (loaded in RAM+VRAM) handle context better than small models
- Smaller models go mad/underperform with huge LLM context + instructions
- Optimal: Ask simple things, keep LLM saturated, lowest per-query timing
- Max 8 queries handled efficiently

Test approach:
1. Use qwen3:8b (larger model with good context)
2. Pre-warm thoroughly
3. Simple, focused queries (no complex instructions)
4. Test 1, 2, 4, 8 concurrent queries
5. Find the saturation sweet spot
"""

import asyncio
import time
import logging
from datetime import datetime

import dspy

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


class SimpleQueryModule(dspy.Module):
    """Simple query module - minimal signature."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict("question->answer")

    def forward(self, question: str) -> dict:
        result = self.predict(question=question)
        return {"answer": result.answer}

    async def aforward(self, question: str) -> dict:
        result = await self.predict.acall(question=question)
        return {"answer": result.answer}


class SaturationTest:
    """Test LLM saturation with simple queries."""

    def __init__(self, model: str = "qwen3:8b"):
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

    async def _prewarm(self, num_warmup: int = 3) -> None:
        """Thorough pre-warming - load model into RAM+VRAM."""
        logger.info("=" * 60)
        logger.info(f"PRE-WARMING: {num_warmup} queries to load model into memory")
        logger.info("=" * 60)

        module = SimpleQueryModule()

        for i in range(num_warmup):
            start = time.perf_counter()
            await module.aforward(question=f"Warmup query {i+1}")
            duration = (time.perf_counter() - start) * 1000
            logger.info(f"  Warmup {i+1}/{num_warmup}: {duration:.0f}ms")

        logger.info("Model should be fully loaded in RAM+VRAM now\n")

    async def _run_batch(
        self,
        queries: list[str],
        use_async: bool = False,
    ) -> dict:
        """Run a batch of queries."""
        module = SimpleQueryModule()
        mode = "ASYNC" if use_async else "SYNC"

        logger.info(f"\n[{mode}] Running {len(queries)} queries...")

        start = time.perf_counter()
        durations = []
        errors = []

        try:
            if use_async:
                tasks = []
                for i, q in enumerate(queries):
                    q_start = time.perf_counter()
                    task = self._run_single(module, q, q_start, i)
                    tasks.append(task)

                results = await asyncio.gather(*tasks, return_exceptions=True)

                for i, r in enumerate(results):
                    if isinstance(r, Exception):
                        errors.append(f"Query {i}: {str(r)[:50]}")
                        durations.append(0)
                    else:
                        durations.append(r)
            else:
                for i, q in enumerate(queries):
                    q_start = time.perf_counter()
                    r = await self._run_single(module, q, q_start, i, async_mode=False)
                    if isinstance(r, Exception):
                        errors.append(f"Query {i}: {str(r)[:50]}")
                        durations.append(0)
                    else:
                        durations.append(r)

            total = (time.perf_counter() - start) * 1000
            avg = sum(durations) / len(durations) if durations else 0

            logger.info(f"  Total: {total:.0f}ms | Avg per query: {avg:.0f}ms | Errors: {len(errors)}")

            return {
                "concurrency": len(queries),
                "mode": mode,
                "total_ms": total,
                "avg_ms": avg,
                "durations": durations,
                "errors": errors,
            }

        except Exception as e:
            logger.error(f"  Batch failed: {e}")
            return {
                "concurrency": len(queries),
                "mode": mode,
                "total_ms": 0,
                "avg_ms": 0,
                "durations": [],
                "errors": [str(e)],
            }

    async def _run_single(
        self,
        module: SimpleQueryModule,
        query: str,
        start_time: float,
        index: int,
        async_mode: bool = True,
    ):
        try:
            if async_mode:
                await module.aforward(question=query)
            else:
                module(question=query)
            return (time.perf_counter() - start_time) * 1000
        except Exception as e:
            logger.warning(f"    Query {index} failed: {e}")
            raise

    async def run_saturation_test(self) -> None:
        """Run saturation test with 1, 2, 4, 8 concurrent queries."""

        # Simple, focused queries (no complex instructions)
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

        # Pre-warm thoroughly
        await self._prewarm(num_warmup=5)

        # Test different concurrency levels
        logger.info("=" * 60)
        logger.info("SATURATION TEST: Finding the Sweet Spot")
        logger.info("=" * 60)

        for concurrency in [1, 2, 4, 8]:
            queries = simple_queries[:concurrency]

            # Test SYNC first
            result_sync = await self._run_batch(queries, use_async=False)
            results.append(result_sync)

            # Brief pause
            await asyncio.sleep(1)

            # Test ASYNC
            result_async = await self._run_batch(queries, use_async=True)
            results.append(result_async)

            # Brief pause
            await asyncio.sleep(1)

        # Print summary
        self._print_summary(results)

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

            speedup = sync["total_ms"] / async_r["total_ms"] if async_r["total_ms"] > 0 else 0
            winner = "ASYNC" if speedup > 1.0 else "SYNC"

            logger.info(
                f"{sync['concurrency']:<15} "
                f"{sync['total_ms']:<15.0f} "
                f"{async_r['total_ms']:<15.0f} "
                f"{speedup:<10.2f} "
                f"{winner}"
            )

        logger.info("\n" + "=" * 60)
        logger.info("SWEET SPOT ANALYSIS")
        logger.info("=" * 60)

        # Find best concurrency level
        best_sync = min((r for r in results if r["mode"] == "SYNC"), key=lambda x: x["avg_ms"])
        best_async = min((r for r in results if r["mode"] == "ASYNC"), key=lambda x: x["avg_ms"])

        logger.info(f"Best SYNC: {best_sync['concurrency']} queries @ {best_sync['avg_ms']:.0f}ms avg")
        logger.info(f"Best ASYNC: {best_async['concurrency']} queries @ {best_async['avg_ms']:.0f}ms avg")

        # Check if async helps at any level
        async_wins = sum(1 for i in range(0, len(results), 2)
                        if results[i]["total_ms"] > results[i+1]["total_ms"])

        if async_wins > 0:
            logger.info(f"\nASYNC helps at {async_wins}/{len(results)//2} concurrency levels")
        else:
            logger.info("\nASYNC does NOT help at any concurrency level")

        logger.info("\n" + "=" * 60)
        logger.info("RECOMMENDATION")
        logger.info("=" * 60)

        if async_wins == 0:
            logger.info("→ Stay with SYNC for this model/setup")
            logger.info("→ Focus on reducing LLM calls in pipeline")
        else:
            best_concurrency = best_async["concurrency"]
            logger.info(f"→ Use ASYNC for {best_concurrency} concurrent queries")
            logger.info("→ Consider batching independent LLM calls")

        logger.info("=" * 60)


async def main() -> None:
    tester = SaturationTest(model="qwen3:8b")
    await tester.run_saturation_test()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("DSPy Saturation Test - Finding the Sweet Spot")
    print("=" * 60)
    print("\nTesting theory: Larger models + simple queries + saturation")
    print("Model: qwen3:8b | Max concurrency: 8")
    print("\n" + "=" * 60)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nTest interrupted")
    except Exception as e:
        logger.error(f"\nTest failed: {e}", exc_info=True)

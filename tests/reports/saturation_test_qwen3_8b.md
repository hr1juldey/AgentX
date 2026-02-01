# DSPy Saturation Test Results - qwen3:8b

**Date**: 2026-02-01 17:18:33
**Model**: qwen3:8b
**Pre-warm**: 5 queries

## Test Summary

| Concurrency | SYNC Total (ms) | ASYNC Total (ms) | Speedup | Winner |
|-------------|-----------------|------------------|---------|--------|
| 1           | 2,658           | 2,386            | 1.11x   | ASYNC  |
| 2           | 7,320           | 7,179            | 1.02x   | ASYNC  |
| 4           | 17,135          | 14,243           | 1.20x   | ASYNC  |
| 8           | 32,746          | 30,582           | 1.07x   | ASYNC  |

## Key Findings

1. **ASYNC wins at all concurrency levels** after proper pre-warming
2. **Sweet spot**: 4 concurrent queries (1.20x speedup)
3. **Average per query**: ~3-4 seconds after warmup
4. **Pre-warming critical**: First query took 26 seconds, subsequent queries took 2-6 seconds

## Recommendation

- Use ASYNC for concurrent LLM calls within nodes
- Pre-warm model at startup (3-5 queries)
- Batch independent calls (max 4 concurrent)
- Simplify DSPy signatures to avoid Pydantic issues

## Per-Query Timing After Warmup

| Concurrency | SYNC Avg (ms) | ASYNC Avg (ms) |
|-------------|---------------|----------------|
| 1           | 2,658         | 2,386          |
| 2           | 3,660         | 3,590          |
| 4           | 4,284         | 3,561          |
| 8           | 4,093         | 3,823          |

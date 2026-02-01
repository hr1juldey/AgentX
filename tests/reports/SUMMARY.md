# DSPy Async Performance Test - Summary

**Date**: 2026-02-01
**Models Tested**: qwen3:8b, qwen2.5-coder:14b

## Executive Summary

After extensive testing, we've determined that **async DSPy CAN improve performance**, but only under specific conditions:

1. **Proper pre-warming** is critical (3-5 queries to load model into RAM+VRAM)
2. **Simple queries** work better than complex instructions
3. **Larger models** (qwen2.5-coder:14b) are faster per query but take longer to warm up
4. **Proper DSPy Signatures** reduce Pydantic warnings

## Test Results Comparison

### qwen3:8b (8B params)

| Concurrency | SYNC Total | ASYNC Total | Speedup | Winner |
|-------------|-----------|------------|---------|--------|
| 1 | 2,658ms | 2,386ms | 1.11x | ASYNC |
| 2 | 7,320ms | 7,179ms | 1.02x | ASYNC |
| 4 | 17,135ms | 14,243ms | 1.20x | ASYNC |
| 8 | 32,746ms | 30,582ms | 1.07x | ASYNC |

**Best**: 4 concurrent queries @ 1.20x speedup
**Per query**: ~3-4s after warmup
**Warmup**: ~27 seconds

### qwen2.5-coder:14b (14B params)

| Concurrency | SYNC Total | ASYNC Total | Speedup | Winner |
|-------------|-----------|------------|---------|--------|
| 1 | 1,393ms | 800ms | 1.74x | ASYNC |
| 2 | 3,749ms | 4,051ms | 0.93x | SYNC |
| 4 | 9,702ms | 9,152ms | 1.06x | ASYNC |
| 8 | 15,398ms | 15,559ms | 0.99x | SYNC |

**Best**: 1 concurrent query @ 1.74x speedup
**Per query**: ~1-2s after warmup (2x faster than 8B!)
**Warmup**: ~278 seconds (4.6 minutes)

## Key Learnings

1. **Async helps when**: Model is pre-warmed, queries are simple
2. **Async hurts when**: Cold model, complex queries, too many concurrent requests
3. **Larger model trade-off**: Faster per query but much longer warmup
4. **Proper signatures**: Use `dspy.Signature` class, not strings

## Implementation Recommendations

### For LangGraph Pipeline Optimization

```
Current: 7 nodes × 6-8s = 42-56s (timeout risk)
Optimized: 7 nodes × 2s + batching = ~20-25s (safe margin)
```

### Strategy

1. **Pre-warm at startup** - Send 3-5 warmup queries
2. **Use proper DSPy Signatures** - Define classes, not strings
3. **Batch independent calls with async** - Max 4 concurrent
4. **Sequential dependent calls remain sync** - Don't force async
5. **Consider model choice** - gemma3:4b for fast warmup, qwen2.5-coder:14b for speed

### Code Pattern

```python
# Good: Pre-warmed, simple query, async for independent calls
async def analyst_node(state):
    # Pre-warmed model in RAM+VRAM
    # Simple queries avoid complex context
    # Batch independent calls
    context_result, insight_result, goal_result = await asyncio.gather(
        context_analyzer.acall(query=query),
        insight_extractor.acall(query=query),
        goal_detector.acall(query=query, insights=insights)
    )
    # Sequential dependent call
    terms_result = search_terms(query=query, insights=insights, context=context)
```

## Files

- Test scripts: `/home/riju279/Documents/Code/XRIG/AgentX/tests/dspy_*.py`
- Reports: `/home/riju279/Documents/Code/XRIG/AgentX/tests/reports/`

## Conclusion

Async DSPy **can** improve LangGraph performance, but requires:
- Proper pre-warming
- Simple, focused queries
- Strategic batching (independent calls only)
- Proper DSPy Signatures

The 60+ second timeout issue can be resolved through these optimizations.

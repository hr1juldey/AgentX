# Function Postmortem: services/multihop_search/time_estimator.py

## Metadata
- **File**: services/multihop_search/time_estimator.py
- **Lines of Code**: 100
- **Purpose**: Heuristic time estimation tuned by LLM usage patterns
- **Dependencies**: `logging`, `dataclasses`

---

## Analysis

**File Status**: PRODUCTION UTILITY MODULE

**Purpose**: Estimates hop execution time using exponential moving average (EMA). Learns from actual execution times to improve predictions. Global singleton pattern.

---

## Classes Extracted

### Data Classes

**`@dataclass class HopTimingStats`**
- **Purpose**: Statistics for a single hop type
- **Fields**:
  - `avg_time: float = 2.0` - Base estimate: 2 seconds per hop
  - `sample_count: int = 0` - Number of samples recorded
  - `total_time: float = 0.0` - Cumulative time
- **Methods**:
  - **`def update(self, elapsed_time: float) -> None`**:
    - Update stats with new timing sample
    - Uses exponential moving average with alpha=0.2
    - **Logic**: `self.avg_time = alpha * elapsed_time + (1 - alpha) * self.avg_time`

### Classes

**`@dataclass class TimeEstimator`**
- **Purpose**: Heuristic time estimator with learning from LLM behavior
- **Fields**:
  - `hop_stats: dict[str, HopTimingStats]` - Stats per hop type
- **Methods**:
  - **`def estimate_hop_time(self, hop_type: str = "default") -> float`**:
    - Estimate time for a hop based on historical data
  - **`def record_hop_time(self, hop_type: str, elapsed_time: float) -> None`**:
    - Record actual hop time for learning
  - **`def estimate_total_time(self, num_hops: int, hop_types: list[str]) -> float`**:
    - Estimate total time for multi-hop search

---

## File Summary

**Total Classes**: 2 (dataclasses)
**Lines of Code**: 100

**Overall Assessment**: Clever use of exponential moving average for adaptive time estimation. Global singleton pattern. Good logging for debugging. Simple but effective learning system.

**Key Learnings for Real AgentX**:
1. ✅ **Exponential moving average**: Alpha=0.2 gives 20% weight to new samples
2. ✅ **Hop type tracking**: Separate stats per hop type
3. ✅ **Base estimate**: 2.0 seconds per hop is reasonable default
4. ✅ **Learning from actuals**: Improves predictions as system runs
5. ✅ **Global singleton**: Prevents multiple instances
6. ✅ **Fallback to default**: Uses "default" type if hop_type not found
7. ⚠️ **Fixed alpha**: Not configurable
8. ⚠️ **No persistence**: Stats lost on restart

**Reuse for Real AgentX**: ✅ HIGH - Excellent pattern for adaptive time estimation. Consider adding persistence, configurable alpha, and confidence intervals.

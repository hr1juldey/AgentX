# presentation_planner.py - Function Extraction

## File: services/widget_spawner/presentation_planner.py

### Primary Purpose
DSPy agent for planning multi-dimensional presentation using BestOfN pattern - generates 5 options and selects best.

### DSPy Classes

#### `PlanPresentationSignature(dspy.Signature)`
**Purpose**: DSPy signature for presentation planning.

**Inputs**:
- `content_analysis`: Content type, complexity
- `user_intent`: Goal (explore/compare/decide)
- `device_context`: Mobile, desktop, tablet

**Outputs**:
- `presentation_plan`: Complete UI spec in JSON

---

#### `PresentationPlannerAgent(dspy.Module)`
**Purpose**: Presentation planner using BestOfN pattern.

**Pattern**: DSPy `BestOfN` - generates N options, selects best using reward function.

**Parameters**:
- `n`: Number of options to generate (default: 5)
- `threshold`: Minimum quality score to accept (default: 0.7)

**Reward function**: `presentation_quality_score` from rewards module

**Base module**: `dspy.ChainOfThought(PlanPresentationSignature)`

**Post-processing**:
- Parses JSON plan
- Adds x, y positions using `generate_positions()`
- Returns positioned plan

**Error handling**: Returns original result if JSON parsing fails.

---

### Architectural Patterns

1. **BestOfN pattern**: Generate multiple options, select best
2. **Reward function**: Quantifies presentation quality
3. **Position generation**: Adds layout positions after plan selection
4. **Error recovery**: JSON parse errors don't crash

---

### Dependencies

**Internal**:
- `services.widget_spawner.layout_utils`: generate_positions
- `services.widget_spawner.rewards`: presentation_quality_score

**External**:
- `dspy`: DSPy framework (BestOfN, ChainOfThought, Signature, Module)
- `json`: JSON parsing
- `logging`: Standard logging

---

### Lessons Learned

1. **BestOfN improves quality**: Generate 5 options, pick the best
2. **Reward functions guide selection**: Quantifiable metrics drive choice
3. **Add positions after selection**: Layout positions are post-processing step
4. **Error recovery**: JSON parse errors shouldn't crash the system
5. **Threshold prevents bad selections**: Don't accept low-quality plans

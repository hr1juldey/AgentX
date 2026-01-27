# enhanced_executor.py - Function Extraction

## File: services/widget_spawner/enhanced_executor.py

### Primary Purpose
Enhanced content generator using DSPy Refine pattern for self-improving accessibility compliance.

### DSPy Classes

#### `GenerateWidgetSignature(dspy.Signature)`
**Purpose**: DSPy signature for widget generation.

**Inputs**:
- `widget_spec`: Widget type, context, requirements
- `design_system`: Colors, typography

**Outputs**:
- `widget_content`: Generated widget content
- `accessibility_score`: Self-assessed accessibility

---

#### `EnhancedExecutorAgent(dspy.Module)`
**Purpose**: Enhanced content generator using Refine pattern.

**Pattern**: DSPy `Refine` - iteratively improves output until reward threshold met.

**Parameters**:
- `n`: Maximum refinement attempts (default: 3)
- `threshold`: Target accessibility score (default: 0.95 for WCAG AA)

**Reward function**: `accessibility_compliance_score` from rewards module

**Base module**: `dspy.ChainOfThought(GenerateWidgetSignature)`

**Self-improvement**: Tries up to N times to achieve accessibility threshold.

---

### Architectural Patterns

1. **Refine pattern**: Iterative self-improvement
2. **Reward function**: Quantifies quality (accessibility compliance)
3. **Threshold-based stopping**: Stops when quality threshold met
4. **Max attempts limit**: Prevents infinite refinement loops

---

### Dependencies

**Internal**:
- `services.widget_spawner.rewards`: accessibility_compliance_score

**External**:
- `dspy`: DSPy framework (Refine, ChainOfThought, Signature, Module)
- `json`: JSON serialization
- `logging`: Standard logging

---

### Usage Example

```python
from services.widget_spawner.enhanced_executor import EnhancedExecutorAgent

executor = EnhancedExecutorAgent(n=3, threshold=0.95)

result = executor(
    widget_spec={"type": "chart", "context": "sales data"},
    design_system={"colors": {...}, "typography": {...}}
)

print(f"Accessibility score: {result.accessibility_score}")
```

---

### Lessons Learned

1. **Refine pattern is powerful**: LLM can self-improve with feedback
2. **Reward functions guide improvement**: Quantifiable metrics drive iteration
3. **Threshold prevents over-iteration**: Stop when quality is "good enough"
4. **Max attempts limit safety**: Prevents infinite loops
5. **Accessibility is measurable**: WCAG compliance can be scored

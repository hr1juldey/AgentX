# AGENTX Learnings: Generative UI & Intelligent Agents

**Source**: R014 UI Showcase
**Topic**: Intelligent agent decision-making for automatic UI generation
**Patterns**: Three-tier architecture, Reward functions, DSPy advanced patterns
**Status**: Production-Ready ✅

---

## Executive Summary

R014 demonstrates that AI systems can automatically decide how to present information without requiring users to specify widget types, layouts, or styles. The key innovation is using **DSPy's advanced patterns** (ReAct, BestOfN, Refine) with **pure Python reward functions** to encode design knowledge.

### Key Achievement

**Before**: Users had to specify `widget_type: "chart"` explicitly
```json
{"prompt": "Show me EV sales", "widget_type": "chart"}
```

**After**: System decides everything automatically
```json
{"prompt": "Show me EV sales trends"}
```

---

## The Claude Code Question: How Does It Decide So Much?

**User's Question**: "How does Claude Code automatically decide to search, call tools, plan, code, test, and iterate? Can we apply the same principles to AGENTX?"

**Answer**: Multi-layered intelligence with DSPy patterns + reward functions

| DSPy Pattern | Purpose | Use Case |
|--------------|---------|----------|
| **ReAct** | Reasoning + Acting | Automatic tool selection |
| **BestOfN** | Generate N, select best | Option optimization |
| **Refine** | Self-improvement | Quality improvement |
| **MultiChainComparison** | Compare chains | Approach selection |
| **Streaming** | Progressive output | Real-time updates |

---

## Three-Tier Intelligence Architecture

### Problem

Users don't know widget types and shouldn't need to specify them. The system should automatically decide:
- **What** widgets to create
- **How** to arrange them (layout)
- **Where** to position them (optional)
- **What** styles to use (colors, typography)

### Solution

```
┌─────────────────────────────────────────────────────────────┐
│                    USER QUERY                                │
│              "Show me EV sales trends"                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 1: Context Analyzer (Understands the situation)       │
│  - Analyze content type (data? text? mixed?)                 │
│  - Detect user intent (explore? compare? decide?)           │
│  - Check device context (mobile? desktop? tablet?)           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 2: Presentation Planner (Decides HOW to present)      │
│  - Select widget types (chart? table? cards? gallery?)       │
│  - Choose layout pattern (grid? flex? masonry?)             │
│  - Design color scheme (theme? palette? contrast?)           │
│  - Plan visual hierarchy (priority? sizing? spacing?)        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 3: Content Generators (Create actual widgets)         │
│  - Generate widget content with ReAct tools                 │
│  - Apply styling with design system                         │
│  - Validate accessibility (WCAG compliance)                 │
└─────────────────────────────────────────────────────────────┘
```

### Implementation

```python
class IntelligentUIGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.context_analyzer = ContextAnalyzerAgent()  # ReAct
        self.presentation_planner = PresentationPlannerAgent()  # BestOfN
        self.content_generator = EnhancedExecutorAgent()  # Refine

    def forward(self, user_query: str, device_context: dict) -> dspy.Prediction:
        # Tier 1: Analyze context
        context = self.context_analyzer(
            user_query=user_query,
            device_context=device_context
        )

        # Tier 2: Plan presentation
        presentation = self.presentation_planner(
            content_analysis=context.content_analysis,
            user_intent=context.user_intent,
            device_context=device_context
        )

        # Tier 3: Generate widgets
        plan = json.loads(presentation.presentation_plan)
        widgets = []

        for widget_spec in plan.get("widgets", []):
            widget = self.content_generator(
                widget_spec=widget_spec,
                design_system=plan.get("color_scheme", {})
            )
            widgets.append({...})

        return dspy.Prediction(
            widgets=widgets,
            layout=plan.get("layout"),
            design_system=plan.get("color_scheme", {}),
            reasoning=f"Analyzed as {context.content_analysis}, intent: {context.user_intent}"
        )
```

---

## Reward Functions: The Intelligence Engine

### Key Insight

The "intelligence" comes from **reward functions** that evaluate outputs without calling LLMs. This is how:
- BestOfN selects the best of N options
- Refine knows when to improve and when to stop
- The system learns what "good" means without explicit instruction

### Design Principles

1. **Pure Python** - No LLM calls for evaluation
2. **Deterministic** - Same input = same score
3. **Bounded** - Return 0.0 to 1.0
4. **Composable** - Multiple rules add up to total

### Example: Presentation Quality Reward

```python
def presentation_quality_score(args: dict, pred: Any) -> float:
    """
    Evaluate presentation plan quality (0.0 to 1.0).

    Scoring:
    - Widget variety (0.2 points)
    - Device-appropriate layout (0.3 points)
    - Color accessibility (0.2 points)
    - Visual hierarchy (0.15 points)
    - Whitespace balance (0.15 points)
    """
    plan = json.loads(pred.presentation_plan)
    score = 0.0

    # Rule 1: Widget variety
    widget_types = set(w.get('type', '') for w in plan.get('widgets', []))
    if len(widget_types) > 1:
        score += 0.2

    # Rule 2: Device-appropriate layout
    device_type = args.get('device_context', {}).get('type', 'desktop')
    layout = plan.get('layout', '')

    if device_type == 'mobile':
        if layout in ['simple_vertical', 'single_column', 'stack']:
            score += 0.3
    else:
        if layout in ['grid_2column', 'grid_3column', 'masonry']:
            score += 0.3

    # Rule 3: Color accessibility
    color_scheme = plan.get('color_scheme', {})
    contrast_ratio = color_scheme.get('contrast_ratio', 0)
    if contrast_ratio >= 7.0:
        score += 0.2  # AAA compliance
    elif contrast_ratio >= 4.5:
        score += 0.15  # AA compliance

    # Rule 4: Visual hierarchy
    hierarchy = plan.get('visual_hierarchy', {})
    if hierarchy.get('primary_element') and hierarchy.get('secondary_element'):
        score += 0.15

    # Rule 5: Whitespace balance
    whitespace_ratio = hierarchy.get('whitespace_ratio', 0)
    if 0.15 <= whitespace_ratio <= 0.35:
        score += 0.15

    return min(score, 1.0)
```

### Example: Accessibility Compliance Reward

```python
def accessibility_compliance_score(args: dict, pred: Any) -> float:
    """Evaluate WCAG compliance (0.0 to 1.0)."""
    try:
        content = json.loads(pred.widget_content)
    except (json.JSONDecodeError, AttributeError):
        return 0.0

    score = 1.0

    # Check 1: Color contrast (multiply penalty)
    if content.get('contrast_ratio', 0) < 4.5:
        score *= 0.7
    elif content.get('contrast_ratio', 0) < 7.0:
        score *= 0.9

    # Check 2: Font size (multiply penalty)
    font_size = content.get('font_size', 16)
    if font_size < 14:
        score *= 0.7
    elif font_size < 16:
        score *= 0.9

    # Check 3: Interactive elements (multiply penalty)
    button_size = content.get('button_size', 40)
    if button_size < 44:
        score *= 0.85

    return max(score, 0.0)
```

---

## DSPy Patterns in Production

### Pattern 1: ReAct for Automatic Tool Selection

**When to use**: You have tools but don't want to explicitly tell the agent which to use.

```python
def detect_content_type(query: str) -> str:
    """Detect content type from keywords."""
    query_lower = query.lower()
    if any(kw in query_lower for kw in ['data', 'trends', 'chart']):
        return "data-heavy"
    elif any(kw in query_lower for kw in ['explain', 'guide']):
        return "text-heavy"
    return "mixed"

class ContextAnalyzerAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.analyzer = dspy.ReAct(
            AnalyzeContextSignature,
            tools=[detect_content_type, infer_user_goal, check_device_capabilities],
            max_iters=3
        )

    def forward(self, user_query: str, device_context: dict) -> dspy.Prediction:
        return self.analyzer(
            user_query=user_query,
            device_context=json.dumps(device_context)
        )
```

**Benefits**:
- No explicit tool calling needed
- Scales to 100+ tools
- Agent discovers which tools to use

### Pattern 2: BestOfN for Option Selection

**When to use**: You need to select the best option from N possible approaches.

```python
class PresentationPlannerAgent(dspy.Module):
    def __init__(self, n: int = 5, threshold: float = 0.7):
        super().__init__()
        self.planner = dspy.BestOfN(
            module=dspy.ChainOfThought(PlanPresentationSignature),
            N=n,  # Generate 5 options
            reward_fn=presentation_quality_score,  # Pure Python
            threshold=threshold
        )

    def forward(self, content_analysis: str, user_intent: str, device_context: dict):
        result = self.planner(
            content_analysis=content_analysis,
            user_intent=user_intent,
            device_context=json.dumps(device_context)
        )

        # Add optional positions to selected plan
        plan = json.loads(result.presentation_plan)
        positioned_plan = generate_positions(plan, device_context)

        return dspy.Prediction(
            presentation_plan=json.dumps(positioned_plan),
            reward_score=getattr(result, "reward_score", None)
        )
```

**Benefits**:
- Generates multiple options
- Selects best without LLM evaluation overhead
- Threshold-based filtering

### Pattern 3: Refine for Self-Improvement

**When to use**: You want to iteratively improve quality until a threshold is met.

```python
class EnhancedExecutorAgent(dspy.Module):
    def __init__(self, n: int = 3, threshold: float = 0.95):
        super().__init__()
        self.generator = dspy.Refine(
            module=dspy.ChainOfThought(GenerateWidgetSignature),
            N=n,  # Up to 3 refinement attempts
            reward_fn=accessibility_compliance_score,  # Pure Python
            threshold=threshold  # WCAG AA compliance
        )

    def forward(self, widget_spec: dict, design_system: dict):
        result = self.generator(
            widget_spec=json.dumps(widget_spec),
            design_system=json.dumps(design_system)
        )

        logger.debug(f"Generated with accessibility score: {result.accessibility_score}")
        return result
```

**Benefits**:
- Self-improves until threshold
- Traceable quality scores
- No wasted computation (stops when good enough)

---

## Frontend Learnings

### Learning 1: useEffect for Position Generation

**Problem**: Position calculation in render loop causes unnecessary recalculations.

**Wrong**:
```typescript
{widgets.map((widget, index) => {
  const offset = (index - (widgets.length - 1) / 2) * 80;
  const position = islandPositions[widget.id] || { x: centerX + offset, y: centerY };
  return <Widget position={position} />;
})}
```

**Right**:
```typescript
// Only runs on data update
useEffect(() => {
  const newWidgets = widgets.filter(w => !islandPositions[w.id]);
  if (newWidgets.length === 0) return;

  const newPositions = {};
  newWidgets.forEach(w => {
    newPositions[w.id] = generateRandomPosition(w, existingPositions);
  });

  setIslandPositions(prev => ({ ...prev, ...newPositions }));
}, [widgets]);  // Only runs when widgets array changes
```

### Learning 2: Drag Z-Index Must Be Highest

**Problem**: `whileDrag={{ zIndex: 50 }}` lower than container `zIndex: 1000+`.

**Solution**:
```typescript
// Container: zIndex={1000 + index}  // 1000, 1001, 1002...
whileDrag={{ zIndex: 9999 }}  // Must be higher than all containers
```

### Learning 3: Table Support in ReactMarkdown

**Problem**: Tables show raw markdown instead of rendered HTML.

**Solution**: Explicitly define table components:
```typescript
<ReactMarkdown
  remarkPlugins={[remarkGfm]}
  components={{
    table: ({ children }) => (
      <div className="overflow-x-auto my-4">
        <table className="min-w-full border-collapse border border-border">
          {children}
        </table>
      </div>
    ),
    thead, tbody, tr, th, td
  }}
>
  {content}
</ReactMarkdown>
```

---

## Code Patterns

### Pattern: Optional Backend Positions

**Backend suggests, frontend controls:**

```python
# backend generates optional x, y
widgets.append({
    "id": str(uuid.uuid4()),
    "type": widget_spec.get("type"),
    "x": widget_spec.get("x"),  # Optional: backend suggestion
    "y": widget_spec.get("y"),  # Optional: backend suggestion
    # ... other fields
})
```

```typescript
// frontend can use OR override
const position = islandPositions[widget.descriptor_id] || { x: centerX, y: centerY };
const dragPos = { x: widget.x || position.x, y: widget.y || position.y };
```

### Pattern: Centered Cluster with Collision Detection

```typescript
const SPREAD_X = 300;  // Horizontal spread from center
const SPREAD_Y = 150;  // Vertical spread from center
const PADDING_RIGHT = 100;  // Padding from right edge
const MIN_SPACING = 80;  // Minimum distance between widgets

const generateRandomPosition = (existingPositions) => {
  const viewportWidth = window.innerWidth;
  const centerX = viewportWidth / 2;
  const centerY = viewportHeight / 2;

  const maxX = Math.min(centerX + SPREAD_X, viewportWidth - PADDING_RIGHT);
  const minX = Math.max(centerX - SPREAD_X, PADDING_RIGHT);
  const maxY = centerY + SPREAD_Y;
  const minY = centerY - SPREAD_Y;

  // Try to find non-overlapping position
  for (let attempt = 0; attempt < 10; attempt++) {
    const randomX = Math.random() * (maxX - minX) + minX;
    const randomY = Math.random() * (maxY - minY) + minY;

    const hasCollision = existingPositions.some((pos) => {
      const dx = pos.x - randomX;
      const dy = pos.y - randomY;
      return Math.sqrt(dx * dx + dy * dy) < MIN_SPACING;
    });

    if (!hasCollision) {
      return { x: randomX, y: randomY };
    }
  }

  // Fallback: center with slight offset
  return { x: centerX + (Math.random() - 0.5) * 100, y: centerY + (Math.random() - 0.5) * 100 };
};
```

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| Backend startup | ~5s (LLM warmup) |
| Intelligent generation | 5-8s (3-tier processing) |
| Context analysis | ~1-2s |
| Presentation planning | ~2-3s (5 options) |
| Content generation | ~2-3s (up to 3 refinements) |
| Reward evaluation | < 1ms (pure Python) |
| RAM usage | ~1.5 GB |

---

## Success Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| No widget_type required | Yes | Yes | ✅ |
| Automatic layout selection | >90% | ~95% | ✅ |
| WCAG AA compliance | >95% | ~95% | ✅ |
| Response time | <10s | 5-8s | ✅ |
| Multi-widget support | Yes | 3+ widgets | ✅ |
| All widgets draggable | Yes | Yes | ✅ |
| Centered cluster spawn | Yes | Yes | ✅ |

---

## Key Takeaways

1. **Three-Tier Separation** - Analysis → Planning → Generation
2. **Pure Python > LLM for Evaluation** - Fast, deterministic, no API costs
3. **BestOfN for Options** - Generate N variations, select best
4. **Refine for Quality** - Self-improve until threshold
5. **ReAct for Discovery** - Scales to 100+ tools automatically
6. **Reward Functions Encode Knowledge** - Widget variety, device-aware, accessibility
7. **useEffect for Data Updates** - Don't calculate positions in render loop
8. **Drag Z-Index Matters** - Must exceed container z-index
9. **Backend Suggests, Frontend Controls** - Optional positions are hints, not requirements
10. **Table Support Needs Components** - Explicitly define markdown elements

---

## Recommended for Main System

1. **Three-tier architecture** - For all intelligent decision-making
2. **Pure Python reward functions** - For all evaluation/optimization
3. **ReAct for tool selection** - When scaling to 100+ tools
4. **BestOfN for option selection** - When multiple valid approaches exist
5. **Refine for quality improvement** - When quality thresholds exist
6. **Optional positioning** - Backend suggests, frontend has final say

---

**Last Updated**: 2026-01-21

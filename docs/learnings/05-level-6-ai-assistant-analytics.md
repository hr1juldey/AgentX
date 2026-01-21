# AGENTX Learnings: Level 6 Prototypes (R011-R014)

**Prototypes Covered**: R011 Personal Assistant, R012 Analytics Dashboard, R013 Travel Planning Stream, R014 UI Showcase
**Complexity Levels**: 6 (AI Assistant, Aggregation, Streaming with Memory, Generative UI)
**Total Build Time**: ~22 hours (R011: ~9h, R012: ~2h, R013: ~6h, R014: ~5h)
**Status**: All Working ✅

---

## Executive Summary

The Level 6 prototypes represent the culmination of AGENTX prototyping:
- **R011 Personal Assistant**: DSPy ReAct agent with voice interface, combining all previous patterns
- **R012 Analytics Dashboard**: Aggregation and visualization, mock data for demonstration
- **R013 Travel Planning Stream**: DSPy async + FastAPI WebSocket streaming with conversation memory
- **R014 UI Showcase**: Intelligent generative UI with three-tier DSPy architecture (ReAct + BestOfN + Refine)

These prototypes integrate all learned patterns and demonstrate production-ready architectures.

---

## R011: Personal Assistant (Level 6 - DSPy ReAct + Voice)

**Build Time**: ~9 hours (4 initial + 3 voice + 2 UI redesign)
**Status**: Working ✅

### What Worked

1. **DSPy ReAct Integration**
   - Built-in Ollama support (no separate package)
   - Tool calling (Calculator, Search, Weather)
   - Streaming responses with `dspy.streamify()`
   - Clean agent architecture

2. **Silero STT/TTS Integration**
   - Speech-to-text from R009
   - Text-to-speech from R009
   - GPU acceleration
   - Low latency

3. **WebSocket Voice Endpoint**
   - Real-time bidirectional voice conversation
   - Streaming text and audio
   - Session management
   - Clean state machine

4. **Voice Mode Toggle**
   - Switch between text and voice modes
   - UI state management
   - Recording indicator
   - Clean UX

### Key Lessons

1. **DSPy Has Built-in Ollama Support** - No separate package needed
2. **WebSocket Essential for Voice** - REST not suitable
3. **DSPy Streaming Works Well** - Token-by-token delivery
4. **MediaRecorder Chunking** - 1-second chunks optimal
5. **`.env` Overrides settings.py** - Must update both
6. **`gemma3:4b` Good Balance** - Speed and quality

---

## R012: Analytics Dashboard (Level 6 - Aggregation)

**Build Time**: ~2 hours
**Status**: Complete ✅

### What Worked

1. **NumPy/Pandas Aggregation** - Efficient array operations
2. **KPI Card Pattern** - Total, active, average metrics
3. **Time-Series Generation** - Chart-ready data structure
4. **Multi-Metric Summary** - Single aggregate endpoint
5. **Chart-Specific Endpoints** - Optimized per visualization

### Key Lessons

1. **NumPy/Pandas for Aggregation** - Built-in statistical functions
2. **Mock Metrics Strategy** - Random data sufficient for UI
3. **KPI Card Pattern** - Consistent format
4. **Time-Series Structure** - Date + value pairs

---

## R013: Travel Planning Stream (Level 6 - DSPy Async + WebSocket Streaming + Memory)

**Build Time**: ~2 hours (initial) + ~4 hours (Ralph Loop iterations)
**Status**: Working ✅

### What Worked

1. **DSPy Async + WebSocket Streaming**
   - `dspy.streamify()` for token-level real-time output
   - `dspy.streaming.StreamListener` with `allow_reuse=True`
   - Synchronous warmup before async streaming (critical pattern)

2. **Conversation History with `dspy.History`**
   - Server-side session manager for context persistence
   - Session ID passed via query parameter
   - History stored as `list[dict[str, Any]]` in `history.messages`

3. **Multi-Turn Conversation Flow**
   - 7-phase conversation: places → details → regions → transport → banter → variations → headcount change
   - 300-second conversation test: 9 turns, 100% success, 4,245 tokens

### Key Lessons

1. **DSPy `streamify` Requires Sync Warmup** - Must call the module synchronously before async streaming
2. **`dspy.History.messages` is a List** - Append dicts to `messages`, not to History directly
3. **Tool Definition Must Be Explicit** - Clear `name` and `desc` prevents argument hallucination
4. **Session Storage Required for History** - WebSocket closes after each request, need server-side storage

---

## R014: UI Showcase (Level 6 - Generative UI with Three-Tier Intelligence)

**Build Time**: ~5 hours (intelligent agent + UI fixes)
**Status**: Working ✅

### What Worked

1. **Three-Tier DSPy Architecture**
   - **Tier 1: Context Analyzer (ReAct)** - Detects content type, user intent, device context
   - **Tier 2: Presentation Planner (BestOfN)** - Generates 5 options, selects best via reward functions
   - **Tier 3: Enhanced Executor (Refine)** - Self-improves accessibility to WCAG AA

2. **Pure Python Reward Functions**
   - Fast evaluation (< 1ms vs 2-5s for LLM)
   - Deterministic (same input = same score)
   - No API costs
   - Easy to tune and debug

3. **No widget_type Required**
   - System automatically decides widget types
   - Device-aware layout selection (mobile vs desktop)
   - Automatic color scheme generation
   - Optional x, y positioning (backend suggests, frontend controls)

4. **Widget Positioning Improvements**
   - Centered cluster spawn (300x150 spread from center)
   - Random positioning within bounds
   - 100px right edge padding
   - 80px minimum spacing between widgets
   - Collision detection with 10 attempts

5. **Table Rendering Support**
   - Markdown widgets render tables properly
   - Card widgets support markdown content
   - ReactMarkdown with table components

6. **Multiple Widget Drag Fix**
   - Fixed z-index (9999 during drag)
   - All 3+ widgets independently draggable
   - Dragged positions persist

### Code Pattern: Three-Tier Architecture

```python
import dspy

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

        return dspy.Prediction(widgets=widgets, layout=plan.get("layout"), ...)
```

### Code Pattern: Pure Python Reward Function

```python
def presentation_quality_score(args: dict, pred: Any) -> float:
    """
    Evaluate presentation plan quality (0.0 to 1.0).
    Pure Python logic - no LLM calls. Deterministic and fast.
    """
    plan = json.loads(pred.presentation_plan)
    score = 0.0

    # Rule 1: Widget variety (0.2 points)
    widget_types = set(w.get('type', '') for w in plan.get('widgets', []))
    if len(widget_types) > 1:
        score += 0.2

    # Rule 2: Device-appropriate layout (0.3 points)
    device_type = args.get('device_context', {}).get('type', 'desktop')
    layout = plan.get('layout', '')

    if device_type == 'mobile':
        if layout in ['simple_vertical', 'single_column', 'stack']:
            score += 0.3
    else:
        if layout in ['grid_2column', 'grid_3column', 'masonry']:
            score += 0.3

    # Rule 3-5: Color accessibility, visual hierarchy, whitespace
    # ... (see reward_functions.py)

    return min(score, 1.0)
```

### Code Pattern: Centered Cluster Positioning

```typescript
// Only runs on data update
useEffect(() => {
  const positionedWidgetIds = new Set(Object.keys(islandPositions));
  const newWidgets = widgets.filter((w) => !positionedWidgetIds.has(w.descriptor_id));
  if (newWidgets.length === 0) return;

  // Positioning constants
  const SPREAD_X = 300;  // Horizontal spread
  const SPREAD_Y = 150;  // Vertical spread
  const PADDING_RIGHT = 100;  // Right edge padding
  const MIN_SPACING = 80;

  const newPositions: Record<string, { x: number; y: number }> = {};
  const existingPositions = Object.values(islandPositions);

  newWidgets.forEach((widget) => {
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
        newPositions[widget.descriptor_id] = { x: randomX, y: randomY };
        existingPositions.push({ x: randomX, y: randomY });
        return;
      }
    }

    // Fallback: center with slight offset
    newPositions[widget.descriptor_id] = {
      x: centerX + (Math.random() - 0.5) * 100,
      y: centerY + (Math.random() - 0.5) * 100,
    };
  });

  setIslandPositions((prev) => ({ ...prev, ...newPositions }));
}, [widgets]);  // Only runs when widgets array changes
```

### Code Pattern: Z-Index Fix for Drag

```typescript
// Problem: whileDrag zIndex: 50 was lower than container zIndex: 1000+
// Solution: Set whileDrag zIndex to 9999

<motion.div
  drag
  dragElastic={0.1}
  dragMomentum={false}
  dragConstraints={false}
  whileDrag={{ scale: 1.02, cursor: "grabbing", zIndex: 9999 }}  // Must be highest
  onDragEnd={handleDragEnd}
  style={{ x: dragPosition?.x || 0, y: dragPosition?.y || 0 }}
/>
```

### Code Pattern: Table Rendering in Markdown

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
    thead: ({ children }) => <thead className="bg-muted">{children}</thead>,
    tbody: ({ children }) => <tbody>{children}</tbody>,
    tr: ({ children }) => <tr className="border-b border-border">{children}</tr>,
    th: ({ children }) => <th className="px-4 py-2 text-left font-semibold">{children}</th>,
    td: ({ children }) => <td className="px-4 py-2">{children}</td>,
  }}
>
  {content}
</ReactMarkdown>
```

### What Didn't Work (And How We Fixed It)

#### Issue 1: Only 2 of 3 Widgets Draggable

**Problem**: When 3 widgets expanded, only 2 could be dragged. Had to collapse to drag more.

**Root Cause**: `whileDrag={{ zIndex: 50 }}` was much lower than container `zIndex: 1000 + index`.

**Solution**: Set `whileDrag={{ zIndex: 9999 }}` on all widgets so dragged widget always on top.

**Learning**: Dragging z-index must be higher than static z-index.

#### Issue 2: Markdown Tables Not Rendering

**Problem**: Tables showed raw markdown syntax instead of rendered HTML.

**Root Cause**: `ReactMarkdown` components didn't include table elements.

**Solution**: Added table components (table, thead, tbody, tr, th, td) to markdown-widget.tsx.

**Learning**: Explicitly define all markdown elements you need in components prop.

#### Issue 3: Widgets Spawning at Screen Edges

**Problem**: With 3+ widgets, they spread toward edges using formula `(index - (widgets.length - 1) / 2) * 80`.

**Root Cause**: Horizontal stacking from center without bounds.

**Solution**: Random cluster positioning with bounds (300x150 spread, 100px right padding) in useEffect.

**Learning**: Use useEffect for position generation, not render loop. Only update on data change.

#### Issue 4: Position Generation on Every Render

**Problem**: `generateRandomPosition` function was being recreated on every render.

**Root Cause**: Function was defined inside the map loop.

**Solution**: Move position generation to useEffect, only run when widgets array changes.

**Learning**: "Only rerender on data update, else save things."

### Performance Metrics

| Metric | Value |
|--------|-------|
| Backend startup | ~5s (LLM warmup included) |
| Intelligent generation | 5-8s (3-tier processing) |
| Context analysis | ~1-2s |
| Presentation planning (BestOfN) | ~2-3s (5 options) |
| Content generation (Refine) | ~2-3s (up to 3 refinements) |
| Widget spawn | Instant (from saved positions) |
| RAM usage | ~1.5 GB |

### Key Lessons

1. **Three-Tier Separation of Concerns** - Planning → Selection → Generation
2. **Pure Python > LLM for Evaluation** - Fast (< 1ms), deterministic, no API costs
3. **BestOfN Generates N Options** - 5 variations, reward function selects best
4. **Refine Self-Improves** - Iteratively improves until threshold met
5. **ReAct for Automatic Tool Selection** - Scales to 100+ tools
6. **useEffect for Position Generation** - Don't calculate positions in render loop
7. **Drag Z-Index Must Be Highest** - `whileDrag` z-index > container z-index
8. **Reward Functions Encode Design Knowledge** - Widget variety, device-appropriate, accessibility
9. **Centered Cluster > Edge Spawning** - Better UX with random positioning in bounds
10. **Table Support in Markdown** - Need explicit components for table elements

### Files Created/Modified

| File | Purpose | Lines |
|------|---------|-------|
| `services/widget_spawner/intelligent_agent.py` | Three-tier orchestrator | 127 |
| `services/widget_spawner/context_analyzer.py` | ReAct context analysis | 112 |
| `services/widget_spawner/presentation_planner.py` | BestOfN presentation planning | 102 |
| `services/widget_spawner/enhanced_executor.py` | Refine self-improvement | 88 |
| `services/widget_spawner/reward_functions.py` | Pure Python evaluation | 200+ |
| `services/widget_spawner/layout_utils.py` | Position generation logic | 150+ |
| `frontend/components/widgets/markdown-widget.tsx` | Tables + smooth drag | 128 |
| `frontend/components/widgets/card-widget.tsx` | Markdown + smooth drag | 82 |
| `frontend/components/widgets/chart-widget.tsx` | Smooth drag fix | 260 |
| `frontend/app/page.tsx` | Cluster positioning | 850+ |

---

## Cross-Prototype Patterns: DSPy in Production

### DSPy Pattern 1: Three-Tier Intelligence

**When to use**: Complex decision-making with multiple optimization criteria.

**Architecture**:
```
User Query
    ↓
Tier 1: ReAct (Context Understanding)
    - Automatic tool selection
    - Content analysis
    - Intent detection
    ↓
Tier 2: BestOfN (Option Generation)
    - Generate N variations
    - Reward function evaluation
    - Select best option
    ↓
Tier 3: Refine (Self-Improvement)
    - Generate output
    - Evaluate with reward function
    - Improve until threshold
    ↓
Final Result
```

**Benefits**:
- Separation of concerns
- Each tier independently optimizable
- Scales to complex decisions
- Pure Python reward functions

### DSPy Pattern 2: Reward Function Design

**Principles**:
1. **Pure Python** - No LLM calls in evaluation
2. **Deterministic** - Same input = same score
3. **Bounded** - Return 0.0 to 1.0
4. **Composable** - Multiple rules add up to total

**Example Structure**:
```python
def reward_function(args, pred) -> float:
    score = 0.0

    # Rule 1: 0.2 points
    if condition_1:
        score += 0.2

    # Rule 2: 0.3 points
    if condition_2:
        score += 0.3

    # ... more rules

    return min(score, 1.0)
```

### DSPy Pattern 3: Streaming with Sync Warmup

**Critical Pattern**: Always warm up DSPy modules synchronously before async streaming.

```python
# Create module
react = dspy.ReAct(signature, tools=tools)

# CRITICAL: Sync warmup first
_ = react(question="warmup", history=dspy.History(messages=[]))

# Then async streaming
stream_react = dspy.streamify(react, ...)

async for chunk in stream_react(question=q, history=history):
    # Handle streaming
    pass
```

---

## All 14 Prototypes Complete! ✅

| Prototype | Level | Status | Build Time | Key Innovation |
|-----------|-------|--------|------------|----------------|
| R001 | 1 | ✅ | ~1h | Basic CRUD |
| R002 | 1 | ✅ | ~1.5h | WebSocket basics |
| R003 | 2 | ✅ | ~1.5h | Multi-widget state |
| R004 | 2 | ✅ | ~1.5h | Time-series charts |
| R005 | 3 | ✅ | ~2h | Authentication |
| R006 | 3 | ✅ | ~2h | Sessions + encryption |
| R007 | 4 | ✅ | ~2h | Document RAG |
| R008 | 4 | ⚠️ | ~2h | Vector search |
| R009 | 5 | ✅ | ~6h | Voice pipeline |
| R010 | 5 | ✅ | ~6h | Vision |
| R011 | 6 | ✅ | ~9h | ReAct + voice |
| R012 | 6 | ✅ | ~2h | Analytics aggregation |
| R013 | 6 | ✅ | ~6h | Streaming + memory |
| R014 | 6 | ✅ | ~5h | **Three-tier intelligence** |
| **Total** | | | **~51 hours** | |

---

## Level 6 Summary: AI Assistant Patterns

### Key Achievements

1. **ReAct Agents** - Automatic tool selection without explicit instruction
2. **BestOfN Selection** - Generate N options, select best via reward functions
3. **Refine Self-Improvement** - Iteratively improve until threshold met
4. **Streaming Responses** - Real-time token delivery with `dspy.streamify()`
5. **Conversation Memory** - `dspy.History` for multi-turn context
6. **Three-Tier Architecture** - Separation: Analysis → Planning → Generation
7. **Pure Python Evaluation** - Fast, deterministic reward functions
8. **Intelligent UI Generation** - No widget_type required

### Production Readiness Checklist

| Pattern | R011 | R012 | R013 | R014 |
|---------|------|------|------|------|
| ReAct agents | ✅ | ❌ | ✅ | ✅ |
| Tool calling | ✅ | ❌ | ✅ | ✅ |
| Streaming | ✅ | ❌ | ✅ | ❌ |
| Memory/history | ❌ | ❌ | ✅ | ❌ |
| Multi-turn | ❌ | ❌ | ✅ | ❌ |
| Auto decision | ❌ | ❌ | ❌ | ✅ |
| Reward functions | ❌ | ❌ | ❌ | ✅ |

### Recommended for Main System

**From R011**:
- DSPy + Ollama integration pattern
- Tool calling framework
- Voice pipeline integration

**From R013**:
- Streaming with `dspy.streamify()`
- Session management
- Conversation memory

**From R014**:
- Three-tier intelligence architecture
- Pure Python reward functions
- BestOfN for option selection
- Refine for self-improvement
- Intelligent UI generation

---

**Last Updated**: 2026-01-21

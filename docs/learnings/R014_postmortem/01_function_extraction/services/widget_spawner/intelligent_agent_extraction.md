# Function Postmortem: services/widget_spawner/intelligent_agent.py

## Metadata
- **File**: services/widget_spawner/intelligent_agent.py
- **Lines of Code**: 126
- **Purpose**: Three-tier intelligent UI generator (no Mem0AI)
- **Dependencies**: `dspy`, `services.widget_spawner.context_analyzer`, `services.widget_spawner.presentation_planner`, `services.widget_spawner.enhanced_executor`

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE

**Purpose**: Three-tier orchestration for intelligent, automatic UI generation. No memory complexity - pure intelligence from DSPy patterns.

---

## Classes Extracted

### IntelligentUIGenerator

**Purpose**: Intelligent UI generator using three-tier architecture

**Signature**:
```python
class IntelligentUIGenerator(dspy.Module):
```

**Lines**: 22-125

**Architecture**: Three-tier DSPy Module

**Three Tiers**:
1. **Context Analyzer** - Understand the situation
2. **Presentation Planner** - Decide HOW to present
3. **Content Generators** - Create actual widgets

**Key Feature**: No Mem0AI - simple, direct, effective

---

### forward

**Purpose**: Generate intelligent UI based on user query

**Signature**:
```python
def forward(
    self, user_query: str, device_context: Dict[str, Any], user_id: str = None
) -> dspy.Prediction:
```

**Lines**: 39-125

**Key Code**:
```python
def forward(
    self, user_query: str, device_context: Dict[str, Any], user_id: str = None
) -> dspy.Prediction:
    """
    Generate intelligent UI based on user query.

    Args:
        user_query: User's natural language request
        device_context: Device info (type, screen_width, screen_height)
        user_id: Optional user ID (not used in this simple version)

    Returns:
        dspy.Prediction with widgets, layout, design_system, reasoning
    """
    logger.info(f"🤖 IntelligentUIGenerator processing: {user_query[:100]}")

    # Tier 1: Analyze context
    context = self.context_analyzer(
        user_query=user_query, device_context=device_context
    )
    logger.info(
        f"🔍 Tier 1 - Context: {getattr(context, 'content_analysis', 'N/A')}, Intent: {getattr(context, 'user_intent', 'N/A')}"
    )

    # Tier 2: Plan presentation
    presentation = self.presentation_planner(
        content_analysis=getattr(context, "content_analysis", "mixed"),
        user_intent=getattr(context, "user_intent", "general"),
        device_context=device_context,
    )

    # Parse the presentation plan
    try:
        plan = json.loads(getattr(presentation, "presentation_plan", "{}"))
        logger.info(f"📋 Tier 2 - Layout: {plan.get('layout', 'unknown')}")
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"📋 Failed to parse presentation plan: {e}")
        # Fallback plan
        plan = {
            "layout": "simple_vertical",
            "color_scheme": {},
            "widgets": [
                {
                    "type": "markdown",
                    "context": user_query[:100],
                    "priority": "medium",
                    "x": None,
                    "y": None,
                }
            ],
        }

    widgets = []

    for widget_spec in plan.get("widgets", []):
        widget = self.content_generator(
            widget_spec=widget_spec, design_system=plan.get("color_scheme", {})
        )

        # Create widget with optional positions
        widgets.append(
            {
                "id": str(uuid.uuid4()),
                "type": widget_spec.get("type"),
                "title": widget_spec.get("context", "")[:50],
                "content": widget.widget_content,
                "x": widget_spec.get("x"),  # Optional: backend suggestion
                "y": widget_spec.get("y"),  # Optional: backend suggestion
                "dismissible": True,
                "metadata": {
                    "layout": plan.get("layout"),
                    "design_system": plan.get("color_scheme", {}),
                    "priority": widget_spec.get("priority"),
                    "accessibility_score": widget.accessibility_score,
                },
            }
        )

    logger.info(f"✅ Tier 3 - Generated {len(widgets)} widgets")

    # Create prediction and set attributes directly
    prediction = dspy.Prediction()
    prediction.widgets = widgets
    prediction.layout = plan.get("layout", "simple_vertical")
    prediction.design_system = plan.get("color_scheme", {})
    prediction.reasoning = f"Analyzed as {getattr(context, 'content_analysis', 'mixed')}, intent: {getattr(context, 'user_intent', 'general')}"

    return prediction
```

**What Works**:
- ✅ Three-tier architecture (context → plan → generate)
- ✅ JSON parsing with exception handling
- ✅ Fallback plan on JSON parse failure
- ✅ UUID for widget IDs
- ✅ Optional x, y positioning (backend suggestions)
- ✅ Accessibility score in metadata
- ✅ Logging with emojis for clarity
- ✅ Returns dspy.Prediction with widgets, layout, design_system, reasoning

**Mistakes Found**: None

**Behavioral Notes**:
- Tier 1: Context Analyzer analyzes query + device context
- Tier 2: Presentation Planner decides layout + widgets
- Tier 3: Content Generators create actual widgets
- Fallback: simple_vertical layout with markdown widget on error
- Truncates title to 50 chars
- user_id parameter not used (reserved for future)

**Dependencies**:
- **Imports**: dspy, json, logging, uuid
- **Uses**: ContextAnalyzerAgent, PresentationPlannerAgent, EnhancedExecutorAgent
- **Returns**: dspy.Prediction with widgets, layout, design_system, reasoning

**Reusability**: HIGH - Three-tier UI generation pattern

---

## File Summary

**Total Classes**: 1
**Total Functions**: 1 method
**Lines of Code**: 126

**Violations**: None

**Success Patterns**:
- ✅ **Three-Tier Architecture**: Context → Plan → Generate
- ✅ **No Memory Complexity**: Pure DSPy intelligence (no Mem0AI)
- ✅ **JSON Parsing with Fallback**: Handles parse errors gracefully
- ✅ **Optional Positioning**: Backend suggests x, y for widgets
- ✅ **Accessibility Tracking**: accessibility_score in metadata
- ✅ **Emoji Logging**: Clear tier tracking in logs
- ✅ **UUID Widget IDs**: Unique identifiers for widgets
- ✅ **dspy.Prediction**: Standard DSPy return type

**Overall Assessment**: EXCELLENT - Clean three-tier UI generation.

**Key Learnings for Real AgentX**:
1. ✅ **Three-Tier Architecture**: Separate context, planning, generation
2. ✅ **No Memory Required**: Can use pure DSPy without Mem0AI
3. ✅ **JSON with Fallback**: Always provide fallback on parse error
4. ✅ **Backend Positioning**: Suggest x, y coordinates for frontend
5. ✅ **Accessibility Tracking**: Include accessibility_score
6. ✅ **Emoji Logging**: Use emojis for clear log tracking

**Reuse for Real AgentX**: ✅ HIGH - Three-tier pattern works well.

---

## Architectural Note

**Three-Tier UI Generation**:

**Tier 1: Context Analyzer**
- Input: user_query, device_context
- Output: content_analysis, user_intent
- Purpose: Understand the situation

**Tier 2: Presentation Planner**
- Input: content_analysis, user_intent, device_context
- Output: presentation_plan (JSON with layout, widgets)
- Purpose: Decide HOW to present

**Tier 3: Content Generators**
- Input: widget_spec, design_system
- Output: Actual widget content
- Purpose: Create the widgets

**Benefits**:
- Each tier has single responsibility
- Can swap out individual tiers
- Fallback is simple markdown widget
- No memory complexity required

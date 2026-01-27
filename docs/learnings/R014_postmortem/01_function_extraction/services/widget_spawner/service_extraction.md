# Function Postmortem: services/widget_spawner/service.py

## Metadata
- **File**: services/widget_spawner/service.py
- **Lines of Code**: 101
- **Purpose**: Widget Spawner Service - Two-agent pattern for widget generation
- **Dependencies**: `services.widget_spawner.executor`, `services.widget_spawner.planner`, `services.widget_spawner.models`

---

## Analysis

**File Status**: PRODUCTION SERVICE LAYER

**Purpose**: Service for managing DSPy widget generation using two-agent pattern (Planner + Executor).

---

## Classes Extracted

### WidgetSpawnerService

**Purpose**: Service for managing DSPy widget generation

**Signature**:
```python
class WidgetSpawnerService:
```

**Lines**: 12-85

**Architecture**: Two-agent pattern

**Two Agents**:
1. **WidgetPlannerAgent** - Decides WHAT widgets to spawn
2. **WidgetExecutorAgent** - Actually SPAWNS the widgets

**Separation of Concerns**:
- Planner: Decision making, intent analysis, widget selection
- Executor: Content generation, widget building

---

### __init__

**Purpose**: Initialize the widget spawner service

**Signature**:
```python
def __init__(self):
```

**Lines**: 27-34

**Key Code**:
```python
def __init__(self):
    """Initialize the widget spawner service.

    LLM configuration is handled by config/dspy.py, not here.
    """
    self._planner: WidgetPlannerAgent | None = None
    self._executor: WidgetExecutorAgent | None = None
    self._configured = False
```

**What Works**:
- ✅ Lazy initialization (agents created when needed)
- ✅ _configured flag for idempotency
- ✅ Type hints with Optional
- ✅ LLM config delegated to config/dspy.py

**Mistakes Found**: None

**Reusability**: HIGH - Service pattern with lazy initialization

---

### _ensure_configured

**Purpose**: Ensure DSPy agents are initialized

**Signature**:
```python
def _ensure_configured(self) -> None:
```

**Lines**: 36-47

**Key Code**:
```python
def _ensure_configured(self) -> None:
    """Ensure DSPy agents are initialized.

    Note: DSPy is already configured in api/routes.py at module level.
    We only need to initialize the agents here.
    """
    if not self._configured:
        # Decision agent: Decides what to create
        self._planner = WidgetPlannerAgent()
        # Execution agent: Creates the widgets
        self._executor = WidgetExecutorAgent()
        self._configured = True
```

**What Works**:
- ✅ Idempotent (checks _configured flag)
- ✅ Creates both agents on first call
- ✅ Clear comments explaining two-agent pattern

**Mistakes Found**: None

**Reusability**: HIGH - Lazy initialization pattern

---

### generate_widget

**Purpose**: Generate widget(s) based on the prompt

**Signature**:
```python
async def generate_widget(
    self, prompt: str, widget_type: str | None = None
) -> MultiWidgetGenerationResponse:
```

**Lines**: 49-85

**Complexity**: O(n) where n is number of widgets in plan

**Key Code**:
```python
async def generate_widget(
    self, prompt: str, widget_type: str | None = None
) -> MultiWidgetGenerationResponse:
    """Generate widget(s) based on the prompt.

    Uses the two-agent pattern:
    1. Planner analyzes prompt and decides what widgets are needed
    2. Executor generates each widget with appropriate content

    Args:
        prompt: User's prompt
        widget_type: Optional specific widget type to force (skips planning)

    Returns:
        Multi-widget response with all generated widgets
    """
    self._ensure_configured()
    assert self._planner is not None
    assert self._executor is not None

    # If widget_type is forced, skip planning and create single widget directly
    if widget_type is not None:
        plan = [{"type": widget_type, "context": prompt}]
    else:
        # Step 1: Plan what widgets to create
        plan_result = self._planner(user_query=prompt)
        plan = plan_result.plan

    # Step 2: Execute the plan and generate widgets
    widgets = self._executor.execute_plan(plan)

    return MultiWidgetGenerationResponse(
        widgets=widgets,
        tools_used=[item["type"] for item in plan],
        reasoning=f"Planned {len(plan)} widget(s): {', '.join([item['type'] for item in plan])}",
        preview_data={"plan": plan},
    )
```

**What Works**:
- ✅ Async method for non-blocking execution
- ✅ Two-agent pattern (planner + executor)
- ✅ Forced widget_type bypasses planning
- ✅ Assert statements for non-null agents
- ✅ Returns MultiWidgetGenerationResponse with reasoning
- ✅ preview_data includes plan for debugging

**Mistakes Found**: None

**Behavioral Notes**:
- If widget_type provided: Skip planning, use single widget
- If widget_type None: Use planner to decide widgets
- Two-step process: Plan → Execute
- Returns response with widgets + tools_used + reasoning

**Dependencies**:
- **Imports**: WidgetExecutorAgent, WidgetPlannerAgent, MultiWidgetGenerationResponse
- **Called by**: API routes, use cases
- **Returns**: MultiWidgetGenerationResponse

**Reusability**: HIGH - Two-agent service pattern

---

## Functions Extracted

### get_widget_spawner_service

**Purpose**: Get the singleton widget spawner service instance

**Signature**:
```python
def get_widget_spawner_service() -> WidgetSpawnerService:
```

**Lines**: 95-100

**Key Code**:
```python
_widget_spawner_service: WidgetSpawnerService | None = None

def get_widget_spawner_service() -> WidgetSpawnerService:
    """Get the singleton widget spawner service instance."""
    global _widget_spawner_service
    if _widget_spawner_service is None:
        _widget_spawner_service = WidgetSpawnerService()
    return _widget_spawner_service
```

**What Works**:
- ✅ Singleton pattern
- ✅ Global variable with type hint
- ✅ Lazy initialization
- ✅ Dependency injection friendly

**Mistakes Found**: None

**Reusability**: HIGH - Standard singleton getter pattern

---

## File Summary

**Total Classes**: 1
**Total Functions**: 2 methods + 1 getter
**Lines of Code**: 101

**Violations**: None

**Success Patterns**:
- ✅ **Two-Agent Pattern**: Planner decides WHAT, Executor creates HOW
- ✅ **Lazy Initialization**: Agents created on first use
- ✅ **Idempotent Config**: _configured flag prevents re-init
- ✅ **Forced Widget Type**: Bypasses planning when specified
- ✅ **Async Method**: Non-blocking widget generation
- ✅ **Singleton Getter**: Global + getter for DI
- ✅ **Response with Reasoning**: MultiWidgetGenerationResponse includes tools_used, reasoning, preview_data

**Overall Assessment**: EXCELLENT - Clean two-agent service pattern.

**Key Learnings for Real AgentX**:
1. ✅ **Two-Agent Pattern**: Separate planning from execution
2. ✅ **Lazy Initialization**: Create expensive objects on first use
3. ✅ **Idempotent Config**: Use flag to prevent re-initialization
4. ✅ **Forced Type**: Allow bypassing planner when type is known
5. ✅ **Response Reasoning**: Include tools_used, reasoning, preview_data
6. ✅ **Singleton Pattern**: Global + getter for dependency injection

**Reuse for Real AgentX**: ✅ HIGH - Two-agent service pattern is reusable.

---

## Architectural Note

**Two-Agent Pattern**:

**Planner Agent** (Decision Layer):
- Input: User query
- Output: Plan (list of widget types with context)
- Responsibility: WHAT widgets to create

**Executor Agent** (Execution Layer):
- Input: Plan (widget types + contexts)
- Output: Actual widgets with content
- Responsibility: HOW to create the widgets

**Benefits**:
- Clear separation of concerns
- Planner can be reused for different executors
- Executor can be tested independently
- Easy to add new widget types (only change executor)

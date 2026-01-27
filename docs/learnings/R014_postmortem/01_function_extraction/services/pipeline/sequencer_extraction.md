# Function Extraction: services/pipeline/sequencer.py

## File Overview
**Path**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/pipeline/sequencer.py`
**Purpose**: SEQUENCER Agent - Plans widget order and timing for narrative flow
**Lines**: 116
**Phase**: Phase 7 - What Order?

---

## Classes and Functions

### `SequencerAgent` (Class)

**Purpose**: DSPy Module that plans widget sequence and pacing for narrative flow.

**Signature**:
```python
class SequencerAgent(dspy.Module):
    def __init__(self):
        # Initializes 2 sequencing tools

    def forward(
        self,
        widgets: list,
        user_query: str = "",
        design: Optional[dict] = None,
    ) -> dict:
```

**Lines**: 24-115

**Key Code Snippet**:
```python
def forward(
    self,
    widgets: list,
    user_query: str = "",
    design: Optional[dict] = None,
) -> dict:
    design_data = design or {}
    visual_hierarchy = design_data.get(
        "visual_hierarchy", ["hero", "insights", "details"]
    )

    # Plan narrative flow
    logger.info("  [SEQUENCER] Planning narrative flow...")
    flow_result_raw = self.flow_planner(widgets=widgets, user_query=user_query)
    flow_result: dict = (
        flow_result_raw if hasattr(flow_result_raw, "get") else {}
    )

    sequence = (
        flow_result.get("sequence", widgets)
        if hasattr(flow_result, "get")
        else widgets
    )
    narrative_arc, is_valid = log_narrative_flow_result(flow_result)
    
    # Create sequence items with order
    sequence_items = []
    for i, widget in enumerate(sequence):
        widget_name = (
            widget.get("widget", widget) if isinstance(widget, dict) else widget
        )
        sequence_items.append(
            {
                "widget": widget_name,
                "order": i + 1,
            }
        )

    # Calculate pacing for staggered delivery
    pacing_result_raw = self.pacing_calculator(
        widgets=widgets,
        sequence=sequence_items,
    )
    pacing_result: dict = (
        pacing_result_raw if hasattr(pacing_result_raw, "get") else {}
    )

    total_duration = log_pacing_result(pacing_result, sequence)

    return {
        "sequence": sequence_for_plan,
        "narrative_arc": narrative_arc,
        "is_valid": is_valid,
        "total_duration": total_duration,
        "delivery_plan": create_delivery_plan(
            sequence_for_plan,
            visual_hierarchy,
        ),
    }
```

**What Works**:
1. **Safe fallbacks**: `design or {}` and `flow_result.get("sequence", widgets)`
2. **Type handling**: Handles both dict and string widget types
3. **Index-based ordering**: Simple `enumerate()` for order assignment
4. **Delegation**: Logging and delivery plan creation delegated to helpers

**Mistakes Found**:
- Inconsistent type annotation on flow_result assignment

**Behavioral Notes**:
- Creates narrative arc: hook → context → insight → action
- Calculates pacing for staggered delivery
- Maps widgets to visual hierarchy roles

**Dependencies**:
- `services.pipeline.sequencer_logging` - log_narrative_flow_result, log_pacing_result
- `services.pipeline.sequencer_utils` - create_delivery_plan
- `services.tools.sequencing_tools` - FlowPlannerModule, PacingCalculatorModule

**Reusability**: High - Generic sequencing for any widget list

---

## Helper Functions

### `create_delivery_plan()` (sequencer_utils.py)

**Purpose**: Create detailed delivery plan from sequence with visual roles.

**Signature**:
```python
def create_delivery_plan(
    sequence: List[Dict[str, Any]], 
    visual_hierarchy: List[str]
) -> List[Dict[str, Any]]:
```

**Lines**: sequencer_utils.py 10-46

**Key Code Snippet**:
```python
def create_delivery_plan(
    sequence: List[Dict[str, Any]], visual_hierarchy: List[str]
) -> List[Dict[str, Any]]:
    delivery_plan = []

    for item in sequence:
        widget = item.get("widget", "unknown")
        order = item.get("order", 1)
        delay = item.get("delay_sec", 0.0)

        # Determine visual role based on order and hierarchy
        if visual_hierarchy:
            role_index = min(order - 1, len(visual_hierarchy) - 1)
            visual_role = visual_hierarchy[role_index]
        else:
            visual_role = "standard"

        delivery_plan.append({
            "widget": widget,
            "order": order,
            "delay_sec": delay,
            "visual_role": visual_role,
            "delivery_type": "immediate" if delay == 0 else "staggered",
        })

    return delivery_plan
```

**What Works**:
- Maps order to visual hierarchy with bounds checking (`min()`)
- Determines delivery type from delay value

**Reusability**: High - Generic delivery plan creation

### `log_narrative_flow_result()` (sequencer_logging.py)

**Purpose**: Log narrative flow result and extract key data.

**Lines**: sequencer_logging.py 38-51

**Reusability**: Medium - Specific to sequencer logging

### `log_pacing_result()` (sequencer_logging.py)

**Purpose**: Log pacing result and extract total duration.

**Lines**: sequencer_logging.py 54-71

**Reusability**: Medium - Specific to sequencer logging

---

## Key Patterns

1. **Visual Hierarchy Mapping Pattern**:
```python
role_index = min(order - 1, len(visual_hierarchy) - 1)
visual_role = visual_hierarchy[role_index]
```

2. **Delivery Type Determination Pattern**:
```python
"delivery_type": "immediate" if delay == 0 else "staggered"
```

---

## Lessons Learned

1. **Bounds checking for hierarchy**: Use `min()` to prevent index errors when mapping to visual hierarchy
2. **Type flexibility**: Handle both dict and primitive types for widget representations
3. **Simple ordering**: Enumerate with 1-based indexing for user-friendly order display

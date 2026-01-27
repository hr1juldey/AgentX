# Function Extraction: services/pipeline/designer.py

## File Overview
**Path**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/pipeline/designer.py`
**Purpose**: DESIGNER Agent - Adds points of view, color schemes, visual hierarchy
**Lines**: 112
**Phase**: Phase 5 - POV + Color Schemes

---

## Classes and Functions

### `DesignerAgent` (Class)

**Purpose**: DSPy Module that generates design elements (POVs, colors, visual hierarchy) for presentation-ready output.

**Signature**:
```python
class DesignerAgent(dspy.Module):
    def __init__(self):
        # Initializes 5 design tools

    def forward(
        self,
        researched_data: dict,
        analysis: dict,
        widgets: Optional[list] = None,
    ) -> dict:
```

**Lines**: 24-111

**Key Code Snippet**:
```python
def forward(
    self,
    researched_data: dict,
    analysis: dict,
    widgets: Optional[list] = None,
) -> dict:
    query = researched_data.get("query", "")
    domain = analysis.get("domain", "general")
    insights = analysis.get("insights", [])

    # Generate balanced POVs
    povs_result_raw = self.pov_generator(
        query=query, researched_data=researched_data
    )
    povs_result = povs_result_raw if hasattr(povs_result_raw, "get") else {}

    # Pick color scheme based on domain
    color_result_raw = self.color_picker(query=query, domain=domain)
    color_result = color_result_raw if hasattr(color_result_raw, "get") else {}

    # Plan visual hierarchy
    widget_list = widgets or analysis.get("suggested_widgets", ["markdown"])
    hierarchy_result_raw = self.hierarchy_planner(widgets=widget_list, query=query)
    hierarchy_result = (
        hierarchy_result_raw if hasattr(hierarchy_result_raw, "get") else {}
    )

    # Check accessibility
    design_for_check = {
        "color_scheme": safe_get(color_result, "color_scheme", {}),
        "widgets": widget_list,
        "layout": safe_get(hierarchy_result, "layout", "narrative_focused"),
    }
    accessibility_result_raw = self.accessibility(design=design_for_check)
    accessibility_result = (
        accessibility_result_raw if hasattr(accessibility_result_raw, "get") else {}
    )

    # Generate widget-specific insights
    widget_insights = {}
    for widget_type in set(widget_list):  # Unique types only
        insights_result_raw = self.insights_generator(
            query=query,
            data=researched_data,
            widget_type=widget_type,
        )
        insights_result = (
            insights_result_raw if hasattr(insights_result_raw, "get") else {}
        )
        widget_insights[widget_type] = safe_get(insights_result, "insights", [])

    return build_designer_output(
        povs_result=povs_result,
        color_result=color_result,
        hierarchy_result=hierarchy_result,
        accessibility_result=accessibility_result,
        widget_insights=widget_insights,
        widget_list=widget_list,
        query=query,
        domain=domain,
        insights=insights,
    )
```

**What Works (Success Patterns)**:
1. **Safe DSPy result handling**: Uses `hasattr(result, "get")` pattern to handle both dict and object returns
2. **Fallback defaults**: `widgets or analysis.get("suggested_widgets", ["markdown"])` ensures robustness
3. **Set iteration**: `set(widget_list)` processes unique widget types only, avoiding duplicate work
4. **Delegated output building**: Uses `build_designer_output()` helper to keep method focused on orchestration
5. **Tool composition**: Combines 5 specialized tools (POV, color, hierarchy, accessibility, insights)

**Mistakes Found**:
None - clean orchestration pattern

**Behavioral Notes**:
- Generates multiple design dimensions in parallel (POV, color, hierarchy, accessibility)
- Creates widget-specific insights for each unique widget type
- Design output enriches researched data with visual presentation layer
- Domain-aware design (uses domain from analysis for color scheme selection)

**Dependencies**:
- `dspy.Module` - Base class for DSPy modules
- `services.pipeline.designer_helpers` - Helper functions for result processing
- `services.tools.designer` - Design tool modules (POVGeneratorModule, ColorPickerModule, etc.)
- `services.tools.designer.widget_insights` - WidgetInsightsModule

**Reusability**: High - Generic design orchestration that works with any researched data and analysis

---

## Imported Functions (from designer_helpers.py)

### `safe_get()`

**Purpose**: Safely get a value from a result object that may or may not have `.get()` method.

**Signature**:
```python
def safe_get(result: Any, key: str, default: Any = None) -> Any:
```

**Lines**: designer_helpers.py 15-28

**Key Code Snippet**:
```python
def safe_get(result: Any, key: str, default: Any = None) -> Any:
    if hasattr(result, "get"):
        return result.get(key, default)
    return default
```

**What Works**: Simple defensive programming for handling heterogeneous result types

**Reusability**: High - Generic utility for any DSPy result handling

### `get_povs_data()`

**Purpose**: Extract POV data from result with defaults.

**Signature**:
```python
def get_povs_data(povs_result: dict) -> dict[str, Any]:
```

**Lines**: designer_helpers.py 31-44

**Reusability**: Medium - Specific to POV data structure

### `get_color_data()`

**Purpose**: Extract color scheme data with sensible defaults.

**Signature**:
```python
def get_color_data(color_result: dict) -> dict[str, Any]:
```

**Lines**: designer_helpers.py 47-65

**What Works**: Provides fallback color scheme if result is empty

**Reusability**: Medium - Specific to color data structure

### `get_hierarchy_data()`

**Purpose**: Extract visual hierarchy data with fallback defaults.

**Signature**:
```python
def get_hierarchy_data(hierarchy_result: dict, widget_list: list) -> dict[str, Any]:
```

**Lines**: designer_helpers.py 68-84

**What Works**: Uses widget_list as fallback for priority_order

**Reusability**: Medium - Specific to hierarchy data structure

### `get_accessibility_data()`

**Purpose**: Extract accessibility data with WCAG compliance defaults.

**Signature**:
```python
def get_accessibility_data(accessibility_result: dict) -> dict[str, Any]:
```

**Lines**: designer_helpers.py 87-101

**What Works**: Defaults to WCAG compliant=True for safety

**Reusability**: Medium - Specific to accessibility data structure

### `build_designer_output()`

**Purpose**: Build final designer output from all module results using data extraction helpers.

**Signature**:
```python
def build_designer_output(
    povs_result: dict,
    color_result: dict,
    hierarchy_result: dict,
    accessibility_result: dict,
    widget_insights: dict,
    widget_list: list,
    query: str,
    domain: str,
    insights: list,
) -> dict[str, Any]:
```

**Lines**: designer_helpers.py 104-145

**What Works**:
- Uses dict unpacking (`**povs_data, **color_data`) for clean composition
- Delegates extraction to specialized getter functions
- Keeps output building separate from business logic

**Reusability**: High - Generic builder pattern for multi-tool results

---

## Key Patterns

1. **DSPy Result Handling Pattern**:
```python
result_raw = self.tool(param=value)
result = result_raw if hasattr(result_raw, "get") else {}
```
Handles both dict and object returns from DSPy modules

2. **Tool Orchestration Pattern**:
Execute multiple tools → Extract results → Build combined output

3. **Safe Fallback Pattern**:
`widgets or analysis.get("suggested_widgets", ["markdown"])` ensures valid value

4. **Set Processing Pattern**:
`for widget_type in set(widget_list)` avoids duplicate work

---

## Lessons Learned

1. **Separate output building from orchestration**: Using `build_designer_output()` keeps the forward() method focused on tool execution
2. **Type-safe DSPy integration**: Always use `hasattr()` checks before calling `.get()` on results
3. **Smart defaults**: Provide sensible fallbacks (like `["markdown"]`) for missing data
4. **Unique processing**: Use `set()` to avoid duplicate processing when iterating over items

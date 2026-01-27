# designer_helpers.py - Function Extraction

## File: services/pipeline/designer_helpers.py

### Primary Purpose
Helper utilities for processing DESIGNER agent results with safe data extraction from module outputs.

### Key Functions

#### `safe_get(result: Any, key: str, default: Any = None) -> Any`
**Purpose**: Safely retrieve values from potentially non-dict objects.

**Pattern**: Defensive programming - handles both dict-like and plain objects.

**Returns**: Value from result.get(key) if available, otherwise default.

---

#### `get_povs_data(povs_result: dict) -> dict[str, Any]`
**Purpose**: Extract Points of View module data.

**Returns**:
- `points_of_view`: List of different perspectives
- `balanced_povs`: Balanced perspective analysis
- `nuanced_analysis`: Nuanced insights

**Default behavior**: Empty list and empty string if missing.

---

#### `get_color_data(color_result: dict) -> dict[str, Any]`
**Purpose**: Extract color scheme data for UI styling.

**Returns**:
- `color_scheme`: Dict with primary/accent/background colors (default: blue_500/green_400/slate_900)
- `contrast_ratio`: WCAG contrast ratio (default: 7.0)

**Design intent**: Provides sensible defaults for color schemes.

---

#### `get_hierarchy_data(hierarchy_result: dict, widget_list: list) -> dict[str, Any]`
**Purpose**: Extract visual hierarchy for layout planning.

**Returns**:
- `visual_hierarchy`: Hierarchy list (default: ["hero", "insights", "details"])
- `priority_order`: Widget priority list (default: widget_list)
- `layout`: Layout type (default: "narrative_focused")

**Key insight**: Hierarchy drives widget placement in presentation.

---

#### `get_accessibility_data(accessibility_result: dict) -> dict[str, Any]`
**Purpose**: Extract WCAG accessibility compliance data.

**Returns**:
- `wcag_compliant`: Boolean compliance flag
- `contrast_ratio`: Contrast ratio value
- `contrast_passes`: Boolean pass/fail
- `size_issues`: List of size-related accessibility issues

---

#### `build_designer_output(...) -> dict[str, Any]`
**Purpose**: Aggregate all DESIGNER module results into final output.

**Parameters**:
- `povs_result`, `color_result`, `hierarchy_result`, `accessibility_result`
- `widget_insights`, `widget_list`
- `query`, `domain`, `insights`

**Returns**: Complete designer output dict with all modules combined.

**Pattern**: Compose final result from individual module extracts.

---

### Architectural Patterns

1. **Safe extraction pattern**: Each `get_*_data()` function uses `safe_get()` to handle missing data gracefully
2. **Default values**: All functions provide sensible defaults for missing data
3. **Composition**: `build_designer_output()` composes final result from individual extracts
4. **Type safety**: Uses `dict[str, Any]` for flexible return types

---

### Dependencies

**Internal**:
- None (standalone utilities)

**External**:
- `typing.Any`: Generic type hints

---

### Usage Example

```python
from services.pipeline.designer_helpers import build_designer_output

# After running individual modules
designer_output = build_designer_output(
    povs_result=povs_module_result,
    color_result=color_module_result,
    hierarchy_result=hierarchy_module_result,
    accessibility_result=accessibility_module_result,
    widget_insights=widget_specific_insights,
    widget_list=["chart", "text", "button"],
    query="show me sales data",
    domain="business",
    insights=analyst_insights
)

# Access aggregated data
color_scheme = designer_output["color_scheme"]
visual_hierarchy = designer_output["visual_hierarchy"]
```

---

### Key Insights

1. **Modular architecture**: DESIGNER is composed of independent modules (POVs, colors, hierarchy, accessibility)
2. **Graceful degradation**: Missing data from any module doesn't break the pipeline
3. **Sensible defaults**: Color schemes and hierarchies have fallback values
4. **Widget-driven**: Hierarchy and accessibility are tied to the widget list

---

### Integration Points

**Called by**:
- `services/pipeline/designer.py` (main DESIGNER agent orchestration)

**Calls**:
- None (pure utility functions)

---

### Testing Considerations

**Test scenarios**:
1. Safe extraction from dict with all fields
2. Safe extraction from dict with missing fields (uses defaults)
3. Safe extraction from non-dict objects
4. `build_designer_output()` with complete module results
5. `build_designer_output()` with partial/missing results

---

### Lessons Learned

1. **Helper module pattern**: Extracting data processing into separate helper files keeps main agent logic clean
2. **Defensive programming**: `safe_get()` prevents crashes when module outputs vary
3. **Default values are critical**: Provide sensible UI defaults (colors, layouts) when LLM outputs are incomplete
4. **Composability**: Each module's extraction is independent, making testing and debugging easier

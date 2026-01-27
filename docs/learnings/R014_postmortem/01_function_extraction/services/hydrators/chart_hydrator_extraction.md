# Function Postmortem: services/hydrators/chart_hydrator.py

## Metadata
- **File**: services/hydrators/chart_hydrator.py
- **Lines of Code**: 105
- **Purpose**: Chart Hydrator - Fills chart widgets with data + POV overlay
- **Dependencies**: `logging`, `uuid`, `datetime`, `typing`, `dspy`, `services.tools.hydrators`

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE

**Purpose**: Creates chart configurations with real data, POV overlays, and appropriate color schemes from the designer.

---

## Classes Extracted

### ChartHydrator

**Purpose**: DSPy module for hydrating chart widgets with researched data and POV overlays

**Signature**:
```python
class ChartHydrator(dspy.Module):
    def __init__(self):
```

**Lines**: 19-99

**Complexity**: O(n) where n is the number of chart data points

**Key Code**:
```python
def forward(
    self,
    presentation_ready: dict,
    researched_data: dict,
    design: dict,
) -> dict[str, Any]:
    """Hydrate chart widget with data.

    Args:
        presentation_ready: Output from PRESENTER agent
        researched_data: Research output from RESEARCHER/CONTEXTUALIZER
        design: Design output from DESIGNER agent

    Returns:
        Chart widget descriptor with hydrated content
    """
    beautiful_data = researched_data.get("beautiful_data", {})
    color_scheme = design.get("color_scheme", {})
    points_of_view = design.get("points_of_view", [])

    # Log what we received for debugging
    logger.info("  📊 [CHART HYDRATOR] Received data:")
    logger.info(f"      - beautiful_data keys: {list(beautiful_data.keys())}")
    logger.info(f"      - points_of_view: {len(points_of_view)} items")
    logger.info(
        f"      - color_scheme: {list(color_scheme.keys()) if color_scheme else 'none'}"
    )

    # Prepare data for hydration
    hydration_input = {
        "researched_data": {
            "beautiful_data": {
                "key_facts": beautiful_data.get("key_facts", []),
                "trends": beautiful_data.get("trends", {}),
                "comparisons": beautiful_data.get("comparisons", []),
                "extracted_numbers": beautiful_data.get("extracted_numbers", []),
            },
            "structured_data": researched_data.get("structured_data", {}),
        },
        "design": {
            "color_scheme": color_scheme,
            "points_of_view": points_of_view,
            "visual_hierarchy": design.get("visual_hierarchy", []),
        },
    }

    # Generate chart configuration
    chart_config = self.hydrator(presentation_ready=hydration_input)

    # Extract content from result (DSPy Predict returns special object)
    content = (
        chart_config.get("content", {}) if hasattr(chart_config, "get") else {}
    )

    # Extract metadata from tool module
    tool_metadata = (
        chart_config.get("metadata", {}) if hasattr(chart_config, "get") else {}
    )

    return {
        "id": str(uuid.uuid4())[:8],
        "type": "chart",
        "timestamp": datetime.utcnow().isoformat(),
        "content": content,
        "metadata": {
            "pov_count": len(points_of_view),
            "data_source": "researched",
            **tool_metadata,
        },
    }
```

**What Works**:
- ✅ DSPy Module pattern
- ✅ Extracts beautiful_data with nested structure (key_facts, trends, comparisons, extracted_numbers)
- ✅ POV overlay integration
- ✅ Color scheme integration
- ✅ Comprehensive logging for debugging
- ✅ Safe extraction with `hasattr` + `get`
- ✅ Metadata preservation (pov_count, data_source)
- ✅ Nested beautiful_data structure in hydration_input

**Mistakes Found**:
- ⚠️ `hasattr(chart_config, "get")` pattern suggests unclear data contract
- ⚠️ Nested "beautiful_data" key inside "researched_data" -> "beautiful_data" (redundant)

**Behavioral Notes**:
- Calls `ChartHydratorModule` from `services.tools.hydrators`
- Returns widget descriptor with: id, type, timestamp, content, metadata
- POV count tracked in metadata
- Truncated UUID (8 chars) for readability
- Comprehensive debugging logs (keys, counts)
- Supports trends, comparisons, extracted_numbers for rich chart data

**Dependencies**:
- **Imports**: `dspy`, `services.tools.hydrators.ChartHydratorModule`
- **Called by**: Master Agent pipeline (hydration phase)
- **Calls**: `ChartHydratorModule` (DSPy module for actual chart generation)

**Reusability**: HIGH - Chart hydration with POV overlay pattern

---

### create_chart_hydrator

**Purpose**: Factory function for ChartHydrator

**Signature**:
```python
def create_chart_hydrator() -> ChartHydrator:
```

**Lines**: 102-104

**Key Code**:
```python
def create_chart_hydrator() -> ChartHydrator:
    """Factory function for ChartHydrator."""
    return ChartHydrator()
```

**What Works**:
- ✅ Simple factory pattern
- ✅ Enables dependency injection

**Mistakes Found**: None

**Reusability**: HIGH - Standard factory pattern

---

## File Summary

**Total Classes**: 1
**Total Functions**: 1 (factory)
**Lines of Code**: 105

**Violations**: None

**Success Patterns**:
- ✅ DSPy Module wrapper pattern
- ✅ Factory function for dependency injection
- ✅ Safe data extraction (`hasattr` + `get`)
- ✅ Widget descriptor structure (id, type, timestamp, content, metadata)
- ✅ POV overlay integration
- ✅ Color scheme integration
- ✅ Comprehensive debugging logs
- ✅ Nested beautiful_data structure (key_facts, trends, comparisons, extracted_numbers)
- ✅ Metadata preservation (pov_count, data_source)

**Overall Assessment**: GOOD - Clean DSPy module wrapper for chart hydration with POV overlay.

**Key Learnings for Real AgentX**:
1. ✅ **Chart Hydration Pattern**: Separate module for filling charts with data + POV
2. ✅ **POV Overlay**: Charts can include multiple perspectives
3. ✅ **Nested Data Structures**: beautiful_data contains key_facts, trends, comparisons, extracted_numbers
4. ✅ **Color Scheme Integration**: Charts use designer's color scheme
5. ✅ **Comprehensive Logging**: Log keys and counts for debugging
6. ⚠️ **Data Contract Clarity**: `hasattr` checks suggest unclear return types

**Reuse for Real AgentX**: ✅ HIGH - Chart hydration with POV overlay pattern is reusable.

**Related to**: Other hydrators (card, markdown, gallery, image, form)

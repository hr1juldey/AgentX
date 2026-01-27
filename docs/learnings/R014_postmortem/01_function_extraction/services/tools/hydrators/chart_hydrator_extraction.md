# Function Postmortem: services/tools/hydrators/chart_hydrator.py

## Metadata
- **File**: services/tools/hydrators/chart_hydrator.py
- **Lines of Code**: 131
- **Purpose**: Orchestrates multiple DSPy signatures to build chart widgets
- **Dependencies**: dspy, logging, chart helper modules, color_palette

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE - COMPLEX ORCHESTRATION

**Purpose**: Comprehensive chart generation pipeline that orchestrates type selection, title generation, axis labeling, and data transformation.

---

## Classes Extracted

### ChartHydratorModule

**Purpose**: DSPy Module that orchestrates chart generation with helper modules for data analysis and transformation.

**Lines**: 28-113

**Key Code**:
```python
class ChartHydratorModule(dspy.Module):
    """Orchestrates chart type selection, title generation, and data transformation."""

    def __init__(self):
        super().__init__()
        self.type_selector = dspy.Predict(ChartTypeSelector)
        self.title_generator = dspy.Predict(ChartTitleGenerator)
        self.label_selector = dspy.Predict(AxisLabelSelector)

    def forward(self, presentation_ready: dict) -> dict:
        """Generate chart configuration using orchestrated signatures.

        Orchestrates:
        1. ChartTypeSelector - chooses bar/line/pie/etc
        2. ChartTitleGenerator - generates descriptive title
        3. AxisLabelSelector - selects axis labels
        4. Deterministic transform - converts extracted_numbers to chart data
        """
        # Extract data using helper
        extracted_numbers = extract_numbers_from_presentation_ready(presentation_ready)

        if not extracted_numbers:
            return _empty_chart()

        # Get design and query
        design = presentation_ready.get("design") or presentation_ready.get(
            "design_context", {}
        )
        query = presentation_ready.get("query", "")

        try:
            # Step 1: Select chart type
            data_sample = build_data_sample(extracted_numbers)
            type_result = self.type_selector(data_sample=data_sample, query=query)
            chart_type = getattr(type_result, "chart_type", "bar")

            # Step 2: Generate title
            data_context = build_data_context(extracted_numbers)
            title_result = self.title_generator(query=query, data_context=data_context)
            title = getattr(title_result, "title", "Chart")

            # Step 3: Select axis labels
            label_result = self.label_selector(
                data_sample=data_sample, chart_type=chart_type
            )
            x_label = getattr(label_result, "x_label", "Category")
            y_label = getattr(label_result, "y_label", "Value")

            # Step 4: Deterministically transform data (no LLM)
            chart_data = transform_extracted_numbers_to_chart_data(
                extracted_numbers=extracted_numbers,
                x_label=x_label,
                y_label=y_label,
            )

            # Get colors
            domain = design.get("domain", "general")
            colors = get_chart_colors(domain=domain, count=1)

            # Build content
            content = {
                "title": title,
                "type": chart_type,
                "data": chart_data,
                "x_axis": x_label,
                "y_axis": [y_label],
                "colors": colors,
                "metadata": {
                    "data_points": len(chart_data),
                    "chart_type": chart_type,
                },
            }

            return {
                "descriptor_type": "chart",
                "content": content,
                "metadata": {
                    "chart_type": chart_type,
                    "data_points": len(chart_data),
                },
            }

        except Exception as e:
            logger.error(f"Chart hydrator error: {e}")
            return _empty_chart()
```

**What Works**:
- ✅ Clear orchestration pattern (4 steps: type → title → labels → data)
- ✅ Early return pattern for empty data (_empty_chart())
- ✅ Separation of LLM and deterministic logic (step 4 is non-LLM)
- ✅ Helper functions for data preparation (build_data_sample, build_data_context)
- ✅ Dual design field fallback (design || design_context)
- ✅ Comprehensive error handling with fallback to empty chart

**Mistakes Found**:
- ⚠️ No validation that chart_type is valid (bar, line, pie, etc.)
- ⚠️ Assumes extracted_numbers is always list of dicts
- ⚠️ No retry logic if LLM fails partway through

**Behavioral Notes**:
- Uses helper modules for data extraction and transformation
- Each step builds on previous results (sequential orchestration)
- Returns descriptor_type for frontend routing
- Includes metadata in both content and top-level
- Graceful degradation to empty chart on any error

**Dependencies**:
- **Imports**: dspy, logging, extract_numbers_from_presentation_ready, build_data_context, build_data_sample, transform_extracted_numbers_to_chart_data, get_chart_colors
- **Uses**: dspy.Predict(), getattr(), dict.get(), try/except

**Reusability**: HIGH - Orchestration pattern applies to any multi-step widget generation

### _empty_chart (Helper Function)

**Purpose**: Returns empty chart configuration when no data available.

**Lines**: 115-130

**Key Code**:
```python
def _empty_chart() -> dict:
    """Return empty chart when no data available."""
    default_colors = get_chart_colors(domain="general", count=1)
    return {
        "descriptor_type": "chart",
        "content": {
            "title": "No Data Available",
            "type": "bar",
            "data": [],
            "x_axis": "Category",
            "y_axis": ["Value"],
            "colors": default_colors,
            "metadata": {"error": "No extracted numbers available"},
        },
        "metadata": {"error": "No extracted numbers available"},
    }
```

**What Works**:
- ✅ Consistent structure with successful return
- ✅ Clear error messaging in metadata
- ✅ Uses same helper functions (get_chart_colors) for consistency

---

## File Summary

**Total Classes**: 1
**Lines of Code**: 131

**Overall Assessment**: EXCELLENT orchestration pattern. This is a MASTERCLASS in multi-step DSPy pipeline design. The separation between LLM steps (type, title, labels) and deterministic steps (data transform) is ideal.

**Key Learnings for Real AgentX**:
1. ✅ Break complex widget generation into sequential steps (type → title → labels → data)
2. ✅ Use early return pattern for invalid inputs (empty data → empty widget)
3. ✅ Separate LLM operations from deterministic transformations
4. ✅ Create helper functions for data preparation (build_data_sample, build_data_context)
5. ✅ Use dual fallback for fields: `presentation_ready.get("design") or presentation_ready.get("design_context", {})`
6. ✅ Wrap entire orchestration in try/except with fallback
7. ✅ Include metadata at both content and top-level
8. ✅ Return descriptor_type for frontend routing
9. ⚠️ Validate enum values (chart_type should be checked against allowed types)

**Reuse for Real AgentX**: ✅ DIRECT - This is the GOLD STANDARD for widget hydrator orchestration

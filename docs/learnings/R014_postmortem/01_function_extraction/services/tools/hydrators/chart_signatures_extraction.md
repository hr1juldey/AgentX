# Function Postmortem: services/tools/hydrators/chart_signatures.py

## Metadata
- **File**: services/tools/hydrators/chart_signatures.py
- **Lines of Code**: 117
- **Purpose**: DSPy signatures for chart and table widget hydration
- **Dependencies**: dspy

---

## Analysis

**File Status**: PRODUCTION DSPy SIGNATURES

**Purpose**: Defines DSPy signatures for extracting numerical data and generating chart/table configurations.

---

## Signatures Extracted

### ExtractDocumentNumbers

**Purpose**: Extract query-relevant numerical data points from document text.

**Lines**: 12-36

**Key Code**:
```python
class ExtractDocumentNumbers(dspy.Signature):
    """Extract query-relevant numerical data points from document text.

    Focus on numbers that directly address the research query.
    Skip generic index data unless it relates to the query topic.

    For war economic impact queries, prioritize:
    - GDP changes (pre-war vs post-war)
    - Sanctions costs and economic penalties
    - Reconstruction spending
    - Casualty counts and refugee numbers
    - Trade volume changes
    - Currency devaluation
    - Defense spending increases

    Skip generic commodity prices unless they show war-related changes.
    """

    query = dspy.InputField(desc="Research query for context")
    document_text = dspy.InputField(desc="Document content to extract numbers from")
    document_title = dspy.InputField(desc="Document title for context")

    structured_numbers = dspy.OutputField(
        desc="JSON array of extracted numbers with label, numeric value, unit, context, and year"
    )
```

**What Works**:
- ✅ Detailed docstring with domain-specific examples (war economic impact)
- ✅ Contextual guidance on what to prioritize vs skip
- ✅ Output format: JSON array with label, value, unit, context, year
- ✅ Query-aware extraction (not all numbers, just query-relevant)

**Behavioral Notes**:
- Domain-specific examples in docstring improve extraction quality
- structured_numbers should be parseable as JSON

---

### ChartTypeSelector

**Purpose**: Select appropriate chart type based on data characteristics.

**Lines**: 39-49

**Key Code**:
```python
class ChartTypeSelector(dspy.Signature):
    """Select the appropriate chart type based on data characteristics."""

    data_sample = dspy.InputField(
        desc="Sample of extracted numbers showing data pattern"
    )
    query = dspy.InputField(desc="User query for context")

    chart_type = dspy.OutputField(
        desc="Chart type: bar, line, area, pie, radar, or radial"
    )
```

**What Works**:
- ✅ Enumerated chart types (bar, line, area, pie, radar, radial)
- ✅ Uses data_sample (not all data) for efficiency
- ✅ Query context for domain-aware selection

**Behavioral Notes**:
- Limited to 6 chart types (keeps output predictable)
- data_sample should show pattern (time series, categorical, etc.)

---

### ChartTitleGenerator

**Purpose**: Generate descriptive title for the chart.

**Lines**: 52-58

**Key Code**:
```python
class ChartTitleGenerator(dspy.Signature):
    """Generate a descriptive title for the chart."""

    query = dspy.InputField(desc="User query")
    data_context = dspy.InputField(desc="Brief description of what data shows")

    title = dspy.OutputField(desc="Chart title")
```

**What Works**:
- ✅ Simple signature
- ✅ Uses query + data_context for relevant title

---

### AxisLabelSelector

**Purpose**: Select appropriate axis labels based on data structure.

**Lines**: 61-68

**Key Code**:
```python
class AxisLabelSelector(dspy.Signature):
    """Select appropriate axis labels based on data structure."""

    data_sample = dspy.InputField(desc="Sample of extracted numbers")
    chart_type = dspy.InputField(desc="Selected chart type")

    x_label = dspy.OutputField(desc="X-axis label")
    y_label = dspy.OutputField(desc="Y-axis label")
```

**What Works**:
- ✅ Uses chart_type for context
- ✅ Separate x_label and y_label

**Behavioral Notes**:
- chart_type affects label selection (e.g., "Year" for line, "Category" for bar)

---

### TableData

**Purpose**: Generate table widget data from extracted numbers.

**Lines**: 71-86

**Key Code**:
```python
class TableData(dspy.Signature):
    """Generate table widget data from extracted numbers for structured display."""

    extracted_numbers = dspy.InputField(
        desc="Structured numbers with label, value, unit, context, year"
    )
    query = dspy.InputField(desc="User query for context")

    columns = dspy.OutputField(
        desc="JSON array of column definitions with key and header"
    )
    rows = dspy.OutputField(
        desc="JSON array of row objects with values matching column keys"
    )
    title = dspy.OutputField(desc="Table title")
```

**What Works**:
- ✅ Outputs column schema (key + header)
- ✅ Outputs rows as objects matching column keys
- ✅ Query context for relevant title

**Behavioral Notes**:
- columns define schema, rows contain data
- JSON format for easy frontend consumption

---

### transform_extracted_numbers_to_chart_data

**Purpose**: Deterministically transform extracted numbers to chart data points (NO LLM).

**Lines**: 88-117

**Key Code**:
```python
def transform_extracted_numbers_to_chart_data(
    extracted_numbers: list, x_label: str, y_label: str
) -> list:
    """Deterministically transform extracted numbers to chart data points.

    No LLM involved - pure Python transformation.

    Args:
        extracted_numbers: List of dicts with label, value, unit, context
        x_label: X-axis field name
        y_label: Y-axis field name

    Returns:
        List of chart data point dicts
    """
    chart_data = []
    for item in extracted_numbers:
        label = item.get("label", "")
        value = item.get("value", 0)

        # Try to convert value to float
        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            continue

        chart_data.append({x_label: label, y_label: numeric_value})

    return chart_data
```

**What Works**:
- ✅ Pure Python (no LLM) - deterministic and fast
- ✅ Graceful error handling (skip invalid values)
- ✅ Maps label → x_label, value → y_label
- ✅ Returns list of dicts for chart libraries

**Behavioral Notes**:
- Skips items with non-numeric values
- Uses item.get() for safe access
- Output format: [{x_label: label, y_label: numeric_value}, ...]

---

## File Summary

**Total Signatures**: 5
**Total Functions**: 1
**Lines of Code**: 117

**Overall Assessment**: Well-designed signature suite for chart/table generation. ExtractDocumentNumbers has excellent domain-specific guidance. transform_extracted_numbers_to_chart_data is a critical deterministic function.

**Key Learnings for Real AgentX**:
1. ✅ Domain-specific guidance: Detailed docstrings with examples improve LLM extraction
2. ✅ Query-aware extraction: Not all data, just query-relevant data
3. ✅ Enumerated outputs: Limited chart types keep output predictable
4. ✅ Deterministic transforms: Separate LLM logic (signatures) from deterministic transforms (functions)
5. ✅ Schema generation: TableData outputs both schema (columns) and data (rows)
6. ✅ Error handling: Skip invalid data gracefully in transforms

**Reuse for Real AgentX**: ✅ DIRECT - All signatures and transform function are reusable for any data visualization system.

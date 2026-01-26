# TODO: Option B - Enhanced Widget Selection with Number Analysis

**Status**: Future Enhancement - After Option A is complete and verified

---

## Overview

Option B enables the Widget Selector to analyze `extracted_numbers` directly, making smarter decisions about chart vs table vs markdown widgets based on actual data characteristics.

---

## Architecture Changes

### Data Flow
```
Researcher (extracts numbers + data_context)
    ↓
Widget Selector: Sees extracted_numbers + data_context
    → Analyzes: 5 countries, inflation rates, year 2023, comparable data
    → Decides: "chart" widget (data warrants visual comparison)
    ↓
Chart Hydrator: Same numbers + already-made decision
    → Fills chart data structure
```

---

## Implementation Tasks

### Phase 1: NumberExtractorModule with Context

#### 1. Update `services/tools/researcher/number_extractor.py`

**Add data_context generation:**

```python
def _analyze_data_context(self, extracted_numbers: list) -> dict:
    """Analyze extracted numbers to generate context for widget selection."""
    if not extracted_numbers:
        return {"number_count": 0}

    # Extract unique contexts
    contexts = set(n.get("context", "") for n in extracted_numbers)

    # Check temporal data
    has_years = any(n.get("year") for n in extracted_numbers)
    years = set(n.get("year") for n in extracted_numbers if n.get("year"))

    # Count items
    number_count = len(extracted_numbers)

    # Determine relationships
    if len(contexts) == 1:
        relationships = "comparable"  # All same context
    elif len(contexts) <= number_count / 2:
        relationships = "semi_comparable"
    else:
        relationships = "unrelated"

    # Determine time span
    if has_years:
        if len(years) == 1:
            time_span = "single_year"
        elif len(years) <= 3:
            time_span = "short_term"
        else:
            time_span = "long_term"
    else:
        time_span = "unknown"

    # Determine semantic intent from patterns
    labels = [n.get("label", "").lower() for n in extracted_numbers]
    if any(c in labels for c in ["us", "china", "europe", "japan"]):
        semantic_intent = "geographic_comparison"
    elif any(c in " ".join(labels) for c in ["jan", "feb", "mar", "apr"]):
        semantic_intent = "temporal_trend"
    elif relationships == "comparable":
        semantic_intent = "comparison"
    else:
        semantic_intent = "general"

    return {
        "number_count": number_count,
        "has_temporal_data": has_years,
        "relationships": relationships,
        "time_span": time_span,
        "semantic_intent": semantic_intent,
        "unique_contexts": len(contexts),
    }
```

**Update return statement:**

```python
def forward(self, raw_data: list) -> dict:
    # ... existing extraction logic ...

    data_context = self._analyze_data_context(extracted_numbers)

    return {
        "extracted_numbers": extracted_numbers,
        "data_context": data_context,  # NEW
        "metadata": {
            "total_numbers": len(extracted_numbers),
            "documents_processed": len(processed_docs),
            "extraction_method": "llm",
            "has_year_data": any(n.get("year") for n in extracted_numbers),
        },
    }
```

---

### Phase 2: Pipeline Flow Updates

#### 2. Update `services/pipeline/researcher_result.py`

**Include data_context and extracted_numbers in return:**

```python
def build_researcher_result(
    # ... existing params ...
    extracted_numbers: list = [],     # NEW
    data_context: dict = {},          # NEW
) -> dict:
    return {
        # ... existing fields ...
        "extracted_numbers": extracted_numbers,  # NEW
        "data_context": data_context,             # NEW
    }
```

#### 3. Update `services/pipeline/researcher_process.py`

**Extract and return numbers + context:**

```python
def process_research_data(
    beautifier,
    structurer,
    citer,
    raw_data: list,
    query_display: str,
) -> tuple:
    # ... existing beautification ...

    # Number Extraction
    number_extractor = NumberExtractorModule()
    number_data = number_extractor(raw_data=raw_data)
    extracted_numbers = number_data.get("extracted_numbers", [])
    data_context = number_data.get("data_context", {})  # NEW

    # Add to beautiful_data
    beautiful_data["extracted_numbers"] = extracted_numbers
    beautiful_data["data_context"] = data_context  # NEW

    # ... existing structuring and citations ...

    return beautiful_data, structured_data, citations, extracted_numbers, data_context  # NEW return values
```

#### 4. Update `services/pipeline/researcher.py`

**Capture and pass through pipeline:**

```python
# In forward() method
beautiful_data, structured_data, citations, extracted_numbers, data_context = process_research_data(...)

return build_researcher_result(
    # ... existing params ...
    extracted_numbers=extracted_numbers,
    data_context=data_context,
)
```

#### 5. Update `services/pipeline/data_contextualizer_builder.py`

**Preserve extracted_numbers and data_context:**

```python
def build_contextualized_return(
    # ... existing params ...
    researched_data: dict,
) -> Dict[str, Any]:
    return {
        # ... existing fields ...
        "extracted_numbers": researched_data.get("extracted_numbers", []),    # NEW
        "data_context": researched_data.get("data_context", {}),              # NEW
    }
```

#### 6. Update `services/pipeline/designer.py`

**Pass through to widget selector:**

```python
# In DesignerAgent.forward() return
return {
    # ... existing fields ...
    "extracted_numbers": researched_data.get("extracted_numbers", []),    # NEW
    "data_context": researched_data.get("data_context", {}),              # NEW
}
```

---

### Phase 3: Widget Selector Updates

#### 7. Update `services/tools/selector_tools.py`

**Update SelectWidgetSignature:**

```python
class SelectWidgetSignature(dspy.Signature):
    """Select appropriate widget type based on query and data characteristics."""

    query: str = dspy.InputField(desc="User query")
    data_type: str = dspy.InputField(desc="Data type classification")
    device_context: str = dspy.InputField(desc="Device type: mobile, desktop, tablet")
    extracted_numbers: list = dspy.InputField(   # NEW
        desc="Structured numbers from research. Each has label, value, unit, context, year."
    )
    data_context: dict = dspy.InputField(        # NEW
        desc="Analysis of extracted numbers: number_count, relationships, time_span, semantic_intent"
    )

    selected_widget: str = dspy.OutputField(
        desc="Selected widget type. "
        "Analyze data_context to decide: "
        "- number_count > 20 AND relationships != 'comparable' → table "
        "- number_count <= 15 AND relationships == 'comparable' → chart "
        "- number_count <= 5 → card "
        "- Else → markdown"
    )
    reasoning: str = dspy.OutputField(
        desc="Explanation for widget selection based on data characteristics"
    )
```

#### 8. Update `services/pipeline/widget_selector.py`

**Pass extracted_numbers to matcher:**

```python
# In WidgetMatcherModule.forward()
def forward(self, query: str, data_type: str, device_context: str,
            extracted_numbers: list = [],     # NEW
            data_context: dict = {}):         # NEW
    result = self.matcher(
        query=query,
        data_type=data_type,
        device_context=device_context,
        extracted_numbers=extracted_numbers,   # NEW
        data_context=data_context,            # NEW
    )
    # ... rest of logic
```

**In WidgetSelectorAgent.forward():**

```python
# Extract from designed_data
extracted_numbers = designed_data.get("extracted_numbers", [])
data_context = designed_data.get("data_context", {})

# Pass to matcher
selected_widgets = self.matcher(
    query=query,
    data_type=data_type,
    device_context=device_context,
    extracted_numbers=extracted_numbers,   # NEW
    data_context=data_context,            # NEW
)
```

---

## Decision Logic Examples

### Widget Selector Decision Table

| number_count | relationships | time_span | Widget Type | Reasoning |
|--------------|----------------|-----------|-------------|-----------|
| 1-5 | any | any | card | Single/few metrics |
| 6-15 | comparable | any | chart | Visual comparison |
| 6-15 | unrelated | any | table | Too complex for chart |
| 16-20 | comparable | any | chart or table | Data density |
| >20 | any | any | table | Too many for chart |
| any | comparable | long_term | line chart | Time series |
| any | comparable | single_year | bar chart | Snapshot comparison |
| any | comparable | semi_comparable | pie chart | Parts of whole |

---

## Testing Checklist

- [ ] Verify data_context is generated correctly
- [ ] Verify extracted_numbers flows through all pipeline stages
- [ ] Test widget selector with different data patterns:
  - [ ] 5 countries, inflation (single year) → bar chart
  - [ ] 25 metrics, unrelated → table
  - [ ] 3 metrics, comparable → card
  - [ ] Time series data → line chart
- [ ] Verify no data loss in pipeline
- [ ] Check ruff/pyrefly compliance

---

## Migration Path

1. Complete Option A (current plan)
2. Verify charts use real numbers
3. Implement Option B Phase 1 (data_context)
4. Implement Option B Phase 2 (pipeline flow)
5. Implement Option B Phase 3 (widget selector)
6. Test and verify smarter decisions

---

## Files Summary

| Phase | Files | Changes |
|-------|-------|---------|
| 1 | `number_extractor.py` | Add data_context generation (~50 lines) |
| 2 | `researcher_result.py`, `researcher_process.py`, `researcher.py` | Pass through pipeline (+35 lines) |
| 2 | `data_contextualizer_builder.py`, `designer.py` | Preserve data (+20 lines) |
| 3 | `selector_tools.py`, `widget_selector.py` | Analyze for decisions (+50 lines) |

**Total**: ~10 files, ~155 lines added/modified

---

## Option B: Frontend Chart Components (ShadCN)

**Status**: Future Enhancement - After Recharts implementation is complete

### Overview

Replace/customize the frontend chart components to use ShadCN chart components instead of Recharts. This provides better integration with the ShadCN ecosystem and more consistent styling.

### Implementation Tasks

1. **Install ShadCN Charts**: Add `@shadcn/recharts` package and dependencies
2. **Create Chart Components**: Build ShadCN-style chart components
   - AreaChart
   - BarChart
   - LineChart
   - PieChart
   - RadarChart
   - RadialChart
3. **Update ChartWidget**: Replace Recharts with ShadCN components
4. **Maintain API Compatibility**: Ensure backend chart data structure works with new components

### Files Summary

| File | Changes |
|------|---------|
| `package.json` | Add ShadCN charts dependencies |
| `components/widgets/ChartWidget.tsx` | Replace with ShadCN components |
| `components/ui/chart/` | New ShadCN chart component files |

**Estimated**: ~10 files, ~400 lines added/modified

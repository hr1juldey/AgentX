# Function Postmortem: services/tools/presenter/flow_checker.py

## Metadata
- **File**: services/tools/presenter/flow_checker.py
- **Lines of Code**: 46
- **Purpose**: Checks narrative flow and pacing of widget sequences
- **Dependencies**: dspy

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE

**Purpose**: Validates that widget sequences tell a coherent story and have appropriate timing/pacing.

---

## Classes Extracted

### FlowCheckerModule

**Purpose**: DSPy Module that analyzes narrative flow and validates pacing delays.

**Lines**: 10-46

**Key Code**:
```python
class FlowCheckerModule(dspy.Module):
    """Checks narrative flow and pacing.

    Has 2 signatures:
    - CheckNarrativeFlow: Check if widgets tell a coherent story
    - ValidatePacing: Check if pacing is appropriate
    """

    def __init__(self):
        super().__init__()
        self.check_flow = dspy.Predict("sequence, widgets -> flow_analysis, issues")
        self.validate_pacing = dspy.Predict("delays -> pacing_analysis, issues")

    def forward(self, sequence: list, widgets: list) -> dict:
        """Check narrative flow and pacing."""
        sequence_str = str(sequence)
        widgets_str = str(widgets)

        flow_result = self.check_flow(sequence=sequence_str, widgets=widgets_str)

        # Extract delays from sequence for pacing validation
        delays = [s.get("delay_sec", 0) for s in sequence]
        pacing_result = self.validate_pacing(delays=str(delays))

        return {
            "flow_analysis": flow_result.flow_analysis
            if hasattr(flow_result, "flow_analysis")
            else "Coherent flow",
            "flow_issues": flow_result.issues if hasattr(flow_result, "issues") else [],
            "pacing_analysis": pacing_result.pacing_analysis
            if hasattr(pacing_result, "pacing_analysis")
            else "Appropriate pacing",
            "pacing_issues": pacing_result.issues
            if hasattr(pacing_result, "issues")
            else [],
        }
```

**What Works**:
- ✅ List comprehension to extract delays from sequence dicts
- ✅ Safe dict.get() with default value (0) for missing keys
- ✅ Separate analysis and issues fields
- ✅ Sensible defaults for both analysis text and issues list

**Mistakes Found**:
- ⚠️ No validation that sequence items are dicts before calling .get()
- ⚠️ Issues field might be string instead of list (LLM unpredictability)
- ⚠️ No handling for negative or unrealistic delay values

**Behavioral Notes**:
- Converts lists to strings for LLM consumption
- Extracts specific numeric fields (delay_sec) from dict structures
- Returns paired analysis/issues for both flow and pacing
- Uses hasattr() for all attribute access

**Dependencies**:
- **Imports**: dspy
- **Uses**: dspy.Predict(), list comprehension, dict.get(), hasattr()

**Reusability**: HIGH - Pattern applies to any validation/checking with extracted fields

---

## File Summary

**Total Classes**: 1
**Lines of Code**: 46

**Overall Assessment**: CLEAN implementation with good field extraction pattern. The list comprehension for extracting delays is elegant but needs type checking. Issues field parsing could be more robust.

**Key Learnings for Real AgentX**:
1. ✅ Use list comprehensions to extract specific fields from dict lists
2. ✅ Always provide default values in dict.get() calls
3. ✅ Return paired analysis/issues for comprehensive validation
4. ⚠️ Add type checking in list comprehensions: `[s.get("delay", 0) for s in sequence if isinstance(s, dict)]`
5. ⚠️ Normalize issues field to always be a list (parse comma-separated strings)

**Reuse for Real AgentX**: ✅ DIRECT - Use the field extraction pattern for any validation requiring numeric analysis

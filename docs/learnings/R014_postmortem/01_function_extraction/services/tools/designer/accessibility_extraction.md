# Function Postmortem: services/tools/designer/accessibility.py

## Metadata
- **File**: services/tools/designer/accessibility.py
- **Lines of Code**: 53
- **Purpose**: Checks accessibility compliance (WCAG)
- **Dependencies**: dspy

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE

**Purpose**: Validates design accessibility including WCAG compliance, color contrast ratios, and tap target sizes.

---

## Classes Extracted

### AccessibilityModule

**Purpose**: DSPy Module that performs comprehensive accessibility checks on design specifications.

**Lines**: 10-53

**Key Code**:
```python
class AccessibilityModule(dspy.Module):
    """Checks accessibility compliance (WCAG).

    Has 3 signatures:
    - CheckWCAG: Check WCAG compliance
    - CheckContrast: Check color contrast ratios
    - CheckSizes: Check text and tap target sizes
    """

    def __init__(self):
        super().__init__()
        self.check_wcag = dspy.Predict("design -> wcag_compliance, issues")
        self.check_contrast = dspy.Predict("color_scheme -> contrast_ratio, passes")
        self.check_sizes = dspy.Predict("widget_types -> size_compliance")

    def forward(self, design: dict) -> dict:
        """Check accessibility compliance."""
        contrast_result = self.check_contrast(
            color_scheme=str(design.get("color_scheme", {}))
        )
        sizes_result = self.check_sizes(widget_types=str(design.get("widgets", [])))
        wcag_result = self.check_wcag(design=str(design))

        # Safely convert contrast_ratio to float
        contrast_ratio = 7.0  # default
        if hasattr(contrast_result, "contrast_ratio"):
            try:
                contrast_ratio = float(contrast_result.contrast_ratio)  # type: ignore[attr-defined]
            except (ValueError, TypeError):
                contrast_ratio = 7.0

        return {
            "wcag_compliant": wcag_result.wcag_compliance == "true"
            if hasattr(wcag_result, "wcag_compliance")
            else True,
            "contrast_ratio": contrast_ratio,
            "contrast_passes": contrast_result.passes == "true"
            if hasattr(contrast_result, "passes")
            else True,
            "size_issues": sizes_result.issues
            if hasattr(sizes_result, "issues")
            else [],
        }
```

**What Works**:
- ✅ Try/except block for safe float conversion
- ✅ Type ignore comment for mypy/pyrefly
- ✅ String comparison ("true") for LLM boolean outputs
- ✅ Safe dict.get() with defaults
- ✅ Multiple accessibility dimensions (WCAG, contrast, sizes)

**Mistakes Found**:
- ⚠️ LLM might return "True"/"False" (Python bools) not "true"/"false" (strings)
- ⚠️ No handling for case-insensitive boolean strings ("True", "TRUE", "true")

**Behavioral Notes**:
- Uses dict.get() with empty defaults to avoid KeyErrors
- Converts entire design dict to string for LLM
- Defaults to compliant=True (optimistic default)
- Returns structured dict with boolean and list fields

**Dependencies**:
- **Imports**: dspy
- **Uses**: dspy.Predict(), dict.get(), hasattr(), float() with try/except

**Reusability**: HIGH - Pattern applies to any validation/checking module

---

## File Summary

**Total Classes**: 1
**Lines of Code**: 53

**Overall Assessment**: SOLID implementation with proper error handling. The try/except for float conversion is production-ready. String comparison for booleans is fragile (should normalize first).

**Key Learnings for Real AgentX**:
1. ✅ Always use try/except when converting LLM strings to numbers
2. ✅ Use type ignore comments when mypy/pyrefly complain about dynamic attributes
3. ✅ Provide optimistic defaults for compliance checks (assume valid unless proven otherwise)
4. ⚠️ Normalize boolean strings before comparison (lowercase, strip whitespace)
5. ⚠️ Consider creating a helper function: `parse_bool(value: str) -> bool`

**Reuse for Real AgentX**: ✅ DIRECT - Use the try/except float conversion pattern for all numeric LLM outputs

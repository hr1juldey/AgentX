# Function Postmortem: services/tools/common/type_utils.py

## Metadata
- **File**: services/tools/common/type_utils.py
- **Lines of Code**: 92
- **Purpose**: Type conversion utilities for LLM outputs
- **Dependencies**: None

---

## Analysis

**File Status**: CRITICAL UTILITY MODULE

**Purpose**: Helper functions for LLM output type conversion with fallbacks. **ESSENTIAL** because LLMs return text instead of proper types.

---

## Functions Extracted

### _to_float

**Purpose**: Convert LLM output to float with fallbacks

**Signature**:
```python
def _to_float(value: str | float | bool | None, default: float = 0.5) -> float:
```

**Lines**: 8-61

**Complexity**: O(1) - conditional logic

**Key Code**:
```python
def _to_float(value: str | float | bool | None, default: float = 0.5) -> float:
    """Convert LLM output to float with fallbacks.

    Handles:
    - Already-float values
    - String floats ("0.75")
    - Text scores ("High" -> 0.9, "Medium" -> 0.5, "Low" -> 0.2)
    - Booleans (True -> 1.0, False -> 0.0)
    - Percentages ("75%" -> 0.75)

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Float value
    """
    if value is None:
        return default
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return default

    value_clean = value.strip().lower()

    # Text-based scores
    text_map = {
        "very high": 0.95,
        "high": 0.85,
        "good": 0.75,
        "medium": 0.50,
        "moderate": 0.50,
        "low": 0.25,
        "very low": 0.15,
        "poor": 0.20,
    }
    if value_clean in text_map:
        return text_map[value_clean]

    # Percentage format
    if "%" in value_clean:
        try:
            return float(value_clean.replace("%", "")) / 100.0
        except ValueError:
            pass

    # Direct float conversion
    try:
        return float(value_clean)
    except ValueError:
        return default
```

**What Works**:
- ✅ Handles 5 input types: None, bool, int, float, str
- ✅ Text score mapping (8 phrases)
- ✅ Percentage handling ("75%" -> 0.75)
- ✅ Boolean conversion (True -> 1.0, False -> 0.0)
- ✅ Default value for failed conversions
- ✅ Graceful fallback (try/except for float())

**Mistakes Found**: None

**Behavioral Notes**:
- Text mapping: "very high"=0.95, "high"=0.85, "good"=0.75, "medium"=0.5, "low"=0.25, "very low"=0.15, "poor"=0.2
- Percentage: removes % and divides by 100
- Booleans: True=1.0, False=0.0
- Default: 0.5 if all conversions fail

**Dependencies**:
- **Used by**: All DSPy modules that need numeric outputs
- **Critical for**: Confidence scores, quality scores, progress values

**Reusability**: CRITICAL - Required for all LLM interactions

---

### _to_bool

**Purpose**: Convert LLM output to bool with fallbacks

**Signature**:
```python
def _to_bool(value: str | bool | None, default: bool = False) -> bool:
```

**Lines**: 64-92

**Complexity**: O(1) - conditional logic

**Key Code**:
```python
def _to_bool(value: str | bool | None, default: bool = False) -> bool:
    """Convert LLM output to bool with fallbacks.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Boolean value
    """
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if not isinstance(value, str):
        return default

    value_clean = value.strip().lower()
    true_values = {"true", "yes", "1", "t", "y", "high", "good", "very high"}
    false_values = {"false", "no", "0", "f", "n", "low", "poor", "very low"}

    if value_clean in true_values:
        return True
    if value_clean in false_values:
        return False
    return default
```

**What Works**:
- ✅ Handles 4 input types: None, bool, int/float, str
- ✅ Text value mapping (8 true values, 8 false values)
- ✅ Numeric conversion (0=False, non-zero=True)
- ✅ Default value for failed conversions
- ✅ Case-insensitive matching

**Mistakes Found**: None

**Behavioral Notes**:
- True values: "true", "yes", "1", "t", "y", "high", "good", "very high"
- False values: "false", "no", "0", "f", "n", "low", "poor", "very low"
- Numbers: 0=False, any other number=True
- Default: False if no match

**Dependencies**:
- **Used by**: All DSPy modules that need boolean outputs
- **Critical for**: Flags, switches, yes/no questions

**Reusability**: CRITICAL - Required for all LLM interactions

---

## File Summary

**Total Functions**: 2
**Lines of Code**: 92

**Violations**: None

**Success Patterns**:
- ✅ **Type Conversion**: Handles all LLM output types
- ✅ **Text Mapping**: Maps common LLM phrases to values
- ✅ **Graceful Fallback**: Default value if conversion fails
- ✅ **Percentage Handling**: Special case for "75%" format
- ✅ **Case Insensitive**: All string comparisons use .lower()

**Overall Assessment**: CRITICAL - Essential utilities for LLM output handling.

**Key Learnings for Real AgentX**:
1. ✅ **LLMs Return Text**: Always use type converters, never trust types
2. ✅ **Text Mapping**: Map common phrases ("high", "medium", "low")
3. ✅ **Percentage Format**: Handle "75%" -> 0.75 conversion
4. ✅ **Boolean Values**: Map many text forms to bool (yes/no, high/low)
5. ✅ **Default Values**: Always provide sensible defaults (0.5 for float, False for bool)
6. ✅ **Graceful Failure**: try/except for numeric conversions

**Reuse for Real AgentX**: ✅ CRITICAL - Copy this file verbatim for all LLM interactions.

---

## LLM Behavior Notes

**Why This Is Needed**:
LLMs (especially small ones like gemma3:4b, qwen3:8b) return:
- Numbers as text: "0.75" instead of 0.75
- Scores as phrases: "High" instead of 0.85
- Booleans as text: "yes" instead of True
- Percentages as text: "75%" instead of 0.75

**Without these converters**, DSPy signatures will fail type checking or produce incorrect results.

**Recommendation**: Add these to ALL DSPy signature output fields that are not strings.

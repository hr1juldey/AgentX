# Function Postmortem: services/core/validation.py

## Metadata
- **File**: services/core/validation.py
- **Lines of Code**: 144
- **Purpose**: LLM response validation and parsing utilities
- **Dependencies**: `typing`, `re`

---

## Analysis

**File Status**: PRODUCTION INFRASTRUCTURE

**Purpose**: Provides utilities for validating and parsing LLM outputs, which are often unstructured text.

---

## Functions Extracted

### validate_output

**Purpose**: Validate LLM output and return fallback if invalid

**Signature**:
```python
def validate_output(
    output: Any,
    validator: Callable[[Any], bool],
    on_invalid: Optional[Callable[[], Any]] = None,
) -> Any
```

**Lines**: 11-30

**Complexity**: O(1) - single validator call

**Key Code**:
```python
def validate_output(
    output: Any,
    validator: Callable[[Any], bool],
    on_invalid: Optional[Callable[[], Any]] = None,
) -> Any:
    """Validate LLM output and return fallback if invalid.

    Args:
        output: LLM output to validate
        validator: Function that returns True if output is valid
        on_invalid: Optional fallback function if validation fails

    Returns:
        Validated output or fallback
    """
    if validator(output):
        return output
    if on_invalid:
        return on_invalid()
    return None
```

**What Works**:
- ✅ Generic validation pattern
- ✅ Callable-based validator (flexible)
- ✅ Optional fallback function
- ✅ Returns None if no fallback and validation fails

**Mistakes Found**: None

**Behavioral Notes**:
- If validator returns True, output is returned as-is
- If validator returns False and on_invalid provided, calls on_invalid()
- If validator returns False and no on_invalid, returns None

**Reusability**: HIGH - Generic validation wrapper

**Example Usage**:
```python
# Validate JSON parsing
def is_json(obj):
    try:
        json.loads(obj)
        return True
    except:
        return False

result = validate_output(
    llm_output,
    validator=is_json,
    on_invalid=lambda: '{"error": "invalid json"}'
)
```

---

### extract_list_from_text

**Purpose**: Extract list items from LLM text output

**Signature**:
```python
def extract_list_from_text(text: str) -> List[str]
```

**Lines**: 33-66

**Complexity**: O(n) where n is length of text

**Key Code**:
```python
def extract_list_from_text(text: str) -> List[str]:
    """Extract list items from LLM text output.

    Handles formats like:
    - "item1, item2, item3"
    - "- item1\\n- item2\\n- item3"
    - "1. item1\\n2. item2\\n3. item3"

    Args:
        text: Raw LLM output

    Returns:
        List of extracted items
    """
    if not text:
        return []

    # Try comma-separated first
    if "," in text and "\n" not in text:
        items = [item.strip() for item in text.split(",")]
        return [i for i in items if i]

    # Try bullet points
    bullet_items = re.findall(r"^[\-\*]\s+(.+)$", text, re.MULTILINE)
    if bullet_items:
        return [i.strip() for i in bullet_items]

    # Try numbered list
    numbered_items = re.findall(r"^\d+\.\s+(.+)$", text, re.MULTILINE)
    if numbered_items:
        return [i.strip() for i in numbered_items]

    # Fallback: split by newlines
    return [line.strip() for line in text.split("\n") if line.strip()]
```

**What Works**:
- ✅ Handles multiple list formats
- ✅ Comma-separated detection (checks for comma without newline)
- ✅ Bullet point parsing (`-` or `*`)
- ✅ Numbered list parsing (`1. ` format)
- ✅ Graceful fallback (newline split)
- ✅ Filters empty items

**Mistakes Found**:
- ⚠️ Doesn't handle `1)` format (only `1.`)
- ⚠️ Comma detection might fail on mixed formats ("item1, item2\nitem3")

**Behavioral Notes**:
- Priority: comma-separated > bullet points > numbered > newlines
- Regex uses `re.MULTILINE` for line-by-line matching
- Strips whitespace from all items

**Test Cases**:
| Input | Output | Method |
|-------|--------|--------|
| "a, b, c" | ["a", "b", "c"] | Comma-separated |
| "- a\n- b\n- c" | ["a", "b", "c"] | Bullet points |
| "1. a\n2. b\n3. c" | ["a", "b", "c"] | Numbered list |
| "a\nb\nc" | ["a", "b", "c"] | Newline fallback |
| "" | [] | Empty check |

**Reusability**: HIGH - Robust list extraction from LLM text

---

### parse_numbered_list

**Purpose**: Parse numbered list from LLM output

**Signature**:
```python
def parse_numbered_list(text: str) -> List[str]
```

**Lines**: 69-95

**Complexity**: O(n) where n is number of lines

**Key Code**:
```python
def parse_numbered_list(text: str) -> List[str]:
    """Parse numbered list from LLM output.

    Handles formats like:
    - "1. First item\\n2. Second item"
    - "1) First item\\n2) Second item"

    Args:
        text: Raw LLM output

    Returns:
        List of items (without numbers)
    """
    if not text:
        return []

    items = []
    for line in text.split("\n"):
        line = line.strip()
        # Match "1." or "1)" format at start of line
        match = re.match(r"^\d+[\.\)]\s*(.+)$", line)
        if match:
            items.append(match.group(1))
        elif line and not line[0].isdigit():  # Non-numbered lines
            items.append(line)

    return items
```

**What Works**:
- ✅ Handles both `1.` and `1)` formats
- ✅ Strips numbers from items
- ✅ Preserves non-numbered lines
- ✅ Filters empty lines

**Mistakes Found**:
- ⚠️ Includes non-numbered lines unconditionally (might include headers)
- ⚠️ No validation of numbering sequence (1, 2, 5 would be accepted)

**Behavioral Notes**:
- Regex: `^\d+[\.\)]\s*(.+)$` matches start of line
- Non-numbered lines included as-is (e.g., headers, descriptions)
- Leading/trailing whitespace stripped

**Test Cases**:
| Input | Output |
|-------|--------|
| "1. Apple\n2. Banana" | ["Apple", "Banana"] |
| "1) Apple\n2) Banana" | ["Apple", "Banana"] |
| "Header:\n1. Apple" | ["Header:", "Apple"] |
| "" | [] |

**Reusability**: HIGH - Specific to numbered lists

---

### parse_float_score

**Purpose**: Parse float score from LLM output with fallback

**Signature**:
```python
def parse_float_score(score_str: str, default: float = 0.0) -> float
```

**Lines**: 98-143

**Complexity**: O(n) where n is length of score_str

**Key Code**:
```python
def parse_float_score(score_str: str, default: float = 0.0) -> float:
    """Parse float score from LLM output with fallback.

    Handles formats like:
    - "0.75"
    - "The score is 0.75"
    - "75%"

    Args:
        score_str: String containing a score
        default: Default value if parsing fails

    Returns:
        Parsed float value or default
    """
    if not score_str:
        return default

    # Try direct float conversion
    try:
        return float(score_str.strip())
    except ValueError:
        pass

    # Try to extract a number using regex
    match = re.search(r"0?\.\d+|1\.0|0|1|\d+%", score_str)
    if match:
        try:
            value = float(match.group().rstrip("%"))
            # Handle percentages
            if "%" in match.group() and value > 1:
                return value / 100.0
            return value
        except ValueError:
            pass

    # Fallback: check for qualitative indicators
    lower = score_str.lower()
    if any(word in lower for word in ["high", "very", "strong", "excellent"]):
        return 0.8
    if any(word in lower for word in ["medium", "moderate", "good"]):
        return 0.5
    if any(word in lower for word in ["low", "weak", "poor"]):
        return 0.2

    return default
```

**What Works**:
- ✅ Multiple format handling (direct, embedded, percentage)
- ✅ Graceful fallback to keyword matching
- ✅ Percentage conversion (75% → 0.75)
- ✅ Default value support
- ✅ Qualitative word mapping

**Mistakes Found**:
- ⚠️ Regex `r"0?\.\d+|1\.0|0|1|\d+%"` doesn't match integers >1 without %
- ⚠️ Qualitative mapping is hardcoded (not configurable)
- ⚠️ Doesn't handle negative scores

**Behavioral Notes**:
- Priority: direct float → regex extraction → keywords → default
- Keywords: "high/very/strong/excellent" → 0.8
- Keywords: "medium/moderate/good" → 0.5
- Keywords: "low/weak/poor" → 0.2
- Percentage >1 becomes fraction (75% → 0.75)

**Test Cases**:
| Input | Output | Method |
|-------|--------|--------|
| "0.75" | 0.75 | Direct float |
| "Score: 0.85" | 0.85 | Regex extraction |
| "75%" | 0.75 | Percentage |
| "High relevance" | 0.8 | Keyword mapping |
| "Medium quality" | 0.5 | Keyword mapping |
| "Low score" | 0.2 | Keyword mapping |
| "xyz" | 0.0 (default) | Default |
| "" | 0.0 (default) | Empty check |

**Reusability**: HIGH - Essential for LLM numeric parsing

**Related to**: `_to_float` in `services/tools/common/type_utils.py` (similar but more comprehensive)

---

## File Summary

**Total Functions**: 4
**Total Classes**: 0
**Lines of Code**: 144

**Violations**: None

**Success Patterns**:
- ✅ Generic validation wrapper (`validate_output`)
- ✅ Multiple format parsing (`extract_list_from_text`)
- ✅ Numbered list parsing (`parse_numbered_list`)
- ✅ Numeric score parsing with fallback (`parse_float_score`)
- ✅ Graceful degradation (always returns valid result)
- ✅ Comprehensive docstrings with examples
- ✅ Type hints throughout

**Overall Assessment**: EXCELLENT - Robust LLM output parsing utilities with multiple fallback strategies.

**Key Learnings for Real AgentX**:
1. ✅ **Validation Wrapper**: Use `validate_output` pattern for all LLM outputs
2. ✅ **List Extraction**: LLMs return lists in many formats - handle them all
3. ✅ **Numeric Parsing**: Always use regex + keyword + default fallback
4. ✅ **Graceful Degradation**: Never crash on LLM output variations
5. ⚠️ **Function Duplication**: `parse_float_score` similar to `_to_float` - consolidate

**Reuse for Real AgentX**: ✅ REQUIRED - All 4 functions are essential for LLM output processing.

**Refactoring Needed**: MAYBE - Consolidate `parse_float_score` with `_to_float` from type_utils.py

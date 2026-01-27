# Function Postmortem: services/pipeline/researcher_helpers.py

## Metadata
- **File**: services/pipeline/researcher_helpers.py
- **Lines of Code**: 60
- **Purpose**: RESEARCHER helper methods for summary and data type
- **Dependencies**: None

---

## Analysis

**File Status**: PRODUCTION HELPER MODULE

**Purpose**: Summary report generation and data type determination for widget selection.

---

## Functions Extracted

### generate_summary_report

**Purpose**: Generate a summary report from research

**Signature**:
```python
def generate_summary_report(
    beautiful_data: dict,
    citations: list,
    domain: str,
) -> str:
```

**Lines**: 8-36

**Key Code**:
```python
def generate_summary_report(
    beautiful_data: dict,
    citations: list,
    domain: str,
) -> str:
    """Generate a summary report from research.

    Args:
        beautiful_data: Beautified research data
        citations: Citation list
        domain: Domain/subject area

    Returns:
        Summary report string
    """
    parts = []

    key_facts = (
        beautiful_data.get("key_facts", []) if hasattr(beautiful_data, "get") else []
    )
    trends = beautiful_data.get("trends", []) if hasattr(beautiful_data, "get") else []

    if key_facts:
        parts.append("Key findings: " + ", ".join(key_facts[:3]))

    if trends:
        parts.append("Trends: " + ", ".join(trends[:3]))

    return " | ".join(parts) if parts else f"Research completed for {domain}"
```

**What Works**:
- ✅ Extracts key_facts and trends
- ✅ Limits to top 3 each ([:3])
- ✅ Separator format (" | ")
- ✅ Fallback if no parts
- ✅ Safe extraction with hasattr

**Mistakes Found**:
- ⚠️ Cititions parameter unused (typo in original: citations)

**Behavioral Notes**:
- Format: "Key findings: X, Y, Z | Trends: A, B, C"
- Fallback: "Research completed for {domain}" if no data

**Reusability**: HIGH - Summary report pattern

---

### determine_data_type

**Purpose**: Determine the type of data for widget selection

**Signature**:
```python
def determine_data_type(analysis: dict, beautiful_data: dict) -> str:
```

**Lines**: 39-59

**Key Code**:
```python
def determine_data_type(analysis: dict, beautiful_data: dict) -> str:
    """Determine the type of data for widget selection.

    Args:
        analysis: Analysis result from ANALYST agent
        beautiful_data: Beautified research data

    Returns:
        Data type string
    """
    query = analysis.get("query", "").lower()
    domain = analysis.get("domain", "").lower()

    if "price" in query or "stock" in query or "finance" in domain:
        return "numerical_time_series"
    if "image" in query or "photo" in query:
        return "visual_image"
    if "comparison" in query:
        return "comparative"

    return "general"
```

**What Works**:
- ✅ Keyword-based classification
- ✅ Checks both query and domain
- ✅ Case-insensitive (lower())
- ✅ Returns 4 data types

**Mistakes Found**:
- ⚠️ beautiful_data parameter unused
- ⚠️ Hardcoded keywords (not extensible)

**Behavioral Notes**:
- Returns: "numerical_time_series", "visual_image", "comparative", "general"
- Keywords: price/stock/finance → time series
- Keywords: image/photo → visual
- Keywords: comparison → comparative
- Default: "general"

**Reusability**: MEDIUM - Simple keyword matching

---

## File Summary

**Total Functions**: 2
**Lines of Code**: 60

**Violations**: None

**Success Patterns**:
- ✅ Summary report with key_facts + trends
- ✅ Top N limiting ([:3] for brevity)
- ✅ Separator format (" | ")
- ✅ Keyword-based data type detection
- ✅ Case-insensitive matching

**Overall Assessment**: GOOD - Simple helpers for research processing.

**Key Learnings for Real AgentX**:
1. ✅ **Summary Format**: "Key findings: X | Trends: Y"
2. ✅ **Top N Limiting**: [:3] for brevity
3. ✅ **Keyword Detection**: Simple substring matching
4. ⚠️ **Unused Parameters**: Remove unused params
5. ⚠️ **Hardcoded Keywords**: Consider configurable keyword lists

**Reuse for Real AgentX**: ⚠️ MODERATE - Useful patterns but needs improvement.

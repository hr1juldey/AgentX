# Function Postmortem: services/tools/selector_tools.py

## Metadata
- **File**: services/tools/selector_tools.py
- **Lines of Code**: 116
- **Purpose**: Widget selector DSPy modules for semantic widget matching
- **Dependencies**: `dspy`

---

## Analysis

**File Status**: PRODUCTION DSPy MODULES

**Purpose**: DSPy modules used by WidgetSelectorAgent to match widgets using semantic understanding, not hard-coded rules.

---

## Classes Extracted

### SelectWidgetSignature

**Purpose**: DSPy Signature for widget selection with semantic patterns

**Lines**: 10-67

**Key Features**:
- 5 semantic few-shot examples
- Data types: numerical_time_series, visual_image, comparative, general, temporal
- Device context: mobile, desktop, tablet
- 1-3 widgets output (comma-separated)
- Rationale field for explainability

**What Works**:
- ✅ Few-shot learning with 5 examples
- ✅ Clear semantic patterns
- ✅ Explainability via rationale

**Reusability**: HIGH - Semantic few-shot pattern

---

### WidgetMatcherModule

**Purpose**: Match widgets using semantic understanding

**Lines**: 70-115

**VALID_WIDGETS** (13 types):
chart, markdown, gallery, card, form, image, map, clock, calendar, calculator, media controls, opengraph-card, opengraph-gallery

**What Works**:
- ✅ ChainOfThought for reasoning
- ✅ Validates LLM output
- ✅ Filters invalid widgets
- ✅ Fallback to ["markdown"]

**Reusability**: HIGH - Semantic selection with validation

---

## Key Learnings

1. Few-shot examples in signature docstring
2. Always validate LLM output
3. Fallback to safe default
4. Include rationale for explainability

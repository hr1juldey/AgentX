# Function Extraction: services/tools/analyst/signatures.py

## File Overview
**Path**: `/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R014_ui_showcase/backend/services/tools/analyst/signatures.py`
**Purpose**: Type-safe DSPy signatures for analyst tools
**Lines**: 70

---

## DSPy Signatures

### `ExtractInitialInsights` (Signature)

**Purpose**: Extract key insights from a text chunk.

**Signature**:
```python
class ExtractInitialInsights(dspy.Signature):
    text_chunk: str = dspy.InputField(desc="Text to analyze (500 chars)")
    insights: str = dspy.OutputField(
        desc="Key insights from text, one per line starting with '- '"
    )
```

**Lines**: 10-19

**What Works**:
- Clear output format specification ("one per line starting with '- '")
- Length hint in input field description

**Reusability**: High - Generic insight extraction signature

---

### `RefineInsights` (Signature)

**Purpose**: Refine insights using context from previous passes.

**Signature**:
```python
class RefineInsights(dspy.Signature):
    text_chunk: str = dspy.InputField(desc="Text to analyze")
    existing_insights: str = dspy.InputField(
        desc="Previously found insights (comma-separated)"
    )
    new_insights: str = dspy.OutputField(
        desc="2-3 additional insights NOT in existing list, one per line starting with '- '"
    )
```

**Lines**: 22-35

**What Works**:
- Explicitly states "NOT in existing list" to avoid duplicates
- Builds on previous context for iterative refinement

**Reusability**: High - Generic insight refinement signature

---

### `AssessCompletenessSignature` (Signature)

**Purpose**: Assess if research data is complete for answering the user query.

**Signature**:
```python
class AssessCompletenessSignature(dspy.Signature):
    query: str = dspy.InputField(desc="User query to evaluate")
    data: str = dspy.InputField(desc="Research data to assess")
    completeness_score: float = dspy.OutputField(
        desc="Completeness score from 0.0 to 1.0"
    )
    missing_elements: str = dspy.OutputField(desc="Description of missing information")
```

**Lines**: 38-47

**What Works**:
- Type-annotated output (`float`) for numeric score
- Clear range specification (0.0 to 1.0)
- Provides both score and explanation

**Reusability**: High - Generic completeness assessment signature

---

### `AssessRelevanceSignature` (Signature)

**Purpose**: Assess if research data is relevant to the user query.

**Signature**:
```python
class AssessRelevanceSignature(dspy.Signature):
    query: str = dspy.InputField(desc="User query")
    data: str = dspy.InputField(desc="Research data to evaluate")
    relevance_score: float = dspy.OutputField(desc="Relevance score from 0.0 to 1.0")
    relevance_explanation: str = dspy.OutputField(
        desc="Explanation of relevance assessment"
    )
```

**Lines**: 50-59

**What Works**:
- Type-annotated output for numeric score
- Provides both score and explanation

**Reusability**: High - Generic relevance assessment signature

---

### `DecideResearchSignature` (Signature)

**Purpose**: Decide if more research is needed based on current data quality.

**Signature**:
```python
class DecideResearchSignature(dspy.Signature):
    completeness_score: float = dspy.InputField(desc="Current completeness score")
    relevance_score: float = dspy.InputField(desc="Current relevance score")
    needs_more_research: bool = dspy.OutputField(desc="Whether more research is needed")
    reason: str = dspy.OutputField(desc="Reason for the decision")
```

**Lines**: 62-69

**What Works**:
- Type-annotated inputs (float scores) for type safety
- Boolean output for clear decision
- Provides reason for explainability

**Reusability**: High - Generic research decision signature

---

## Key Patterns

1. **Type-Annotated Output Pattern**:
```python
completeness_score: float = dspy.OutputField(desc="Completeness score from 0.0 to 1.0")
needs_more_research: bool = dspy.OutputField(desc="Whether more research is needed")
```

2. **Range Specification Pattern**:
```python
desc="Score from 0.0 to 1.0"
```

3. **Explainable Output Pattern**:
```python
completeness_score: float = dspy.OutputField(...)
missing_elements: str = dspy.OutputField(desc="Description of missing information")
```

---

## Lessons Learned

1. **Use type annotations for numeric/boolean outputs**: Improves LLM consistency
2. **Specify ranges for numeric scores**: "from 0.0 to 1.0" guides LLM output
3. **Provide both score and explanation**: Makes decisions explainable
4. **Use explicit negative constraints**: "NOT in existing list" prevents duplicates
5. **Specify output format clearly**: "one per line starting with '- '" ensures consistent parsing

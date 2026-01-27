# Function Postmortem: services/tools/hydrators/markdown_hydrator.py

## Metadata
- **File**: services/tools/hydrators/markdown_hydrator.py
- **Lines of Code**: 50
- **Purpose**: Hydrates markdown widgets with content
- **Dependencies**: dspy, number_extractor_utils

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE

**Purpose**: Generates markdown content from research data, POVs, and citations with wrapper stripping.

---

## Classes Extracted

### MarkdownHydratorModule

**Purpose**: DSPy Module that generates markdown content and strips code block wrappers.

**Lines**: 12-50

**Key Code**:
```python
class MarkdownHydratorModule(dspy.Module):
    """Hydrates markdown widgets with content."""

    def __init__(self):
        super().__init__()
        self.generate_markdown = dspy.Predict(
            "data, povs, citations -> markdown_content"
        )

    def forward(self, presentation_ready: dict) -> dict:
        """Generate markdown content."""
        data = presentation_ready.get("researched_data", {})
        design = presentation_ready.get("design", {})

        povs = design.get("points_of_view", [])
        citations = data.get("citations", [])

        markdown_result = self.generate_markdown(
            data=str(data),
            povs=str(povs),
            citations=str(citations),
        )

        # Get raw markdown content from LLM
        raw_content = (
            markdown_result.markdown_content
            if hasattr(markdown_result, "markdown_content")
            else ""
        )

        # Strip markdown code block wrapper (14B coder models)
        clean_content = strip_markdown_wrapper(raw_content)

        return {
            "descriptor_type": "markdown",
            "content": clean_content,
            "citations": citations,  # Include citations for frontend display
        }
```

**What Works**:
- ✅ Uses strip_markdown_wrapper utility to handle 14B coder model artifacts
- ✅ Includes citations in return for frontend rendering
- ✅ Simple dict.get() with safe defaults
- ✅ Converts complex objects to strings for LLM consumption

**Mistakes Found**: None - simple and effective

**Behavioral Notes**:
- Converts all inputs to strings for LLM (data, povs, citations)
- Passes citations through unchanged (no transformation)
- Returns descriptor_type for frontend routing
- Relies on external utility (strip_markdown_wrapper) for cleanup

**Dependencies**:
- **Imports**: dspy, strip_markdown_wrapper from services.tools.researcher.number_extractor_utils
- **Uses**: dspy.Predict(), dict.get(), hasattr()

**Reusability**: HIGH - Pattern applies to any content generation with LLM artifacts

---

## File Summary

**Total Classes**: 1
**Lines of Code**: 50

**Overall Assessment**: SIMPLE and CLEAN implementation. The strip_markdown_wrapper utility call is critical for handling 14B coder models that wrap outputs in ```markdown code blocks.

**Key Learnings for Real AgentX**:
1. ✅ Always strip markdown code block wrappers from 14B coder models
2. ✅ Pass through metadata (citations) unchanged for frontend use
3. ✅ Convert complex objects to strings for LLM consumption
4. ✅ Use dict.get() with empty defaults for all field access
5. ✅ Return descriptor_type for frontend routing

**Reuse for Real AgentX**: ✅ DIRECT - Use this pattern for any LLM text generation (not just markdown)

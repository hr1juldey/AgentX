# Function Postmortem: services/tools/designer/pov_generator.py

## Metadata
- **File**: services/tools/designer/pov_generator.py
- **Lines of Code**: 74
- **Purpose**: Generates multiple balanced points of view for analysis
- **Dependencies**: dspy, json, logging, POVGeneration signature

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE

**Purpose**: Generates 3-5 balanced perspectives (POVs) for a given query using researched data. Provides structured JSON output with fallback handling for LLM unpredictability.

---

## Classes Extracted

### POVGeneratorModule

**Purpose**: DSPy Module that generates balanced points of view with structured JSON output.

**Lines**: 16-74

**Key Code**:
```python
class POVGeneratorModule(dspy.Module):
    """Generates multiple balanced points of view with structured output.

    Has DSPy signature for proper POV generation with 3-5 perspectives.
    """

    def __init__(self):
        super().__init__()
        self.generate_povs = dspy.Predict(POVGeneration)

    def forward(self, query: str, researched_data: dict) -> dict:
        """Generate balanced POVs with structured output."""
        try:
            result = self.generate_povs(
                query=query,
                research_data=str(researched_data),
            )

            # Extract structured output
            povs_str = getattr(result, "points_of_view", "[]")

            # Parse POVs - expect JSON array
            try:
                if isinstance(povs_str, str):
                    # Try JSON parse first
                    povs = json.loads(povs_str)
                elif isinstance(povs_str, list):
                    povs = povs_str
                else:
                    # Fallback: comma-separated string
                    povs = [p.strip() for p in str(povs_str).split(",") if p.strip()]
            except (json.JSONDecodeError, TypeError):
                # Fallback to comma-separated
                povs = [p.strip() for p in str(povs_str).split(",") if p.strip()]

            # Ensure minimum 3 POVs
            if len(povs) < 3:
                logger.warning(f"Only {len(povs)} POVs generated, expected 3+")
                # Add default POVs if missing
                default_povs = [
                    f"Neutral: Analysis of {query}",
                    f"Optimistic: Positive outlook on {query}",
                    f"Cautious: Risk factors for {query}",
                ]
                povs.extend(default_povs[len(povs):])

            return {
                "points_of_view": povs[:5],  # Max 5 POVs
                "pov_count": len(povs[:5]),
            }

        except Exception as e:
            logger.error(f"POV generator error: {e}")
            return {
                "points_of_view": [f"Neutral: {query}"],
                "pov_count": 1,
                "error": str(e),
            }
```

**What Works**:
- ✅ Multi-format parsing handles JSON, list, or comma-separated LLM output
- ✅ Enforces minimum 3 POVs with intelligent defaults
- ✅ Caps maximum at 5 POVs for consistency
- ✅ Comprehensive error handling with fallback responses
- ✅ Clean separation of concerns (parsing, validation, defaults)

**Mistakes Found**: None - excellent fallback chain implementation

**Behavioral Notes**:
- LLMs often return arrays as comma-separated strings instead of valid JSON
- Uses getattr() with default to avoid AttributeError
- Default POVs are context-aware (include query string)
- Returns structured metadata (pov_count, error flags)

**Dependencies**:
- **Imports**: dspy, json, logging, POVGeneration signature
- **Uses**: dspy.Predict() for LLM interaction, getattr() for safe attribute access

**Reusability**: HIGH - Pattern is reusable for any multi-item structured output

---

## File Summary

**Total Classes**: 1
**Lines of Code**: 74

**Overall Assessment**: EXCELLENT implementation of structured output parsing with robust fallbacks. The triple fallback chain (JSON → list → comma-separated) is production-ready.

**Key Learnings for Real AgentX**:
1. ✅ Always expect LLMs to return structured data in unpredictable formats
2. ✅ Implement multi-stage fallback parsing (JSON → list → string split)
3. ✅ Enforce minimum/maximum constraints with intelligent defaults
4. ✅ Use getattr() with defaults instead of direct attribute access
5. ✅ Include metadata in responses (counts, error flags)
6. ✅ Make fallback values context-aware (include query in defaults)

**Reuse for Real AgentX**: ✅ DIRECT - Use this exact pattern for any multi-item generation (cards, form fields, etc.)

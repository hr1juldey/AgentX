# Function Postmortem: services/tools/designer/widget_insights.py

## Metadata
- **File**: services/tools/designer/widget_insights.py
- **Lines of Code**: 65
- **Purpose**: Generates insights specific to widget types
- **Dependencies**: dspy, json, logging, WidgetInsights signature

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE

**Purpose**: Generates widget-specific insights (cards, forms, charts, markdown) with JSON parsing.

---

## Classes Extracted

### WidgetInsightsModule

**Purpose**: DSPy Module that generates widget-specific insights with capped output.

**Lines**: 16-65

**Key Code**:
```python
class WidgetInsightsModule(dspy.Module):
    """Generates insights specific to widget types.

    Uses DSPy signature to generate widget-specific insights:
    - Cards: Key metrics and statistics
    - Forms: Data collection points
    - Charts: Trends and patterns
    - Markdown: Narrative themes
    """

    def __init__(self):
        super().__init__()
        self.generate_insights = dspy.Predict(WidgetInsights)

    def forward(self, query: str, data: dict, widget_type: str) -> dict:
        """Generate widget-specific insights."""
        try:
            result = self.generate_insights(
                query=query,
                data=str(data),
                widget_type=widget_type,
            )

            # Extract structured output
            insights_str = getattr(result, "insights", "[]")

            # Parse insights
            try:
                if isinstance(insights_str, str):
                    insights = json.loads(insights_str)
                elif isinstance(insights_str, list):
                    insights = insights_str
                else:
                    insights = []
            except (json.JSONDecodeError, TypeError):
                insights = []

            return {
                "insights": insights[:5],  # Max 5 insights
                "insight_count": len(insights[:5]),
            }

        except Exception as e:
            logger.error(f"Widget insights generator error: {e}")
            return {
                "insights": [],
                "insight_count": 0,
                "error": str(e),
            }
```

**What Works**:
- ✅ Triple fallback parsing (JSON string → list → empty)
- ✅ Capped output (max 5 insights)
- ✅ Comprehensive error handling with fallback
- ✅ Widget type parameter for context-aware generation
- ✅ Insight count metadata

**Mistakes Found**: None - simple and robust

**Behavioral Notes**:
- Expects LLM to return JSON array of insight strings
- Caps output at 5 insights (prevents bloat)
- Returns error in metadata on exception
- Converts data dict to string for LLM

**Dependencies**:
- **Imports**: dspy, json, logging, WidgetInsights signature
- **Uses**: dspy.Predict(), getattr(), json.loads(), try/except

**Reusability**: HIGH - Pattern applies to any capped array generation

---

## File Summary

**Total Classes**: 1
**Lines of Code**: 65

**Overall Assessment**: SIMPLE and ROBUST implementation. The triple fallback parsing combined with output capping is production-ready. This is a simpler version of the card_hydrator pattern.

**Key Learnings for Real AgentX**:
1. ✅ Use triple fallback: JSON string → list → empty
2. ✅ Cap output to prevent bloat ([:5] slicing)
3. ✅ Return metadata with counts (insight_count)
4. ✅ Include error in metadata on exception
5. ✅ Use widget_type parameter for context-aware generation
6. ✅ Convert complex objects to strings for LLM

**Reuse for Real AgentX**: ✅ DIRECT - Use this pattern for any capped array generation (insights, suggestions, recommendations, etc.)

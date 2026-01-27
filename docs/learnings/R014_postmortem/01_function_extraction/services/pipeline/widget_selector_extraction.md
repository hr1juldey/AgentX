# Function Postmortem: services/pipeline/widget_selector.py

## Metadata
- **File**: services/pipeline/widget_selector.py
- **Lines of Code**: 101
- **Purpose**: Selects appropriate widgets based on data context
- **Dependencies**: dspy, services.tools.selector_tools

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE

**Purpose**: Decides which widgets to use based on complete data context, user intent, and URL detection.

---

## Classes Extracted

### WidgetSelectorAgent

**Purpose**: DSPy Module that selects widgets based on data type, URL count, and context.

**Lines**: 12-100

**Key Code**:
```python
class WidgetSelectorAgent(dspy.Module):
    """WIDGET SELECTOR Agent: Decides which widgets to use.

    Runs AFTER research is complete, selects appropriate widgets
    based on complete data context and user intent.
    """

    def __init__(self):
        super().__init__()
        self.widget_matcher = WidgetMatcherModule()

    def forward(
        self,
        designed_data: dict,
        device_context: str = "desktop",
    ) -> dict:
        """Execute WIDGET SELECTOR agent pipeline."""
        # URL-related keywords (search, find, look up)
        url_keywords = [
            "search",
            "find",
            "look up",
            "information about",
            "what is",
            "tell me about",
            "show me",
        ]

        # Check if query is likely to return URLs
        query = designed_data.get("query", "").lower()
        metadata = designed_data.get("metadata", {})
        url_count = metadata.get("url_count", 0)
        is_url_query = any(keyword in query for keyword in url_keywords)

        # Multiple URLs → OpenGraph gallery
        if is_url_query and url_count > 1:
            return {
                "widgets": ["gallery", "markdown"],
                "rationale": "Gallery for multiple URLs, markdown for summary",
                "device_context": device_context,
            }

        # Single URL → OpenGraph card (via image hydrator)
        if is_url_query and url_count == 1:
            return {
                "widgets": ["image", "markdown"],
                "rationale": "Image card for single URL, markdown for context",
                "device_context": device_context,
            }

        # Match widgets based on designed data
        match_result_raw = self.widget_matcher(
            designed_data=designed_data,
            device_context=device_context,
        )
        match_result = match_result_raw if hasattr(match_result_raw, "get") else {}

        matched_widgets = match_result.get("widgets", ["markdown"])  # type: ignore[missing-attribute]

        return {
            "widgets": matched_widgets,
            "rationale": match_result.get(  # type: ignore[missing-attribute]
                "rationale", "Selected based on data type and context"
            ),
            "device_context": device_context,
        }

    def suggest_fallback_widget(self, error_type: str = "") -> str:
        """Suggest a fallback widget when selection fails."""
        if "data" in error_type.lower() or "research" in error_type.lower():
            return "markdown"
        if "visual" in error_type.lower():
            return "card"
        return "markdown"  # Default fallback
```

**What Works**:
- ✅ URL detection: Checks for URL-related keywords in query
- ✅ Early returns: Special handling for single/multiple URLs
- ✅ Fallback to widget_matcher: General case handled by WidgetMatcherModule
- ✅ Default fallback: Always returns ["markdown"] if matching fails
- ✅ Device context: Passes through device_context for responsive design
- ✅ Rationale tracking: Explains why widgets were selected
- ✅ Error handling: suggest_fallback_widget provides graceful degradation

**Mistakes Found**: None - clean multi-branch selection

**Behavioral Notes**:
- URL keywords: search, find, look up, information about, what is, tell me about, show me
- URL count from metadata: url_count > 1 → gallery, url_count == 1 → image + markdown
- Default widget: markdown (always safe fallback)
- Device context: desktop, mobile, tablet affects widget selection

**Dependencies**:
- **Imports**: dspy, services.tools.selector_tools.WidgetMatcherModule
- **Uses**: WidgetMatcherModule

**Reusability**: HIGH - Multi-branch widget selection pattern is reusable for any content routing system.

---

## File Summary

**Total Classes**: 1
**Lines of Code**: 101

**Overall Assessment**: Clean widget selector with URL detection and graceful fallbacks. Multi-branch pattern handles special cases before general matching.

**Key Learnings for Real AgentX**:
1. ✅ Early returns: Handle special cases (URLs) before general logic
2. ✅ Keyword detection: Use keyword lists for intent detection
3. ✅ Metadata-driven: Use url_count from metadata for decisions
4. ✅ Always have defaults: Return ["markdown"] if everything fails
5. ✅ Rationale tracking: Explain why decisions were made
6. ✅ Fallback method: Provide suggest_fallback_widget for error recovery
7. ✅ Device context: Pass through device context for responsive design

**Reuse for Real AgentX**: ✅ DIRECT - Use this multi-branch selection pattern for any content routing or widget selection system.

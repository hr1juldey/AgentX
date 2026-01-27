# Function Postmortem: services/tools/hydrators/card_hydrator.py

## Metadata
- **File**: services/tools/hydrators/card_hydrator.py
- **Lines of Code**: 81
- **Purpose**: Hydrates card widgets with structured card data
- **Dependencies**: dspy, json, logging, CardData signature, number_extractor_utils

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE

**Purpose**: Generates card widgets with JSON array parsing and comprehensive validation.

---

## Classes Extracted

### CardHydratorModule

**Purpose**: DSPy Module that generates structured card data with robust JSON parsing and validation.

**Lines**: 17-81

**Key Code**:
```python
class CardHydratorModule(dspy.Module):
    """Hydrates card widgets with properly structured card data."""

    def __init__(self):
        super().__init__()
        self.generate_cards = dspy.Predict(CardData)

    def forward(self, presentation_ready: dict) -> dict:
        """Generate card configuration with structured output."""
        data = presentation_ready.get("researched_data", {})
        design = presentation_ready.get("design", {})
        query = presentation_ready.get("query", "")

        try:
            result = self.generate_cards(
                query=query,
                data=str(data),
                design=str(design),
            )

            # Extract structured output
            cards_str = getattr(result, "cards", "[]")

            # Parse cards - LLM may return JSON array
            try:
                if isinstance(cards_str, str):
                    # Strip markdown code block wrapper (14B coder models)
                    cards_str = strip_markdown_wrapper(cards_str)
                    cards = json.loads(cards_str)
                elif isinstance(cards_str, list):
                    cards = cards_str
                else:
                    cards = []
            except (json.JSONDecodeError, TypeError):
                logger.warning(f"Failed to parse cards: {cards_str}")
                cards = []

            # Validate card structure
            validated_cards = []
            for card in cards if isinstance(cards, list) else []:
                if isinstance(card, dict):
                    validated_cards.append(
                        {
                            "title": card.get("title", "Metric"),
                            "value": card.get("value", "N/A"),
                            "description": card.get("description", ""),
                            "icon": card.get("icon", "📊"),
                            "color": card.get("color", "blue_500"),
                        }
                    )

            return {
                "descriptor_type": "card",
                "content": {"cards": validated_cards},
                "metadata": {"card_count": len(validated_cards)},
            }

        except Exception as e:
            logger.error(f"Card hydrator error: {e}")
            return {
                "descriptor_type": "card",
                "content": {"cards": []},
                "metadata": {"card_count": 0, "error": str(e)},
            }
```

**What Works**:
- ✅ Triple fallback parsing (JSON string → list → empty)
- ✅ strip_markdown_wrapper for 14B coder models
- ✅ Comprehensive validation with dict.get() defaults
- ✅ Type checking (isinstance) before iteration
- ✅ Structured metadata (card_count, error)
- ✅ Top-level try/except with error fallback

**Mistakes Found**: None - excellent implementation

**Behavioral Notes**:
- Expects LLM to return JSON array of card objects
- Validates each card has required fields with defaults
- Returns empty list on any parse error (graceful degradation)
- Includes error in metadata when exception occurs
- Validates both cards list type and individual card dict type

**Dependencies**:
- **Imports**: dspy, json, logging, CardData signature, strip_markdown_wrapper
- **Uses**: dspy.Predict(), getattr(), json.loads(), isinstance(), dict.get()

**Reusability**: VERY HIGH - This is the GOLD STANDARD for array-based structured output

---

## File Summary

**Total Classes**: 1
**Lines of Code**: 81

**Overall Assessment**: EXCELLENT implementation with production-ready parsing and validation. The triple fallback chain (JSON → list → empty) combined with comprehensive field validation makes this robust for real-world use.

**Key Learnings for Real AgentX**:
1. ✅ Always strip markdown wrappers before JSON parsing
2. ✅ Use triple fallback: JSON string → list → empty
3. ✅ Validate both outer container (isinstance(cards, list)) and inner items (isinstance(card, dict))
4. ✅ Provide sensible defaults for all fields: `card.get("title", "Metric")`
5. ✅ Return metadata with counts and errors
6. ✅ Use top-level try/except with error metadata
7. ✅ Log warnings for parse failures but continue gracefully

**Reuse for Real AgentX**: ✅ DIRECT - This is the PERFECT PATTERN for any array-based structured output (cards, form fields, list items, etc.)

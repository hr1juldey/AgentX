# Function Postmortem: services/tools/hydrators/form_hydrator.py

## Metadata
- **File**: services/tools/hydrators/form_hydrator.py
- **Lines of Code**: 124
- **Purpose**: Hydrates form widgets with structured field data
- **Dependencies**: dspy, json, logging, FormFieldNames, FormFieldDetails signatures, number_extractor_utils

---

## Analysis

**File Status**: PRODUCTION DSPy MODULE - TWO-STAGE SIGNATURE PATTERN

**Purpose**: Generates form fields using split signatures (names first, then details for each field).

---

## Classes Extracted

### FormHydratorModule

**Purpose**: DSPy Module that uses two-stage signature pattern for form field generation.

**Lines**: 20-124

**Key Code**:
```python
class FormHydratorModule(dspy.Module):
    """Hydrates form widgets with properly structured field data."""

    def __init__(self):
        super().__init__()
        self.get_field_names = dspy.Predict(FormFieldNames)
        self.get_field_details = dspy.Predict(FormFieldDetails)

    def forward(self, presentation_ready: dict) -> dict:
        """Generate form configuration using split signatures."""
        data = presentation_ready.get("researched_data", {})
        insights = presentation_ready.get("insights", [])
        query = presentation_ready.get("query", "")

        validated_fields = []

        try:
            # Step 1: Get field names (simple task)
            names_result = self.get_field_names(
                query=query, data=str(data), insights=str(insights)
            )
            field_names_str = getattr(names_result, "field_names", "[]")

            # Parse field names (JSON array of strings)
            try:
                if isinstance(field_names_str, str):
                    # Strip markdown code block wrapper (14B coder models)
                    field_names_str = strip_markdown_wrapper(field_names_str)
                    field_names = json.loads(field_names_str)
                elif isinstance(field_names_str, list):
                    field_names = field_names_str
                else:
                    field_names = []
            except (json.JSONDecodeError, TypeError):
                logger.warning(f"Failed to parse field_names: {field_names_str}")
                field_names = []

            logger.info(f"[FORM HYDRATOR] Got {len(field_names)} field names")

            # Step 2: Get details for each field (focused task)
            for field_name in field_names:
                if not isinstance(field_name, str):
                    continue

                try:
                    details_result = self.get_field_details(
                        field_name=field_name, query=query, data=str(data)
                    )

                    field_type = getattr(details_result, "field_type", "text")
                    description = getattr(details_result, "description", "")
                    options_str = getattr(details_result, "options", "[]")

                    # Parse options (JSON array of strings)
                    try:
                        if isinstance(options_str, str):
                            # Strip markdown code block wrapper (14B coder models)
                            options_str = strip_markdown_wrapper(options_str)
                            options = json.loads(options_str)
                        elif isinstance(options_str, list):
                            options = options_str
                        else:
                            options = []
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(
                            f"Failed to parse options for '{field_name}': {options_str}"
                        )
                        options = []

                    # Generate name from label (snake_case for form submission)
                    name = field_name.lower().replace(" ", "_").replace("-", "_")

                    validated_fields.append(
                        {
                            "name": name,
                            "type": field_type
                            if field_type
                            in ["text", "textarea", "number", "select", "checkbox"]
                            else "text",
                            "label": field_name,
                            "placeholder": description,
                            "options": options if isinstance(options, list) else [],
                        }
                    )

                except Exception as e:
                    logger.warning(
                        f"Failed to get details for field '{field_name}': {e}"
                    )
                    continue

            return {
                "descriptor_type": "form",
                "content": {"form_fields": validated_fields},
                "metadata": {"field_count": len(validated_fields)},
            }

        except Exception as e:
            logger.error(f"Form hydrator error: {e}")
            return {
                "descriptor_type": "form",
                "content": {"form_fields": []},
                "metadata": {"field_count": 0, "error": str(e)},
            }
```

**What Works**:
- ✅ Two-stage signature pattern (names first, then individual details)
- ✅ Reduces LLM complexity by splitting task into focused steps
- ✅ Individual try/except for each field (one failure doesn't break all)
- ✅ Enum validation for field_type (whitelist check)
- ✅ Auto-generates name from label (snake_case conversion)
- ✅ Per-field error handling with continue
- ✅ Comprehensive logging at each stage

**Mistakes Found**: None - excellent two-stage pattern

**Behavioral Notes**:
- Step 1 gets array of field names (simple list generation)
- Step 2 loops through names and gets details for each (focused task)
- Uses continue on individual field failures (partial success)
- Validates field_type against whitelist (defaults to "text")
- Generates HTML-friendly name attributes from labels
- Triple fallback for options parsing (JSON → list → empty)

**Dependencies**:
- **Imports**: dspy, json, logging, FormFieldNames, FormFieldDetails signatures, strip_markdown_wrapper
- **Uses**: dspy.Predict(), getattr(), json.loads(), isinstance(), dict.get()

**Reusability**: VERY HIGH - Two-stage pattern is ideal for any multi-item structured output

---

## File Summary

**Total Classes**: 1
**Lines of Code**: 124

**Overall Assessment**: EXCELLENT two-stage signature pattern. This is a MASTERCLASS in reducing LLM complexity by splitting a complex task (generate form fields with details) into two focused tasks (get names → get details per name).

**Key Learnings for Real AgentX**:
1. ✅ Split complex multi-item generation into two stages: list → individual details
2. ✅ Use individual try/except for each item (continue on failure, don't break entire operation)
3. ✅ Validate enum values with whitelist: `if field_type in ["text", "textarea", "number", "select", "checkbox"]`
4. ✅ Auto-generate technical fields from user-facing labels (snake_case conversion)
5. ✅ Log at each stage for debugging (field names count, individual field failures)
6. ✅ Return partial results on failure (some fields succeed, some fail)
7. ✅ Use strip_markdown_wrapper for both outer and inner JSON parsing

**Reuse for Real AgentX**: ✅ DIRECT - Use this two-stage pattern for any multi-item generation where items need individual details (form fields, list items, table rows, etc.)

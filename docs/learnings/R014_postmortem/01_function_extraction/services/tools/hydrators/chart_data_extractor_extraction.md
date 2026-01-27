# Function Postmortem: services/tools/hydrators/chart_data_extractor.py

## Metadata
- **File**: services/tools/hydrators/chart_data_extractor.py
- **Lines of Code**: 76
- **Purpose**: Extracts numbers from nested presentation_ready structures
- **Dependencies**: json, logging

---

## Analysis

**File Status**: PRODUCTION UTILITY FUNCTION

**Purpose**: Robust extraction of extracted_numbers from nested presentation_ready dict with multiple fallback paths.

---

## Functions Extracted

### extract_numbers_from_presentation_ready

**Purpose**: Extract extracted_numbers from nested presentation_ready structure with multiple fallback paths.

**Lines**: 14-75

**Key Code**:
```python
def extract_numbers_from_presentation_ready(presentation_ready: dict) -> list:
    """Extract extracted_numbers from nested presentation_ready structure.

    Tries multiple paths to handle both e2e and unit test structures:
    1. researched_data.beautiful_data.extracted_numbers (e2e)
    2. researched_data.extracted_numbers (fallback)
    3. beautiful_data.extracted_numbers (direct/unit test)

    Args:
        presentation_ready: Full presentation_ready dict

    Returns:
        List of extracted_numbers dicts
    """
    # Log presentation_ready structure for debugging
    logger.info(
        f"📊 [CHART HYDRATOR] presentation_ready keys: {list(presentation_ready.keys())}"
    )

    # Extract extracted_numbers from nested structure (e2e) or direct (unit test)
    researched_data = presentation_ready.get("researched_data", {})
    logger.info(
        f"📊 [CHART HYDRATOR] researched_data keys: {list(researched_data.keys())}"
    )

    beautiful_data = researched_data.get("beautiful_data", {})
    logger.info(
        f"📊 [CHART HYDRATOR] beautiful_data keys: {list(beautiful_data.keys())}"
    )
    logger.info(
        f"📊 [CHART HYDRATOR] beautiful_data item counts: {[(k, len(v) if isinstance(v, list) else type(v).__name__) for k, v in beautiful_data.items()]}"
    )

    extracted_numbers = beautiful_data.get("extracted_numbers", [])
    logger.info(
        f"📊 [CHART HYDRATOR] extracted_numbers from nested: {len(extracted_numbers)} items"
    )

    # Fallback to direct extracted_numbers for unit test compatibility
    if not extracted_numbers:
        extracted_numbers = researched_data.get("extracted_numbers", [])
        logger.info(
            f"📊 [CHART HYDRATOR] extracted_numbers from fallback: {len(extracted_numbers)} items"
        )

    # Fallback to top-level beautiful_data
    if not extracted_numbers:
        beautiful_data_direct = presentation_ready.get("beautiful_data", {})
        extracted_numbers = beautiful_data_direct.get("extracted_numbers", [])
        logger.info(
            f"📊 [CHART HYDRATOR] extracted_numbers from direct: {len(extracted_numbers)} items"
        )

    if not extracted_numbers:
        logger.warning(
            "📊 [CHART HYDRATOR] No extracted numbers available for chart generation"
        )
        logger.warning(
            f"📊 [CHART HYDRATOR] Full presentation_ready structure: {json.dumps({k: str(v)[:100] for k, v in presentation_ready.items()})"
        )

    return extracted_numbers
```

**What Works**:
- ✅ 3 fallback paths for robustness
- ✅ Comprehensive logging at each step (debugging aid)
- ✅ Graceful handling of missing data (returns empty list)
- ✅ Logs full structure on failure (diagnostics)
- ✅ Supports both e2e and unit test structures

**Mistakes Found**: None - robust extraction pattern

**Behavioral Notes**:
- Path 1: researched_data.beautiful_data.extracted_numbers (e2e)
- Path 2: researched_data.extracted_numbers (fallback)
- Path 3: beautiful_data.extracted_numbers (unit test)
- Extensive logging with emoji prefixes for readability
- json.dumps truncates values to 100 chars to avoid log spam

**Dependencies**:
- **Imports**: json, logging
- **Uses**: logger (logging.getLogger)

**Reusability**: HIGH - Multi-path fallback pattern is reusable for any nested dict extraction.

---

## File Summary

**Total Functions**: 1
**Lines of Code**: 76

**Overall Assessment**: Robust extraction function with comprehensive logging. Multi-path fallback handles both e2e and unit test structures gracefully.

**Key Learnings for Real AgentX**:
1. ✅ Multi-path fallback: Try nested → fallback → direct for robustness
2. ✅ Comprehensive logging: Log structure at each level for debugging
3. ✅ Graceful degradation: Return empty list, don't crash
4. ✅ Diagnostics on failure: Log full structure (truncated) when extraction fails
5. ✅ Emoji prefixes: Use emojis for log readability (📊 [CHART HYDRATOR])
6. ✅ Type checking: Check isinstance(v, list) before len()

**Reuse for Real AgentX**: ✅ DIRECT - Use this multi-path fallback pattern for any nested data extraction.

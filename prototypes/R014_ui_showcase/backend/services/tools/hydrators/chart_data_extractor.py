# =============================================================================
# AGENTX Hydrators - Chart Data Extractor
# =============================================================================
# Extracts numbers from nested presentation_ready structures
# =============================================================================

import json
import logging


logger = logging.getLogger(__name__)


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
            f"📊 [CHART HYDRATOR] Full presentation_ready structure: {json.dumps({k: str(v)[:100] for k, v in presentation_ready.items()})}"
        )

    return extracted_numbers

# =============================================================================
# AGENTX Widget Spawner - Accessibility Compliance Rewards
# =============================================================================
# Reward functions for WCAG compliance evaluation
# =============================================================================

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def accessibility_compliance_score(args: Any, pred: Any) -> float:
    """Evaluate WCAG compliance (0.0 to 1.0).

    Checks: color contrast, font sizes, interactive element sizes.
    """
    try:
        content = json.loads(pred.widget_content)
    except (json.JSONDecodeError, AttributeError):
        logger.warning("Invalid widget content JSON")
        return 0.0

    score = 1.0

    # Check 1: Color contrast (multiply penalty)
    if content.get("contrast_ratio", 0) < 4.5:
        score *= 0.7
    elif content.get("contrast_ratio", 0) < 7.0:
        score *= 0.9

    # Check 2: Font size (multiply penalty)
    font_size = content.get("font_size", 16)
    if font_size < 14:
        score *= 0.7
    elif font_size < 16:
        score *= 0.9

    # Check 3: Interactive elements (multiply penalty)
    button_size = content.get("button_size", 40)
    if button_size < 44:
        score *= 0.85

    # Check 4: Has alt text (additive bonus)
    if content.get("has_alt_text", False):
        score = min(score + 0.05, 1.0)

    return max(score, 0.0)

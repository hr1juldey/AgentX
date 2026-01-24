# =============================================================================
# AGENTX SEQUENCER Utilities
# =============================================================================
# Helper functions for delivery plan creation
# =============================================================================

from typing import List, Dict, Any


def create_delivery_plan(
    sequence: List[Dict[str, Any]], visual_hierarchy: List[str]
) -> List[Dict[str, Any]]:
    """Create detailed delivery plan from sequence.

    Args:
        sequence: Sequence list with widget, order, delay info
        visual_hierarchy: Visual hierarchy list (hero, insights, details)

    Returns:
        Delivery plan with visual role and delivery type
    """
    delivery_plan = []

    for item in sequence:
        widget = item.get("widget", "unknown")
        order = item.get("order", 1)
        delay = item.get("delay_sec", 0.0)

        # Determine visual role based on order and hierarchy
        if visual_hierarchy:
            role_index = min(order - 1, len(visual_hierarchy) - 1)
            visual_role = visual_hierarchy[role_index]
        else:
            visual_role = "standard"

        delivery_plan.append(
            {
                "widget": widget,
                "order": order,
                "delay_sec": delay,
                "visual_role": visual_role,
                "delivery_type": "immediate" if delay == 0 else "staggered",
            }
        )

    return delivery_plan

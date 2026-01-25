# =============================================================================
# AGENTX Color Palette System
# =============================================================================
# Domain-based color palettes for chart widgets
# =============================================================================

from typing import Dict, List


# Default chart colors (match frontend --chart-1 to --chart-5)
DEFAULT_CHART_COLORS: List[str] = [
    "hsl(12 76% 61%)",  # Coral
    "hsl(173 58% 39%)",  # Teal
    "hsl(197 37% 24%)",  # Blue
    "hsl(43 74% 66%)",  # Amber
    "hsl(27 87% 67%)",  # Orange
]


# Domain-specific palettes (5 colors each)
DOMAIN_PALETTES: Dict[str, List[str]] = {
    "finance": [
        "hsl(142 76% 36%)",
        "hsl(0 84% 60%)",
        "hsl(217 91% 60%)",
        "hsl(48 96% 53%)",
        "hsl(215 20% 40%)",
    ],  # Green, Red, Blue, Yellow, Gray
    "health": [
        "hsl(142 76% 36%)",
        "hsl(271 81% 56%)",
        "hsl(199 89% 48%)",
        "hsl(25 95% 53%)",
        "hsl(330 81% 60%)",
    ],  # Green, Purple, Cyan, Orange, Pink
    "technology": [
        "hsl(217 91% 60%)",
        "hsl(189 94% 43%)",
        "hsl(238 84% 67%)",
        "hsl(173 58% 39%)",
        "hsl(215 20% 40%)",
    ],  # Blue, Cyan, Indigo, Teal, Gray
    "sports": [
        "hsl(0 84% 60%)",
        "hsl(48 96% 53%)",
        "hsl(27 87% 67%)",
        "hsl(199 89% 48%)",
        "hsl(142 76% 36%)",
    ],  # Red, Yellow, Orange, Blue, Green
    "science": [
        "hsl(199 89% 48%)",
        "hsl(217 91% 60%)",
        "hsl(142 76% 36%)",
        "hsl(271 81% 56%)",
        "hsl(25 95% 53%)",
    ],  # Cyan, Blue, Green, Purple, Orange
    "business": [
        "hsl(217 91% 60%)",
        "hsl(142 76% 36%)",
        "hsl(25 95% 53%)",
        "hsl(215 20% 40%)",
        "hsl(199 89% 48%)",
    ],  # Blue, Green, Orange, Gray, Cyan
}


def get_chart_colors(domain: str = "general", count: int = 5) -> List[str]:
    """Get chart colors for a specific domain.

    Args:
        domain: Domain name (e.g., "finance", "health", "technology")
        count: Number of colors to return (max 5)

    Returns:
        List of HSL color strings
    """
    palette = DOMAIN_PALETTES.get(domain.lower(), DEFAULT_CHART_COLORS)
    return palette[:count]


def get_default_colors(count: int = 5) -> List[str]:
    """Get default chart colors.

    Args:
        count: Number of colors to return (max 5)

    Returns:
        List of HSL color strings
    """
    return DEFAULT_CHART_COLORS[:count]

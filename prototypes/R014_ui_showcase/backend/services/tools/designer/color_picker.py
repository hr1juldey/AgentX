# =============================================================================
# AGENTX Designer - Color Picker Module
# =============================================================================
# Selects color schemes based on theme and mood
# =============================================================================

import dspy


class ColorPickerModule(dspy.Module):
    """Selects color schemes based on theme and mood.

    Has 2 signatures:
    - PickByTheme: Pick colors by data theme (finance, health, etc.)
    - PickByMood: Pick colors by mood (professional, casual, urgent)
    """

    def __init__(self):
        super().__init__()
        self.pick_by_theme = dspy.Predict("domain, query -> color_scheme")
        self.pick_by_mood = dspy.Predict("domain, mood -> color_scheme")
        self.check_contrast = dspy.Predict(
            "primary_color, secondary_color -> contrast_ratio"
        )

    def forward(self, query: str, domain: str = "") -> dict:
        """Pick color scheme based on query context."""
        domain_str = domain or "general"
        theme_result = self.pick_by_theme(domain=domain_str, query=query)

        # Default color scheme
        default_scheme = {
            "primary": "blue_500",
            "accent": "green_400",
            "background": "slate_900",
        }

        if hasattr(theme_result, "color_scheme"):
            color_scheme_raw = theme_result.color_scheme

            # Handle if LLM returns string instead of dict
            if isinstance(color_scheme_raw, dict):
                color_scheme = color_scheme_raw
            else:
                color_scheme = default_scheme

            # Safely get colors with fallbacks
            primary = (
                color_scheme.get("primary", default_scheme["primary"])
                if isinstance(color_scheme, dict)
                else default_scheme["primary"]
            )
            accent = (
                color_scheme.get("accent", default_scheme["accent"])
                if isinstance(color_scheme, dict)
                else default_scheme["accent"]
            )

            # Check contrast for accessibility
            contrast_result = self.check_contrast(
                primary_color=primary,
                secondary_color=accent,
            )

            return {
                "color_scheme": color_scheme
                if isinstance(color_scheme, dict)
                else default_scheme,
                "contrast_ratio": float(contrast_result.contrast_ratio)
                if hasattr(contrast_result, "contrast_ratio")
                else 7.0,
            }

        return {
            "color_scheme": default_scheme,
            "contrast_ratio": 7.0,
        }

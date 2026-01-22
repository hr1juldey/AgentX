# =============================================================================
# AGENTX Designer Tools
# =============================================================================
# DSPy modules for the DESIGNER agent (POV + Color Schemes)
# =============================================================================

import dspy


class POVGeneratorModule(dspy.Module):
    """Generates multiple points of view for balanced analysis.

    Has 3 signatures:
    - GeneratePOVs: Generate bull/bear/neutral POVs
    - BalancePerspectives: Ensure balanced representation
    - AddNuance: Add nuanced considerations
    """

    def __init__(self):
        super().__init__()
        self.generate_povs = dspy.Predict("query, data -> points_of_view")
        self.balance_perspectives = dspy.Predict("points_of_view -> balanced_povs")
        self.add_nuance = dspy.Predict("povs -> nuanced_povs")

    def forward(self, query: str, researched_data: dict) -> dict:
        """Generate balanced POVs."""
        povs_result = self.generate_povs(query=query, data=str(researched_data))

        if hasattr(povs_result, "points_of_view"):
            balanced_result = self.balance_perspectives(
                points_of_view=povs_result.points_of_view
            )
            nuanced_result = self.add_nuance(povs=str(balanced_result))

            return {
                "points_of_view": [
                    pov.strip()
                    for pov in str(povs_result.points_of_view).split(",")
                    if pov.strip()
                ],
                "balanced_povs": balanced_result.balanced_povs
                if hasattr(balanced_result, "balanced_povs")
                else [],
                "nuanced_analysis": nuanced_result.nuanced_povs
                if hasattr(nuanced_result, "nuanced_povs")
                else "",
            }

        return {"points_of_view": [], "balanced_povs": [], "nuanced_analysis": ""}


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
                # LLM returned a string description, use default
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


class HierarchyPlannerModule(dspy.Module):
    """Plans visual hierarchy and flow.

    Has 2 signatures:
    - PlanVisualFlow: Plan how information flows visually
    - AssignPriority: Assign priority levels to elements
    """

    def __init__(self):
        super().__init__()
        self.plan_flow = dspy.Predict("widgets, query -> visual_flow")
        self.assign_priority = dspy.Predict("widgets -> priority_order")

    def forward(self, widgets: list, query: str = "") -> dict:
        """Plan visual hierarchy."""
        widgets_str = str(widgets)
        flow_result = self.plan_flow(widgets=widgets_str, query=query)
        priority_result = self.assign_priority(widgets=widgets_str)

        return {
            "visual_hierarchy": [
                item.strip()
                for item in str(flow_result.visual_flow).split(",")
                if item.strip()
            ]
            if hasattr(flow_result, "visual_flow")
            else ["hero", "insights", "details"],
            "priority_order": [
                item.strip()
                for item in str(priority_result.priority_order).split(",")
                if item.strip()
            ]
            if hasattr(priority_result, "priority_order")
            else widgets,
            "layout": "narrative_focused",
        }


class AccessibilityModule(dspy.Module):
    """Checks accessibility compliance (WCAG).

    Has 3 signatures:
    - CheckWCAG: Check WCAG compliance
    - CheckContrast: Check color contrast ratios
    - CheckSizes: Check text and tap target sizes
    """

    def __init__(self):
        super().__init__()
        self.check_wcag = dspy.Predict("design -> wcag_compliance, issues")
        self.check_contrast = dspy.Predict("color_scheme -> contrast_ratio, passes")
        self.check_sizes = dspy.Predict("widget_types -> size_compliance")

    def forward(self, design: dict) -> dict:
        """Check accessibility compliance."""
        contrast_result = self.check_contrast(
            color_scheme=str(design.get("color_scheme", {}))
        )
        sizes_result = self.check_sizes(widget_types=str(design.get("widgets", [])))
        wcag_result = self.check_wcag(design=str(design))

        # Safely convert contrast_ratio to float
        contrast_ratio = 7.0  # default
        if hasattr(contrast_result, "contrast_ratio"):
            try:
                contrast_ratio = float(contrast_result.contrast_ratio)  # type: ignore[attr-defined]
            except (ValueError, TypeError):
                contrast_ratio = 7.0

        return {
            "wcag_compliant": wcag_result.wcag_compliance == "true"
            if hasattr(wcag_result, "wcag_compliance")
            else True,
            "contrast_ratio": contrast_ratio,
            "contrast_passes": contrast_result.passes == "true"
            if hasattr(contrast_result, "passes")
            else True,
            "size_issues": sizes_result.issues
            if hasattr(sizes_result, "issues")
            else [],
        }

"""Hierarchy Designer Module for Designer agent.

Ported from R014: services/tools/designer/hierarchy.py

Designs visual hierarchy for complex widgets.
Determines layout and information architecture.
"""

import dspy

from agentx.agent.dspy_signatures.designer.pov import DesignHierarchy
from agentx.agent.tools.common.dspy_helpers import safe_extract


class HierarchyDesignerModule(dspy.Module):
    """Designs visual hierarchy for complex widgets.

    Determines:
    - Primary/secondary/tertiary elements
    - Grouping and spacing
    - Visual flow
    """

    def __init__(self) -> None:
        """Initialize the hierarchy designer."""
        super().__init__()
        self.designer = dspy.Predict(DesignHierarchy)

    def forward(
        self,
        widget_type: str,
        content_structure: str,
    ) -> dict:
        """Design hierarchy for widget.

        Args:
            widget_type: Type of widget being designed
            content_structure: Structure of the content

        Returns:
            dict with hierarchy plan (primary, secondary, tertiary, spacing, grouping)
        """
        # Run hierarchy designer
        result = self.designer(
            widget_type=widget_type,
            content_structure=content_structure,
        )

        # Extract hierarchy plan
        hierarchy_plan = safe_extract(result, "hierarchy_plan", "")

        # Parse hierarchy plan
        hierarchy = self._parse_hierarchy(hierarchy_plan)

        return hierarchy

    def _parse_hierarchy(self, plan: str) -> dict:
        """Parse hierarchy plan string into dict.

        Args:
            plan: Hierarchy plan string

        Returns:
            dict with primary, secondary, tertiary, spacing, grouping
        """
        import json

        # Try to parse as JSON
        try:
            return json.loads(plan)
        except json.JSONDecodeError:
            pass

        # Fallback: Parse line-by-line
        hierarchy: dict[str, object] = {
            "primary": [],
            "secondary": [],
            "tertiary": [],
            "spacing": "medium",
            "grouping": [],
        }

        current_section: str | None = None
        for line in plan.split("\n"):
            line = line.strip().lower()
            if not line:
                continue

            if line.startswith("primary:"):
                current_section = "primary"
            elif line.startswith("secondary:"):
                current_section = "secondary"
            elif line.startswith("tertiary:"):
                current_section = "tertiary"
            elif line.startswith("spacing:"):
                hierarchy["spacing"] = line.split(":", 1)[1].strip()
            elif line.startswith("grouping:"):
                hierarchy["grouping"] = line.split(":", 1)[1].strip().split(",")
            elif current_section and line.startswith("- "):
                section = current_section
                if section in hierarchy and isinstance(hierarchy[section], list):
                    hierarchy[section].append(line[2:].strip())  # type: ignore[arg-type]

        return hierarchy

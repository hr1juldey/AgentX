# =============================================================================
# AGENTX Hydration Tools
# =============================================================================
# DSPy modules for widget hydration (fill widgets with data)
# =============================================================================

import dspy


class ChartHydratorModule(dspy.Module):
    """Hydrates chart widgets with data."""

    def __init__(self):
        super().__init__()
        self.generate_chart_config = dspy.Predict("data, design -> chart_config")

    def forward(self, presentation_ready: dict) -> dict:
        """Generate chart configuration."""
        data = presentation_ready.get("researched_data", {})
        design = presentation_ready.get("design", {})

        config_result = self.generate_chart_config(data=str(data), design=str(design))

        return {
            "descriptor_type": "chart",
            "content": config_result.chart_config
            if hasattr(config_result, "chart_config")
            else {},
        }


class MarkdownHydratorModule(dspy.Module):
    """Hydrates markdown widgets with content."""

    def __init__(self):
        super().__init__()
        self.generate_markdown = dspy.Predict(
            "data, povs, citations -> markdown_content"
        )

    def forward(self, presentation_ready: dict) -> dict:
        """Generate markdown content."""
        data = presentation_ready.get("researched_data", {})
        design = presentation_ready.get("design", {})

        povs = design.get("points_of_view", [])
        citations = data.get("citations", [])

        markdown_result = self.generate_markdown(
            data=str(data),
            povs=str(povs),
            citations=str(citations),
        )

        return {
            "descriptor_type": "markdown",
            "content": markdown_result.markdown_content
            if hasattr(markdown_result, "markdown_content")
            else "",
        }


class CardHydratorModule(dspy.Module):
    """Hydrates card widgets with stat data."""

    def __init__(self):
        super().__init__()
        self.extract_stats = dspy.Predict("data, design -> stat_cards")

    def forward(self, presentation_ready: dict) -> dict:
        """Extract stat cards from data."""
        data = presentation_ready.get("researched_data", {})
        design = presentation_ready.get("design", {})

        stats_result = self.extract_stats(data=str(data), design=str(design))

        return {
            "descriptor_type": "card",
            "content": stats_result.stat_cards
            if hasattr(stats_result, "stat_cards")
            else [],
        }


class FormHydratorModule(dspy.Module):
    """Hydrates form widgets with action items."""

    def __init__(self):
        super().__init__()
        self.generate_form = dspy.Predict("insights, data -> form_fields")

    def forward(self, presentation_ready: dict) -> dict:
        """Generate form fields."""
        insights = presentation_ready.get("insights", [])
        data = presentation_ready.get("researched_data", {})

        form_result = self.generate_form(insights=str(insights), data=str(data))

        return {
            "descriptor_type": "form",
            "content": form_result.form_fields
            if hasattr(form_result, "form_fields")
            else [],
        }


class ImageHydratorModule(dspy.Module):
    """Hydrates image widgets with image URLs."""

    def __init__(self):
        super().__init__()
        self.extract_images = dspy.Predict("data -> image_urls")

    def forward(self, presentation_ready: dict) -> dict:
        """Extract image URLs from data."""
        data = presentation_ready.get("researched_data", {})

        image_result = self.extract_images(data=str(data))

        return {
            "descriptor_type": "image",
            "content": image_result.image_urls
            if hasattr(image_result, "image_urls")
            else [],
        }


class GalleryHydratorModule(dspy.Module):
    """Hydrates gallery widgets with multiple images."""

    def __init__(self):
        super().__init__()
        self.extract_gallery = dspy.Predict("data -> gallery_items")

    def forward(self, presentation_ready: dict) -> dict:
        """Extract gallery items from data."""
        data = presentation_ready.get("researched_data", {})

        gallery_result = self.extract_gallery(data=str(data))

        return {
            "descriptor_type": "gallery",
            "content": gallery_result.gallery_items
            if hasattr(gallery_result, "gallery_items")
            else [],
        }

# =============================================================================
# AGENTX R014 - Mock Widget Factory
# =============================================================================
# Creates realistic mock widgets for E2E testing
# =============================================================================

import uuid
from datetime import datetime


class MockWidgetFactory:
    """Factory for creating mock widgets that match frontend expectations."""

    WIDGET_TYPES = [
        "markdown",
        "card",
        "chart",
        "form",
        "image",
        "gallery",
        "opengraph-card",
        "opengraph-gallery",
    ]

    @staticmethod
    def create_markdown_widget(content: str = "Test markdown content") -> dict:
        """Create a markdown widget."""
        return {
            "id": str(uuid.uuid4())[:8],
            "type": "markdown",
            "timestamp": datetime.utcnow().isoformat(),
            "content": content,
            "metadata": {
                "word_count": len(content.split()),
                "citation_count": 2,
            },
        }

    @staticmethod
    def create_card_widget(title: str = "Test Card") -> dict:
        """Create a card widget."""
        return {
            "id": str(uuid.uuid4())[:8],
            "type": "card",
            "timestamp": datetime.utcnow().isoformat(),
            "title": title,
            "content": "Card content goes here",
            "metadata": {
                "priority": "high",
            },
        }

    @staticmethod
    def create_chart_widget(chart_type: str = "bar") -> dict:
        """Create a chart widget."""
        return {
            "id": str(uuid.uuid4())[:8],
            "type": "chart",
            "timestamp": datetime.utcnow().isoformat(),
            "content": {
                "chart_type": chart_type,
                "data": {
                    "labels": ["A", "B", "C"],
                    "datasets": [
                        {
                            "label": "Dataset 1",
                            "data": [10, 20, 30],
                        }
                    ],
                },
                "options": {
                    "responsive": True,
                },
            },
            "metadata": {
                "data_points": 3,
                "chart_type": chart_type,
            },
        }

    @staticmethod
    def create_form_widget() -> dict:
        """Create a form widget."""
        return {
            "id": str(uuid.uuid4())[:8],
            "type": "form",
            "timestamp": datetime.utcnow().isoformat(),
            "content": [
                {
                    "name": "name",
                    "type": "text",
                    "label": "Name",
                    "required": True,
                },
                {
                    "name": "email",
                    "type": "email",
                    "label": "Email",
                    "required": True,
                },
            ],
            "metadata": {
                "field_count": 2,
            },
        }

    @staticmethod
    def create_image_widget() -> dict:
        """Create an image widget (as OpenGraph card)."""
        return {
            "id": str(uuid.uuid4())[:8],
            "type": "opengraph-card",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "url": "https://example.com/image.jpg",
                "title": "Test Image",
                "description": "A test image description",
                "site_name": "Example Site",
            },
        }

    @staticmethod
    def create_gallery_widget(item_count: int = 4) -> dict:
        """Create a gallery widget."""
        items = [
            {
                "url": f"https://example.com/image{i}.jpg",
                "title": f"Image {i}",
                "caption": f"Caption for image {i}",
            }
            for i in range(item_count)
        ]

        return {
            "id": str(uuid.uuid4())[:8],
            "type": "opengraph-gallery",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "images": items,
                "item_count": item_count,
            },
        }

    @classmethod
    def create_widget(cls, widget_type: str) -> dict:
        """Create a widget of the specified type."""
        widget_map = {
            "markdown": cls.create_markdown_widget,
            "card": cls.create_card_widget,
            "chart": cls.create_chart_widget,
            "form": cls.create_form_widget,
            "image": cls.create_image_widget,
            "gallery": cls.create_gallery_widget,
            "opengraph-card": cls.create_image_widget,
            "opengraph-gallery": cls.create_gallery_widget,
        }

        factory_func = widget_map.get(widget_type, cls.create_markdown_widget)
        return factory_func()

    @classmethod
    def create_widget_sequence(cls, types: list[str] | None = None) -> list[dict]:
        """Create a sequence of widgets for testing.

        Args:
            types: List of widget types to create. Defaults to all types.

        Returns:
            List of widget descriptors
        """
        if types is None:
            types = cls.WIDGET_TYPES

        return [cls.create_widget(t) for t in types]

    @staticmethod
    def validate_widget_structure(widget: dict) -> tuple[bool, list[str]]:
        """Validate that a widget has the required fields.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Required fields
        required_fields = ["id", "type", "timestamp"]
        for field in required_fields:
            if field not in widget:
                errors.append(f"Missing required field: {field}")

        # type must be one of the known types
        widget_type = widget.get("type")
        if widget_type and widget_type not in MockWidgetFactory.WIDGET_TYPES:
            errors.append(f"Unknown widget type: {widget_type}")

        return len(errors) == 0, errors

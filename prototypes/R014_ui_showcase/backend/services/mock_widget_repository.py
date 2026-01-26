# =============================================================================
# AGENTX Mock Widget Repository
# =============================================================================
# Repository for loading mock widget data
# =============================================================================

"""Repository for loading mock widget data.

Follows Repository pattern from DDD - separates data access from business logic.
"""

import json
import logging
from pathlib import Path

MOCK_DATA_PATH = Path(__file__).parent / "mock_data" / "widgets.json"
logger = logging.getLogger(__name__)


class MockWidgetRepository:
    """Repository for loading mock widget data.

    Follows Repository pattern from DDD - separates data access from business logic.
    """

    def __init__(self, data_path: Path = MOCK_DATA_PATH):
        self._data_path = data_path
        self._cache: dict | None = None

    def load(self) -> dict:
        """Load mock widget data from JSON file.

        Returns:
            Dictionary containing widget definitions and delivery defaults
        """
        if self._cache is not None:
            return self._cache

        if not self._data_path.exists():
            raise FileNotFoundError(f"Mock data file not found: {self._data_path}")

        with open(self._data_path, "r") as f:
            data = json.load(f)

        self._cache = data
        logger.info(f"Loaded mock data from {self._data_path}")
        return data

    def get_widget(self, widget_type: str) -> dict | None:
        """Get a specific widget type from the mock data.

        Args:
            widget_type: Type of widget (chart, card, form, markdown)

        Returns:
            Widget data dict or None if not found
        """
        data = self.load()
        return data.get("widgets", {}).get(widget_type)

    def get_available_widget_types(self) -> list[str]:
        """Get list of available widget types.

        Returns:
            List of widget type names
        """
        data = self.load()
        return list(data.get("widgets", {}).keys())

    def get_delivery_defaults(self) -> dict:
        """Get default delivery configuration.

        Returns:
            Dictionary with delays and total_duration
        """
        data = self.load()
        return data.get("delivery_defaults", {"delays": [0.0], "total_duration": 1.0})

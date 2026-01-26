# =============================================================================
# AGENTX Mock Widget Sender CLI
# =============================================================================
# CLI entry point for mock widget sender
# =============================================================================

"""CLI entry point for mock widget sender.

Run with: uv run python services/mock_widget_sender.py [chart] [card] [form] [markdown]
"""

import asyncio
import sys

from services.mock_widget_repository import MockWidgetRepository
from services.mock_widget_sender import MockWidgetSender


def main() -> None:
    """CLI entry point for mock widget sender."""
    # Parse command line arguments
    widget_types = sys.argv[1:] if len(sys.argv) > 1 else None

    # Create dependencies (Dependency Injection)
    repository = MockWidgetRepository()
    sender = MockWidgetSender(repository)

    # Run with: uv run python services/mock_widget_sender.py [chart] [card] [form] [markdown]
    asyncio.run(sender.send_widgets(widget_types))


if __name__ == "__main__":
    main()

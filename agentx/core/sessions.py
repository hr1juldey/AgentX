"""Session-related dependencies for AGENTX."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from agentx.infrastructure.memory.session_state_manager import SessionStateManager

logger = logging.getLogger(__name__)

_session_manager: SessionStateManager | None = None


def get_session_manager() -> SessionStateManager:
    """Get the singleton SessionStateManager."""
    from agentx.infrastructure.memory.session_state_manager import (
        SessionStateManager,
    )

    global _session_manager

    if _session_manager is None:
        _session_manager = SessionStateManager()
        logger.info("SessionStateManager initialized")

    return _session_manager

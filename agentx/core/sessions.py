"""Session-related dependencies for AGENTX."""

import logging
from typing import TYPE_CHECKING

from agentx.core.config import settings

if TYPE_CHECKING:
    from agentx.infrastructure.memory.session_state_manager import SessionStateManager

logger = logging.getLogger(__name__)

_session_manager: "SessionStateManager" | None = None


def get_session_manager() -> SessionStateManager:
    """Get the singleton SessionStateManager."""
    from agentx.infrastructure.memory.session_state_manager import (
        SessionStateManager,
    )

    global _session_manager

    if _session_manager is None:
        timeout = int(getattr(settings, "session_timeout_seconds", 300))
        _session_manager = SessionStateManager(session_timeout_seconds=timeout)
        logger.info("SessionStateManager initialized")

    return _session_manager

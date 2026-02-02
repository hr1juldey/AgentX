"""Session management for agent query execution.

Handles session retrieval and creation for query processing.
"""

import logging
from uuid import UUID

from agentx.application.dtos.agent_dtos import ExecuteAgentQueryRequest
from agentx.core.dependencies import get_agent_session_repository
from agentx.domain.entities.agent_session import AgentSessionEntity, SHA256Hash

logger = logging.getLogger(__name__)


async def get_or_create_session(
    request: ExecuteAgentQueryRequest,
) -> AgentSessionEntity:
    """Get existing session or create new one.

    Args:
        request: The query request DTO.

    Returns:
        AgentSessionEntity: The session entity.
    """
    session_repository = get_agent_session_repository()

    if request.session_id:
        session = await session_repository.find_by_id(UUID(request.session_id))
        if session:
            logger.info(f"[Session] Using existing session: {session.session_id}")
            return session

    # Create new session
    user_hash = SHA256Hash.from_string(request.user_id or "anonymous")
    session = AgentSessionEntity.create(user_hash)
    await session_repository.save(session)
    logger.info(f"[Session] Created new session: {session.session_id}")
    return session

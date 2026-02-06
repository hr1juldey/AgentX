"""Session state manager for voice conversation sessions."""

import logging
from datetime import datetime, timedelta, timezone

import dspy

from agentx.application.agents.conversation import ConversationAgent
from agentx.core.config import settings
from agentx.domain.entities.session import SessionState

logger = logging.getLogger(__name__)


class SessionStateManager:
    """Manages voice conversation session state in memory."""

    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}
        self._session_timeout = timedelta(seconds=settings.session_timeout_seconds)

    def get_or_create_session(
        self, session_id: str, user_id: str = "default"
    ) -> SessionState:
        if session_id in self._sessions:
            session = self._sessions[session_id]
            session.update_activity()
            logger.debug(f"Resumed session: {session_id}")
            return session

        agent = ConversationAgent(user_id=user_id)
        session = SessionState(session_id=session_id, agent=agent, user_id=user_id)
        self._sessions[session_id] = session
        logger.info(f"Created new session: {session_id}")
        return session

    def cleanup_expired_sessions(self) -> int:
        now = datetime.now(timezone.utc)
        expired_ids = [
            sid
            for sid, state in self._sessions.items()
            if now - state.last_activity > self._session_timeout
        ]
        for sid in expired_ids:
            del self._sessions[sid]
            logger.info(f"Cleaned up expired session: {sid}")
        return len(expired_ids)

    def add_user_message(self, session_id: str, message: str) -> None:
        if session_id not in self._sessions:
            logger.warning(f"Session not found: {session_id}")
            return
        self._sessions[session_id].update_activity()

    def add_assistant_message(
        self, session_id: str, message: str, prediction: dspy.Prediction
    ) -> None:
        if session_id not in self._sessions:
            logger.warning(f"Session not found: {session_id}")
            return
        session = self._sessions[session_id]
        # DSPy Prediction is dict-like; convert explicitly for type checker
        session.history.messages.append({"question": message, **dict(prediction)})
        session.update_activity()

    def get_history(self, session_id: str) -> dspy.History | None:
        session = self._sessions.get(session_id)
        return session.history if session else None

    def remove_session(self, session_id: str) -> None:
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Removed session: {session_id}")

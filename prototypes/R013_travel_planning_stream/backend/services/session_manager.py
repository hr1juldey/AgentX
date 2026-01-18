# =============================================================================
# AGENTX R013 - Session Manager for Conversation History
# =============================================================================
# Maintains conversation history across WebSocket connections
# =============================================================================

import logging
import uuid
from dataclasses import dataclass, field

import dspy

logger = logging.getLogger(__name__)


@dataclass
class ConversationTurn:
    """Single conversation turn."""

    question: str
    answer: str
    timestamp: float = field(default_factory=lambda: __import__("time").time())


@dataclass
class Session:
    """Conversation session with history."""

    session_id: str
    history: dspy.History
    turns: list[ConversationTurn] = field(default_factory=list)

    def append_turn(self, question: str, answer: str) -> None:
        """Append a conversation turn to history."""
        turn = ConversationTurn(question=question, answer=answer)
        self.turns.append(turn)

        # Update DSPy History
        # History.messages expects dict with question and answer
        self.history.messages.append({"question": question, "answer": answer})
        logger.debug(f"Session {self.session_id}: Added turn ({len(self.turns)} total)")


class SessionManager:
    """Manages conversation sessions with history persistence."""

    def __init__(self) -> None:
        """Initialize session manager with empty session storage."""
        self._sessions: dict[str, Session] = {}

    def create_session(self) -> Session:
        """Create a new conversation session.

        Returns:
            Newly created Session with empty history
        """
        session_id = str(uuid.uuid4())
        session = Session(
            session_id=session_id,
            history=dspy.History(messages=[]),
        )
        self._sessions[session_id] = session
        logger.info(f"Created new session: {session_id}")
        return session

    def get_session(self, session_id: str) -> Session | None:
        """Get existing session by ID.

        Args:
            session_id: Session UUID

        Returns:
            Session if found, None otherwise
        """
        return self._sessions.get(session_id)

    def get_or_create_session(self, session_id: str | None) -> Session:
        """Get existing session or create new one.

        Args:
            session_id: Optional session UUID. If None, creates new session.

        Returns:
            Session (existing or newly created)
        """
        if session_id is None:
            return self.create_session()

        session = self.get_session(session_id)
        if session is None:
            logger.warning(f"Session {session_id} not found, creating new one")
            return self.create_session()

        return session

    def delete_session(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: Session UUID

        Returns:
            True if session was deleted, False if not found
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False

    def get_session_count(self) -> int:
        """Get total number of active sessions."""
        return len(self._sessions)


# Global session manager instance
_session_manager: SessionManager | None = None


def get_session_manager() -> SessionManager:
    """Get global session manager instance.

    Returns:
        Shared SessionManager instance

    Raises:
        RuntimeError: If session manager not initialized
    """
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager

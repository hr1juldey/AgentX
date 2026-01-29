"""Agent session domain entity.

Locked from LLD: docs/engineering/lld/domain_model.md:38-110
Represents a user's conversation session with the AI agent.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from agentx.domain.entities.enums import SessionState


@dataclass(frozen=True)
class SHA256Hash:
    """SHA-256 hash value object for user identifiers.

    Immutable value object for secure user identification.
    """

    value: str

    def __post_init__(self) -> None:
        """Validate SHA-256 hash format."""
        if not isinstance(self.value, str) or len(self.value) != 64:
            msg = "SHA-256 hash must be 64 character hex string"
            raise ValueError(msg)

    @classmethod
    def from_string(cls, value: str) -> "SHA256Hash":
        """Create hash from string.

        Args:
            value: Input string to hash.

        Returns:
            SHA256Hash: Hash value object.
        """
        import hashlib

        hash_value = hashlib.sha256(value.encode()).hexdigest()
        return cls(hash_value)


@dataclass
class AgentSessionEntity:
    """Represents a user's conversation session with the AI agent.

    Lifecycle: INITIALIZING -> ACTIVE -> PAUSED/CLOSED

    Attributes:
        session_id: Unique session identifier.
        user_id: SHA-256 hash of user identifier.
        state: Current session state.
        created_at: Session creation timestamp.
        modified_at: Last modification timestamp.
        last_activity_at: Last user activity timestamp.
        current_reasoning_step: Current reasoning step (for multi-step).
        total_tool_calls: Total tool executions in session.
    """

    session_id: UUID
    user_id: SHA256Hash
    state: SessionState
    created_at: datetime
    modified_at: datetime
    last_activity_at: datetime
    current_reasoning_step: int = 0
    total_tool_calls: int = 0

    @classmethod
    def create(cls, user_id: SHA256Hash) -> "AgentSessionEntity":
        """Create a new session.

        Args:
            user_id: User identifier hash.

        Returns:
            AgentSessionEntity: New session in INITIALIZING state.
        """
        now = datetime.now()
        return cls(
            session_id=uuid4(),
            user_id=user_id,
            state=SessionState.INITIALIZING,
            created_at=now,
            modified_at=now,
            last_activity_at=now,
        )

    def activate(self) -> None:
        """Transition session to ACTIVE state."""
        if self.state == SessionState.INITIALIZING:
            self.state = SessionState.ACTIVE
            self._update_activity()

    def pause(self) -> None:
        """Transition session to PAUSED state."""
        if self.state == SessionState.ACTIVE:
            self.state = SessionState.PAUSED
            self._update_activity()

    def close(self) -> None:
        """Transition session to CLOSED state."""
        if self.state in (SessionState.ACTIVE, SessionState.PAUSED):
            self.state = SessionState.CLOSED
            self._update_activity()

    def increment_reasoning_step(self) -> None:
        """Increment the current reasoning step counter."""
        self.current_reasoning_step += 1
        self._update_activity()

    def increment_tool_calls(self) -> None:
        """Increment the total tool calls counter."""
        self.total_tool_calls += 1
        self._update_activity()

    def _update_activity(self) -> None:
        """Update last activity timestamp."""
        self.modified_at = datetime.now()
        self.last_activity_at = datetime.now()

    def is_active(self) -> bool:
        """Check if session is in active state.

        Returns:
            bool: True if session is active.
        """
        return self.state == SessionState.ACTIVE

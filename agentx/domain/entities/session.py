"""Session entity for voice conversation state."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import dspy

if TYPE_CHECKING:
    from agentx.application.agents.conversation import ConversationAgent


@dataclass
class SessionState:
    """State for a single voice conversation session."""

    session_id: str
    agent: ConversationAgent
    history: dspy.History = field(default_factory=lambda: dspy.History(messages=[]))
    user_id: str = "default"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict = field(default_factory=dict)

    def update_activity(self) -> None:
        self.last_activity = datetime.now(timezone.utc)

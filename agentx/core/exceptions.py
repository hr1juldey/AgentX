"""Global exception definitions for AGENTX."""


class AgentException(Exception):
    """Base exception for all AGENTX errors."""

    pass


class GraphCompilationException(AgentException):
    """Raised when graph compilation fails."""

    pass


class MemoryException(AgentException):
    """Raised when memory operations fail."""

    pass


class VoiceException(AgentException):
    """Raised when voice operations fail."""

    pass


class RetrievalException(AgentException):
    """Raised when retrieval operations fail."""

    pass

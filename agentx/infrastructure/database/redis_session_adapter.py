"""Redis session adapter facade for backward compatibility.

This facade maintains backward compatibility with existing imports.
Actual implementation has been moved to the redis/ subdirectory.
"""

from agentx.infrastructure.database.redis.redis_session_adapter import (
    RedisSessionAdapter,
)

__all__ = [
    "RedisSessionAdapter",
]

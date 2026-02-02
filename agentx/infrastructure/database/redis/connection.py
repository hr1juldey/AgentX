"""Redis connection management for session adapter."""

import redis.asyncio as redis

from agentx.core.config import get_settings


class RedisConnectionManager:
    """Manages Redis client connection."""

    def __init__(self) -> None:
        """Initialize connection manager."""
        settings = get_settings()
        self._client: redis.Redis | None = None
        self._url = settings.database.redis_url
        self._ttl = 86400  # 24 hours default

    async def get_client(self) -> redis.Redis:
        """Get or create Redis client.

        Returns:
            redis.Redis: The Redis client instance.
        """
        if self._client is None:
            self._client = await redis.from_url(
                self._url, encoding="utf-8", decode_responses=True
            )
        return self._client

    @property
    def ttl(self) -> int:
        """Get the default TTL for session data."""
        return self._ttl

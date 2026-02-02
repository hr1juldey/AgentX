"""Redis lifespan management for LangGraph memory.

This module provides async context management for Redis connections
used by LangGraph checkpointers and store.

Following Clean Architecture: infrastructure layer handles external concerns.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from langgraph.checkpoint.redis.aio import AsyncRedisSaver  # type: ignore[import]
from langgraph.store.redis.aio import AsyncRedisStore  # type: ignore[import]

from agentx.infrastructure.memory.checkpointer_config import set_checkpointer
from agentx.infrastructure.memory.langgraph_store_adapter import set_store


@asynccontextmanager
async def redis_lifespan(db_uri: str) -> AsyncGenerator[None, None]:
    """Manage Redis connection lifecycle for LangGraph memory.

    Initializes both checkpointer (graph memory) and store (agent memory)
    using async context managers.

    Args:
        db_uri: Redis connection string (e.g., "redis://localhost:6380")

    Yields:
        None: Control returns to caller while connections are active
    """
    async with (
        AsyncRedisStore.from_conn_string(db_uri) as store,
        AsyncRedisSaver.from_conn_string(db_uri) as checkpointer,
    ):
        # Set global instances for dependency injection
        set_store(store)
        set_checkpointer(checkpointer)
        yield

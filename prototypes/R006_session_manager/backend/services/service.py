"""Session service with Redis storage and fallback to in-memory."""

import json
import logging
import secrets
from datetime import datetime, timedelta
from typing import List, Optional

import redis
from redis.exceptions import ConnectionError, RedisError

from config.settings import settings
from models.schemas import SessionCreate, SessionResponse

logger = logging.getLogger(__name__)


class SessionService:
    """Service for managing sessions with Redis backend."""

    def __init__(self):
        """Initialize session service with Redis connection."""
        self.redis_client: Optional[redis.Redis] = None
        self.fallback_storage: dict = {}  # Fallback in-memory storage
        self._use_fallback = False
        self._initialize_redis()

    def _initialize_redis(self) -> None:
        """Initialize Redis connection with graceful fallback."""
        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                max_connections=settings.redis_max_connections,
                socket_timeout=settings.redis_socket_timeout,
                socket_connect_timeout=settings.redis_socket_connect_timeout,
                decode_responses=True,
            )
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Redis connection established successfully")
        except (ConnectionError, RedisError) as e:
            logger.warning(f"⚠️  Redis connection failed: {e}")
            logger.warning("🔄 Falling back to in-memory storage (not recommended for production)")
            self._use_fallback = True
            self.redis_client = None

    def _generate_token(self) -> str:
        """Generate a secure session token."""
        return secrets.token_urlsafe(settings.session_token_length)

    def _generate_id(self) -> str:
        """Generate a unique session ID."""
        return secrets.token_hex(16)

    def _serialize_session(self, session_data: dict) -> str:
        """Serialize session data for storage."""
        return json.dumps(session_data)

    def _deserialize_session(self, data: str) -> dict:
        """Deserialize session data from storage."""
        return json.loads(data)

    def _get_redis_key(self, session_id: str) -> str:
        """Get Redis key for a session."""
        return f"session:{session_id}"

    def _get_user_sessions_key(self, user_id: str) -> str:
        """Get Redis key for user's session list."""
        return f"user_sessions:{user_id}"

    async def create_session(
        self,
        session_data: SessionCreate,
        user_id: str,
    ) -> SessionResponse:
        """
        Create a new session.

        Args:
            session_data: Session creation data
            user_id: User ID for the session

        Returns:
            Created session response
        """
        session_id = self._generate_id()
        session_token = self._generate_token()
        now = datetime.utcnow()

        session = {
            "id": session_id,
            "session_token": session_token,
            "user_id": user_id,
            "device_name": session_data.device_name,
            "device_type": session_data.device_type.value,
            "user_agent": session_data.user_agent,
            "ip_address": session_data.ip_address,
            "created_at": now.isoformat(),
            "last_active": now.isoformat(),
            "is_active": True,
        }

        expiry_seconds = settings.session_expiry_hours * 3600

        if self._use_fallback:
            # Fallback to in-memory storage
            self.fallback_storage[session_id] = session
            # Add to user's session list
            user_sessions_key = f"user_sessions:{user_id}"
            if user_sessions_key not in self.fallback_storage:
                self.fallback_storage[user_sessions_key] = []
            if session_id not in self.fallback_storage[user_sessions_key]:
                self.fallback_storage[user_sessions_key].append(session_id)
            logger.debug(f"Created session {session_id} in in-memory storage")
        else:
            # Store in Redis
            key = self._get_redis_key(session_id)
            self.redis_client.setex(
                key,
                expiry_seconds,
                self._serialize_session(session),
            )
            # Add to user's session list
            user_sessions_key = self._get_user_sessions_key(user_id)
            self.redis_client.sadd(user_sessions_key, session_id)
            self.redis_client.expire(user_sessions_key, expiry_seconds)
            logger.debug(f"Created session {session_id} in Redis")

        return SessionResponse(**session)

    async def get_session(self, session_id: str) -> Optional[SessionResponse]:
        """
        Get a session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session response if found, None otherwise
        """
        if self._use_fallback:
            session = self.fallback_storage.get(session_id)
            if session:
                # Update last_active on access
                session["last_active"] = datetime.utcnow().isoformat()
                return SessionResponse(**session)
            return None
        else:
            key = self._get_redis_key(session_id)
            data = self.redis_client.get(key)
            if data:
                session = self._deserialize_session(data)
                # Update last_active on access
                session["last_active"] = datetime.utcnow().isoformat()
                # Update in Redis
                self.redis_client.setex(
                    key,
                    settings.session_expiry_hours * 3600,
                    self._serialize_session(session),
                )
                return SessionResponse(**session)
            return None

    async def list_sessions(self, user_id: str) -> List[SessionResponse]:
        """
        List all sessions for a user.

        Args:
            user_id: User ID

        Returns:
            List of session responses
        """
        sessions = []

        if self._use_fallback:
            user_sessions_key = f"user_sessions:{user_id}"
            session_ids = self.fallback_storage.get(user_sessions_key, [])
            for session_id in session_ids:
                session = self.fallback_storage.get(session_id)
                if session and session.get("is_active"):
                    sessions.append(SessionResponse(**session))
        else:
            user_sessions_key = self._get_user_sessions_key(user_id)
            session_ids = self.redis_client.smembers(user_sessions_key)
            for session_id in session_ids:
                key = self._get_redis_key(session_id)
                data = self.redis_client.get(key)
                if data:
                    session = self._deserialize_session(data)
                    if session.get("is_active"):
                        sessions.append(SessionResponse(**session))

        return sessions

    async def update_session(
        self,
        session_id: str,
        is_active: bool,
    ) -> Optional[SessionResponse]:
        """
        Update a session.

        Args:
            session_id: Session ID
            is_active: New active status

        Returns:
            Updated session response if found, None otherwise
        """
        if self._use_fallback:
            session = self.fallback_storage.get(session_id)
            if session:
                session["is_active"] = is_active
                session["last_active"] = datetime.utcnow().isoformat()
                return SessionResponse(**session)
            return None
        else:
            key = self._get_redis_key(session_id)
            data = self.redis_client.get(key)
            if data:
                session = self._deserialize_session(data)
                session["is_active"] = is_active
                session["last_active"] = datetime.utcnow().isoformat()
                # Update in Redis
                self.redis_client.setex(
                    key,
                    settings.session_expiry_hours * 3600,
                    self._serialize_session(session),
                )
                return SessionResponse(**session)
            return None

    async def delete_session(self, session_id: str, user_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session ID
            user_id: User ID

        Returns:
            True if deleted, False otherwise
        """
        if self._use_fallback:
            if session_id in self.fallback_storage:
                del self.fallback_storage[session_id]
                # Remove from user's session list
                user_sessions_key = f"user_sessions:{user_id}"
                if user_sessions_key in self.fallback_storage:
                    if session_id in self.fallback_storage[user_sessions_key]:
                        self.fallback_storage[user_sessions_key].remove(session_id)
                return True
            return False
        else:
            key = self._get_redis_key(session_id)
            # Delete session
            result = self.redis_client.delete(key)
            # Remove from user's session list
            user_sessions_key = self._get_user_sessions_key(user_id)
            self.redis_client.srem(user_sessions_key, session_id)
            return result > 0

    async def delete_all_sessions(self, user_id: str) -> int:
        """
        Delete all sessions for a user.

        Args:
            user_id: User ID

        Returns:
            Number of sessions deleted
        """
        count = 0

        if self._use_fallback:
            user_sessions_key = f"user_sessions:{user_id}"
            session_ids = self.fallback_storage.get(user_sessions_key, [])
            for session_id in session_ids:
                if session_id in self.fallback_storage:
                    del self.fallback_storage[session_id]
                    count += 1
            self.fallback_storage[user_sessions_key] = []
        else:
            user_sessions_key = self._get_user_sessions_key(user_id)
            session_ids = self.redis_client.smembers(user_sessions_key)
            for session_id in session_ids:
                key = self._get_redis_key(session_id)
                if self.redis_client.delete(key):
                    count += 1
            # Clear user's session list
            self.redis_client.delete(user_sessions_key)

        return count

    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions (manual cleanup for fallback storage).

        Returns:
            Number of sessions cleaned up
        """
        if not self._use_fallback:
            # Redis handles expiration automatically
            return 0

        # For in-memory storage, we need to check manually
        count = 0
        now = datetime.utcnow()
        expiry_threshold = now - timedelta(hours=settings.session_expiry_hours)

        keys_to_delete = []
        for key, value in self.fallback_storage.items():
            if key.startswith("session:"):
                session = value
                created_at = datetime.fromisoformat(session["created_at"])
                if created_at < expiry_threshold:
                    keys_to_delete.append(key)

        for key in keys_to_delete:
            del self.fallback_storage[key]
            count += 1

        if count > 0:
            logger.info(f"Cleaned up {count} expired sessions from in-memory storage")

        return count

    def get_storage_status(self) -> dict:
        """
        Get the current storage status.

        Returns:
            Dictionary with storage information
        """
        if self._use_fallback:
            return {
                "storage_type": "in-memory",
                "warning": "Redis unavailable - using in-memory fallback (not recommended for production)",
                "active_sessions": len(
                    [k for k in self.fallback_storage.keys() if k.startswith("session:")]
                ),
            }
        else:
            try:
                info = self.redis_client.info()
                return {
                    "storage_type": "redis",
                    "connected": True,
                    "used_memory_human": info.get("used_memory_human", "unknown"),
                    "connected_clients": info.get("connected_clients", 0),
                }
            except RedisError as e:
                return {
                    "storage_type": "redis",
                    "connected": False,
                    "error": str(e),
                }


# Global session service instance
session_service = SessionService()

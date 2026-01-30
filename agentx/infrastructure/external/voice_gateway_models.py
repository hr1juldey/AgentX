"""Voice gateway data structures.

Provides configuration and session dataclasses for VoiceGatewayService.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import WebSocket

from agentx.infrastructure.external.voice_protocol import KYUTAI_STT_URL, KYUTAI_TTS_URL


@dataclass
class VoiceGatewayConfig:
    """Voice gateway configuration."""

    stt_url: str = KYUTAI_STT_URL
    tts_url: str = KYUTAI_TTS_URL
    max_concurrent_sessions: int = 5
    use_voice_sdk: bool = False


@dataclass
class VoiceSession:
    """Active voice session."""

    session_id: UUID
    frontend_ws: WebSocket
    stt_ws: Any | None = None  # type: ignore[valid-type]
    tts_ws: Any | None = None  # type: ignore[valid-type]
    interrupted: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

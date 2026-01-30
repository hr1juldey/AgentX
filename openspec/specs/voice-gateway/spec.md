# Spec: voice-gateway

**File**: `specs/voice-gateway/spec.md`

**Generated**: 2026-01-31
**Change**: c010-voice-client

---

## 1.1 Purpose

Define the backend VoiceGatewayService for bridging frontend WebSocket connections to external kyutai voice-server. This spec covers message routing, dual WebSocket management (STT + TTS), and kyutai protocol handling.

---

## 1.2 Scope

**In Scope**:
- VoiceGatewayService for message routing (frontend ↔ kyutai)
- Dual WebSocket management (STT + TTS connections to kyutai)
- Kyutai protocol message handling (Config, Audio, Text, Error, Eos, Heartbeat)
- Health check endpoint for kyutai availability
- Integration with C003 agent pipeline

**Out of Scope**:
- Conversational state management (covered by conversational-state spec)
- Text stream buffering (covered by voice-stream-handling spec)
- Audio processing (handled by kyutai)

---

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-VG-001 | VoiceGatewayService MUST manage frontend WebSocket connection on port 8019 | Must |
| FR-VG-002 | VoiceGatewayService MUST manage STT WebSocket to kyutai (ws://localhost:16000/api/v1/ws/stt) | Must |
| FR-VG-003 | VoiceGatewayService MUST manage TTS WebSocket to kyutai (ws://localhost:16000/api/v1/ws/tts) | Must |
| FR-VG-004 | VoiceGatewayService MUST route Audio messages from frontend to kyutai STT | Must |
| FR-VG-005 | VoiceGatewayService MUST route Text messages from kyutai STT to frontend | Must |
| FR-VG-006 | VoiceGatewayService MUST route Text messages to kyutai TTS | Must |
| FR-VG-007 | VoiceGatewayService MUST route Audio messages from kyutai TTS to frontend | Must |
| FR-VG-008 | VoiceGatewayService MUST handle Error messages from kyutai and translate to frontend | Must |
| FR-VG-009 | VoiceGatewayService MUST provide health check endpoint at GET /api/v1/voice/kyutai/status | Must |
| FR-VG-010 | VoiceGatewayService MUST integrate with C003 ExecuteAgentQueryUseCase | Must |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-VG-001 | VoiceGatewayService MUST use absolute imports only | Must |
| NFR-VG-002 | VoiceGatewayService MUST pass ruff check and ruff format | Must |
| NFR-VG-003 | VoiceGatewayService MUST pass pyrefly type checking | Must |
| NFR-VG-004 | VoiceGatewayService MUST handle WebSocket messages within 50ms | Should |
| NFR-VG-005 | VoiceGatewayService file MUST NOT exceed 150 lines | Must |

---

## 1.4 Data Model

### File: agentx/infrastructure/external/voice_gateway_service.py

```python
"""Voice gateway service for external kyutai integration."""

import asyncio
import json
import base64
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Awaitable, Callable
from uuid import UUID, uuid4

import websockets
from fastapi import WebSocket

from agentx.application.use_cases.execute_agent_query import (
    ExecuteAgentQueryUseCase,
)
from agentx.application.dtos.agent_dtos import (
    ExecuteAgentQueryRequest,
    ExecuteAgentQueryResponse,
)
from agentx.application.dtos.voice_gateway_dtos import (
    KyutaiMessage,
    KyutaiMessageType,
)


class VoiceGatewayError(Exception):
    """Voice gateway error."""


class KyutaiConnectionError(VoiceGatewayError):
    """Kyutai connection error."""


@dataclass
class VoiceGatewayConfig:
    """Voice gateway configuration."""

    stt_url: str = "ws://localhost:16000/api/v1/ws/stt?encoding=json"
    tts_url: str = "ws://localhost:16000/api/v1/ws/tts?encoding=json"
    max_concurrent_sessions: int = 5
    session_timeout: int = 300  # 5 minutes


@dataclass
class VoiceSession:
    """Active voice session."""

    session_id: UUID
    frontend_ws: WebSocket
    stt_ws: websockets.WebSocketClientProtocol | None = None
    tts_ws: websockets.WebSocketClientProtocol | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity_at: datetime = field(default_factory=datetime.utcnow)
    interrupted: bool = False


class VoiceGatewayService:
    """Gateway for routing messages between frontend and kyutai voice-server."""

    def __init__(self, config: VoiceGatewayConfig) -> None:
        """Initialize voice gateway service."""
        self._config = config
        self._sessions: dict[UUID, VoiceSession] = {}
        self._query_use_case = ExecuteAgentQueryUseCase()

    async def handle_session(self, frontend_ws: WebSocket, session_id: UUID) -> None:
        """Handle a voice session WebSocket connection.

        Args:
            frontend_ws: Frontend WebSocket connection.
            session_id: Session identifier.

        Raises:
            VoiceGatewayError: If session cannot be established.
        """
        if len(self._sessions) >= self._config.max_concurrent_sessions:
            raise VoiceGatewayError("Max concurrent sessions reached")

        # Connect to kyutai STT and TTS
        stt_ws = await websockets.connect(self._config.stt_url)
        tts_ws = await websockets.connect(self._config.tts_url)

        # Send config to kyutai
        config_msg = KyutaiMessage(
            type=KyutaiMessageType.CONFIG,
            data={
                "streaming_mode": "both",
                "input_format": "int16",
            },
            session_id=str(session_id),
            timestamp=datetime.utcnow().timestamp(),
        )
        await stt_ws.send(config_msg.to_json())
        await tts_ws.send(config_msg.to_json())

        # Create session
        session = VoiceSession(
            session_id=session_id,
            frontend_ws=frontend_ws,
            stt_ws=stt_ws,
            tts_ws=tts_ws,
        )
        self._sessions[session_id] = session

        try:
            # Run input/output tasks concurrently
            await asyncio.gather(
                self._input_task(session),
                self._output_task(session),
            )
        finally:
            await self._cleanup_session(session_id)

    async def _input_task(self, session: VoiceSession) -> None:
        """Handle messages from frontend to kyutai.

        Args:
            session: Active voice session.
        """
        try:
            while True:
                data = await session.frontend_ws.receive_json()
                message = KyutaiMessage.from_dict(data)

                session.last_activity_at = datetime.utcnow()

                if message.type == KyutaiMessageType.AUDIO:
                    # Route audio to STT
                    if session.stt_ws:
                        await session.stt_ws.send(message.to_json())
                elif message.type == KyutaiMessageType.TEXT:
                    # Route text to TTS (for agent response)
                    if session.tts_ws:
                        await session.tts_ws.send(message.to_json())
                elif message.type == KyutaiMessageType.INTERRUPT:
                    # Handle interruption
                    session.interrupted = True

        except Exception as e:
            raise VoiceGatewayError(f"Input task error: {e}") from e

    async def _output_task(self, session: VoiceSession) -> None:
        """Handle messages from kyutai to frontend.

        Args:
            session: Active voice session.
        """
        try:
            while True:
                # Wait for messages from either STT or TTS
                stt_task = asyncio.create_task(session.stt_ws.recv()) if session.stt_ws else None
                tts_task = asyncio.create_task(session.tts_ws.recv()) if session.tts_ws else None

                if stt_task and tts_task:
                    done, pending = await asyncio.wait(
                        [stt_task, tts_task],
                        return_when=asyncio.FIRST_COMPLETED,
                    )

                    # Cancel pending tasks
                    for task in pending:
                        task.cancel()

                    # Get the completed message
                    message_data = list(done)[0].result()
                elif stt_task:
                    message_data = await stt_task
                elif tts_task:
                    message_data = await tts_task
                else:
                    break

                message = KyutaiMessage.from_json(message_data)

                # Route transcript to frontend and agent
                if message.type == KyutaiMessageType.TEXT and session.stt_ws:
                    await session.frontend_ws.send_json(message.to_dict())

                    # Pass to agent pipeline
                    await self._process_agent_response(session, message.data)

                # Route TTS audio to frontend
                elif message.type == KyutaiMessageType.AUDIO and session.tts_ws:
                    await session.frontend_ws.send_json(message.to_dict())

                # Handle errors
                elif message.type == KyutaiMessageType.ERROR:
                    await session.frontend_ws.send_json(message.to_dict())

        except Exception as e:
            raise VoiceGatewayError(f"Output task error: {e}") from e

    async def _process_agent_response(self, session: VoiceSession, transcript: str) -> None:
        """Process transcript through agent pipeline and send to TTS.

        Args:
            session: Active voice session.
            transcript: User transcript from STT.
        """
        request = ExecuteAgentQueryRequest(
            query=transcript,
            session_id=str(session.session_id),
        )

        response = await self._query_use_case.execute(request)

        # Send agent response to TTS
        if session.tts_ws:
            tts_msg = KyutaiMessage(
                type=KyutaiMessageType.TEXT,
                data=response.response,
                session_id=str(session.session_id),
                timestamp=datetime.utcnow().timestamp(),
            )
            await session.tts_ws.send(tts_msg.to_json())

    async def _cleanup_session(self, session_id: UUID) -> None:
        """Clean up a voice session.

        Args:
            session_id: Session identifier.
        """
        session = self._sessions.pop(session_id, None)
        if session:
            if session.stt_ws:
                await session.stt_ws.close()
            if session.tts_ws:
                await session.tts_ws.close()

    async def check_health(self) -> bool:
        """Check if kyutai server is available.

        Returns:
            True if kyutai is available, False otherwise.
        """
        try:
            async with websockets.connect(self._config.stt_url) as ws:
                return True
        except Exception:
            return False
```

---

## 1.5 Acceptance Criteria

- [ ] VoiceGatewayService manages frontend WebSocket on port 8019
- [ ] VoiceGatewayService manages STT WebSocket to kyutai
- [ ] VoiceGatewayService manages TTS WebSocket to kyutai
- [ ] VoiceGatewayService routes Audio messages frontend → kyutai STT
- [ ] VoiceGatewayService routes Text messages kyutai STT → frontend
- [ ] VoiceGatewayService routes Text messages to kyutai TTS
- [ ] VoiceGatewayService routes Audio messages kyutai TTS → frontend
- [ ] VoiceGatewayService handles Error messages from kyutai
- [ ] VoiceGatewayService provides health check endpoint
- [ ] VoiceGatewayService integrates with C003 ExecuteAgentQueryUseCase
- [ ] VoiceGatewayService passes ruff check, ruff format, pyrefly check
- [ ] VoiceGatewayService file under 150 lines

---

**Related Specs**:
- `voice-client` - Frontend WebSocket client
- `conversational-state` - Conversation state management
- `voice-stream-handling` - Text stream processing
- C003 agent pipeline - LLM integration

---

"""Core dependency injection for AGENTX."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

import dspy

from agentx.core.config import settings

if TYPE_CHECKING:
    from agentx.infrastructure.memory.mem0_client import Mem0Client
    from agentx.infrastructure.memory.session_state_manager import SessionStateManager
    from agentx.infrastructure.voice.voice_adapter import VoiceSDKAdapter
    from agentx.infrastructure.voice.voice_gateway import VoiceGatewayService

logger = logging.getLogger(__name__)

_lm: Optional[dspy.LM] = None
_mem0_client: Optional[Mem0Client] = None
_qdrant_client: Optional[object] = None
_agent_registry: dict = {}
_session_manager: Optional[SessionStateManager] = None
_voice_sdk_adapter: Optional[VoiceSDKAdapter] = None
_voice_gateway: Optional[VoiceGatewayService] = None


def ensure_dspy_configured() -> None:
    """Configure DSPy globally with Ollama LM."""
    from agentx.infrastructure.external.ollama import check_ollama_health

    global _lm

    if _lm is None:
        check_ollama_health()
        _lm = dspy.LM(
            model=f"ollama_chat/{settings.llm_model}", api_base=settings.llm_api_base
        )
        logger.info(f"DSPy configured with Ollama model: {settings.llm_model}")

    dspy.configure(lm=_lm)


def get_mem0_client() -> Optional[Mem0Client]:
    """Get the singleton Mem0AI client.

    Uses local Ollama for LLM/embeddings and Qdrant for vector storage.
    No API keys required.

    Returns:
        Mem0Client instance or None if unavailable
    """
    from agentx.infrastructure.memory.mem0_client import Mem0Client

    global _mem0_client
    if _mem0_client is None:
        try:
            _mem0_client = Mem0Client(
                qdrant_host=settings.mem0_qdrant_host,
                qdrant_port=settings.mem0_qdrant_port,
                llm_model=settings.mem0_llm_model,
                embedder_model=settings.mem0_embedder_model,
                embedding_dims=settings.mem0_embedding_dims,
            )
            logger.info("Mem0AI client initialized")
        except Exception as e:
            logger.warning(f"Mem0AI client initialization failed: {e}")
            logger.info("Continuing without persistent memory")
            _mem0_client = None

    return _mem0_client


def get_qdrant_client() -> object:
    """Get the singleton Qdrant client."""
    global _qdrant_client
    if _qdrant_client is None:
        raise NotImplementedError("Qdrant client not yet implemented")
    return _qdrant_client


def get_agent_registry() -> dict:
    """Get the agent registry for graph compilation."""
    return _agent_registry


def register_agent(name: str, agent_class: type) -> None:
    """Register an agent class in the agent registry."""
    _agent_registry[name] = agent_class


def get_session_manager() -> SessionStateManager:
    """Get the singleton SessionStateManager."""
    from agentx.core.sessions import get_session_manager as _get_session_manager

    return _get_session_manager()


def get_voice_sdk_adapter() -> VoiceSDKAdapter:
    """Get the singleton VoiceSDKAdapter."""
    from agentx.infrastructure.voice.voice_adapter import VoiceSDKAdapter

    global _voice_sdk_adapter
    if _voice_sdk_adapter is None:
        _voice_sdk_adapter = VoiceSDKAdapter(
            stt_url=settings.voice_kyutai_stt_url,
            tts_url=settings.voice_kyutai_tts_url,
        )
        logger.info("VoiceSDKAdapter initialized")
    return _voice_sdk_adapter


def get_voice_gateway() -> VoiceGatewayService:
    """Get the singleton VoiceGatewayService."""
    from agentx.infrastructure.voice.voice_gateway import VoiceGatewayService

    global _voice_gateway
    if _voice_gateway is None:
        _voice_gateway = VoiceGatewayService(
            session_manager=get_session_manager(),
            voice_adapter=get_voice_sdk_adapter(),
        )
        logger.info("VoiceGatewayService initialized")
    return _voice_gateway

"""Core dependency injection for AGENTX."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

import dspy

from agentx.core.config import settings

if TYPE_CHECKING:
    from agentx.infrastructure.memory.mem0_client import Mem0Client
    from agentx.infrastructure.memory.session_state_manager import SessionStateManager
    from agentx.infrastructure.retrieval.qdrant_collection_manager import (
        QdrantCollectionManager,
    )
    from agentx.infrastructure.voice.voice_adapter import VoiceSDKAdapter
    from agentx.infrastructure.voice.voice_gateway import VoiceGatewayService

logger = logging.getLogger(__name__)

_lm: Optional[dspy.LM] = None
_mem0_client: Optional[Mem0Client] = None
_qdrant_client: Optional[object] = None
# Cache of collection managers by collection name
_qdrant_collection_managers: dict[str, QdrantCollectionManager] = {}
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
    """Get the singleton Qdrant client.

    Returns:
        QdrantClient instance for vector operations
    """
    from qdrant_client import QdrantClient
    from qdrant_client.http.exceptions import UnexpectedResponse

    global _qdrant_client
    if _qdrant_client is None:
        try:
            _qdrant_client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
            )
            # Verify connection
            collections = _qdrant_client.get_collections()
            logger.info(
                f"Qdrant client initialized: {settings.qdrant_host}:{settings.qdrant_port}, "
                f"{len(collections.collections)} collections"
            )
        except UnexpectedResponse as e:
            logger.warning(f"Qdrant client initialization failed: {e}")
            logger.info("Continuing without Qdrant client")
            _qdrant_client = None
        except Exception as e:
            logger.warning(f"Qdrant client connection failed: {e}")
            logger.info("Continuing without Qdrant client")
            _qdrant_client = None
    return _qdrant_client


def get_qdrant_collection_manager(
    collection_name: str = "agentx_knowledge",
) -> Optional[QdrantCollectionManager]:
    """Get or create a Qdrant collection manager for a specific collection.

    Supports per-agent private collections and shared knowledge collections.
    Collection managers are cached by collection name.

    Args:
        collection_name: Name of the collection (e.g., "research_agent_memory",
                       "chatbot_agent_memory", or "agentx_knowledge" for shared)

    Returns:
        QdrantCollectionManager instance or None if Qdrant unavailable

    Examples:
        # Get shared knowledge collection
        shared_manager = get_qdrant_collection_manager("agentx_knowledge")

        # Get per-agent private collection
        research_manager = get_qdrant_collection_manager("research_agent_memory")
        chatbot_manager = get_qdrant_collection_manager("chatbot_agent_memory")
    """
    from agentx.infrastructure.retrieval.qdrant_collection_manager import (
        QdrantCollectionManager,
    )

    global _qdrant_collection_managers

    # Return cached manager if exists
    if collection_name in _qdrant_collection_managers:
        return _qdrant_collection_managers[collection_name]

    # Get Qdrant client
    qdrant_client = get_qdrant_client()
    if qdrant_client is None:
        logger.warning(
            f"Qdrant client unavailable, cannot create collection manager for '{collection_name}'"
        )
        return None

    try:
        manager = QdrantCollectionManager(
            qdrant_client,  # type: ignore[arg-type]
            collection_name,
        )
        # Ensure collection exists with proper configuration
        if manager.ensure_collection_exists():
            logger.info(
                f"QdrantCollectionManager initialized for '{collection_name}' and collection ready"
            )
        else:
            logger.warning(
                f"QdrantCollectionManager initialized for '{collection_name}' but collection validation failed"
            )
        # Cache the manager
        _qdrant_collection_managers[collection_name] = manager
        return manager
    except Exception as e:
        logger.warning(
            f"QdrantCollectionManager initialization failed for '{collection_name}': {e}"
        )
        return None


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

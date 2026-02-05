"""DSPy LM configuration management."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

import dspy

from agentx.core.config import settings

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

_lm: Optional[dspy.LM] = None


def ensure_dspy_configured() -> None:
    """Configure DSPy globally with Ollama LM."""
    from agentx.infrastructure.external.ollama import check_ollama_health

    global _lm

    if _lm is None:
        check_ollama_health()
        _lm = dspy.LM(
            model=f"ollama_chat/{settings.llm_model}",
            api_base=settings.llm_api_base,
        )
        logger.info(f"DSPy configured with Ollama model: {settings.llm_model}")

    dspy.configure(lm=_lm)


def get_lm() -> Optional[dspy.LM]:
    """Get the configured DSPy LM instance."""
    ensure_dspy_configured()
    return _lm

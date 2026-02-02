"""DSPy configuration dependency.

Provides DSPy LM configuration with Ollama.
"""

import dspy

from agentx.core.config import get_settings

# Global singleton state
_dspy_configured: bool = False


def configure_dspy() -> None:
    """Configure DSPy with Ollama LM.

    Uses settings from config.py. Must be called before any DSPy agent usage.
    """
    global _dspy_configured
    if _dspy_configured:
        return

    settings = get_settings()

    # Configure DSPy with Ollama
    # Note: DSPy uses "ollama_chat/" prefix for Ollama chat models
    # Ollama requires api_key="" (empty string)
    lm = dspy.LM(
        model=f"ollama_chat/{settings.llm.model}",
        api_base=settings.llm.api_base,
        api_key="",  # Ollama doesn't require API key, but DSPy needs empty string
        temperature=settings.llm.temperature,
        max_tokens=settings.llm.max_tokens,
        cache=False,  # Disable caching to avoid serialization issues with streaming
    )
    dspy.configure(lm=lm)
    _dspy_configured = True


def ensure_dspy_configured() -> None:
    """Ensure DSPy is configured with Ollama LM.

    This should be called before any DSPy agent usage.
    """
    configure_dspy()


def reset_dspy() -> None:
    """Reset DSPy configuration singleton.

    Useful for testing or clearing state.
    """
    global _dspy_configured
    _dspy_configured = False

"""Ollama external service client for health checks."""

import logging

import requests
from agentx.core.config import settings

logger = logging.getLogger(__name__)


def check_ollama_health() -> None:
    """Check if Ollama is running and accessible.

    Raises:
        ConnectionError: If Ollama is not available at the configured URL.
    """
    ollama_health_url = f"{settings.llm_api_base.rstrip('/')}/api/tags"

    try:
        response = requests.get(
            ollama_health_url,
            timeout=600,
        )
        response.raise_for_status()
        logger.info(f"Ollama is available at {settings.llm_api_base}")
    except requests.exceptions.ConnectionError as e:
        msg = (
            f"Cannot connect to Ollama at {settings.llm_api_base}. "
            f"Please ensure Ollama is running with 'ollama serve'. "
            f"Model '{settings.llm_model}' must be available."
        )
        raise ConnectionError(msg) from e
    except requests.exceptions.Timeout as e:
        msg = (
            f"Ollama at {settings.llm_api_base} timed out after 600 seconds. "
            f"The model '{settings.llm_model}' may still be loading. "
            f"Try pulling the model first: ollama pull {settings.llm_model}"
        )
        raise ConnectionError(msg) from e
    except requests.exceptions.HTTPError as e:
        msg = f"Ollama returned HTTP error: {e}"
        raise ConnectionError(msg) from e

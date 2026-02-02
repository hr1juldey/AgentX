"""Voice gateway service configuration.

Manages service configuration and initialization.
"""

import logging

from agentx.core.config import get_settings
from agentx.infrastructure.external.voice_gateway_models import VoiceGatewayConfig

logger = logging.getLogger(__name__)
settings = get_settings()


class VoiceGatewayError(Exception):
    """Voice gateway error."""


def create_config(
    config: "VoiceGatewayConfig | None" = None,
) -> VoiceGatewayConfig:
    """Create voice gateway configuration.

    Args:
        config: Optional existing configuration

    Returns:
        VoiceGatewayConfig: The configuration to use
    """
    return config or VoiceGatewayConfig(
        use_voice_sdk=settings.voice.use_voice_sdk,
        max_concurrent_sessions=5,  # Default value
    )

"""Voice gateway service components.

Provides session management, task orchestration, agent callbacks, and configuration.
"""

from agentx.infrastructure.external.voice_gateway.agent_callback import (
    process_agent_callback,
    process_agent_response_with_tts,
)
from agentx.infrastructure.external.voice_gateway.config import (
    VoiceGatewayError,
    create_config,
)
from agentx.infrastructure.external.voice_gateway.session_manager import (
    check_server_health,
    cleanup_voice_session,
    create_session_connections,
)
from agentx.infrastructure.external.voice_gateway.task_orchestrator import (
    run_input_task,
    run_output_task,
)

__all__ = [
    "VoiceGatewayError",
    "create_config",
    "check_server_health",
    "cleanup_voice_session",
    "create_session_connections",
    "process_agent_callback",
    "process_agent_response_with_tts",
    "run_input_task",
    "run_output_task",
]

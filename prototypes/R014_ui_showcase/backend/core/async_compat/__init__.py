# =============================================================================
# AGENTX Async Compatibility Layer
# =============================================================================
# Graceful degradation: Async by default, sync fallback
# =============================================================================

from core.async_compat.decorators import auto_async
from core.async_compat.executor import SafeAsyncExecutor
from core.async_compat.hardware_detection import (
    HardwareTier,
    detect_hardware_tier,
    should_use_async,
)

__all__ = [
    "auto_async",
    "SafeAsyncExecutor",
    "HardwareTier",
    "detect_hardware_tier",
    "should_use_async",
]

# =============================================================================
# AGENTX Hardware Detection for Adaptive Async
# =============================================================================
# Detects GPU capabilities to determine optimal execution strategy
# =============================================================================

import logging

import torch

from config.settings import settings

logger = logging.getLogger(__name__)


class HardwareTier:
    """Hardware capability tiers for adaptive behavior."""

    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"


def detect_hardware_tier() -> str:
    """Detect hardware tier for adaptive behavior.

    Returns:
        Hardware tier string
    """
    if not torch.cuda.is_available():
        return HardwareTier.BASIC

    gpu_count = torch.cuda.device_count()
    vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)

    if gpu_count >= 8 and vram_gb >= 80:
        return HardwareTier.ENTERPRISE
    if gpu_count >= 4 and vram_gb >= 40:
        return HardwareTier.ADVANCED
    if vram_gb >= 40:
        return HardwareTier.STANDARD
    return HardwareTier.BASIC


def should_use_async(module_name: str) -> bool:
    """Determine if async should be used for a module.

    Args:
        module_name: Name of the module being checked

    Returns:
        True if async should be used
    """
    if settings.force_sync:
        return False
    if settings.force_async:
        return True

    tier = detect_hardware_tier()

    tier_rules = {
        HardwareTier.BASIC: {
            "MultiHopSearchAgent": True,
            "ResearcherAgent": False,
            "default": False,
        },
        HardwareTier.STANDARD: {
            "MultiHopSearchAgent": True,
            "ResearcherAgent": True,
            "AnalystAgent": True,
            "default": True,
        },
        HardwareTier.ADVANCED: {"default": True},
        HardwareTier.ENTERPRISE: {"default": True},
    }

    rules = tier_rules.get(tier, tier_rules[HardwareTier.BASIC])
    return rules.get(module_name, rules.get("default", False))

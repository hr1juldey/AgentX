# Function Postmortem: core/async_compat/hardware_detection.py

## Metadata
- **File**: prototypes/R014_ui_showcase/backend/core/async_compat/hardware_detection.py
- **Lines of Code**: 80
- **Purpose**: Hardware detection for adaptive async execution
- **Dependencies**: torch, config.settings

---

## Analysis

**Status**: Working hardware detection and tier-based execution rules

**Purpose**: Detects GPU capabilities to determine optimal execution strategy (async vs sync) based on hardware tier.

**Architecture**: Hardware tier classification + module-specific rules

---

## Functions/Classes Extracted

### HardwareTier (class)

**Purpose**: Hardware capability tiers for adaptive behavior

**Lines**: 16-22

```python
class HardwareTier:
    """Hardware capability tiers for adaptive behavior."""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"
```

**Tiers**:
- **BASIC**: No GPU or low-end
- **STANDARD**: Single GPU with 40GB+ VRAM
- **ADVANCED**: 4+ GPUs with 40GB+ VRAM each
- **ENTERPRISE**: 8+ GPUs with 80GB+ VRAM each

---

### detect_hardware_tier (function)

**Purpose**: Detect hardware tier for adaptive behavior

**Signature**: `def detect_hardware_tier() -> str`

**Lines**: 25-43

**Key Code**:
```python
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
```

**What Works**:
- Simple tier detection
- Uses PyTorch for GPU detection
- VRAM calculation in GB
- Realistic thresholds

**Mistakes Found**:
- Only checks first GPU's VRAM
- Ignores multi-GPU total VRAM

**Behavioral Notes**:
- No GPU → BASIC
- Single 40GB+ GPU → STANDARD
- 4x 40GB+ GPUs → ADVANCED
- 8x 80GB+ GPUs → ENTERPRISE

**Dependencies**:
- torch
- HardwareTier

**Reusability**: HIGH - Good tier classification

---

### should_use_async (function)

**Purpose**: Determine if async should be used for a module

**Signature**: `def should_use_async(module_name: str) -> bool`

**Lines**: 46-79

**Key Code**:
```python
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
```

**What Works**:
- Settings override (force_sync/force_async)
- Module-specific rules per tier
- Fallback to default
- Good tier-based strategy

**Mistakes Found**:
- Rules are hardcoded
- No dynamic adjustment based on load

**Behavioral Notes**:
- Settings override all detection
- BASIC tier: Most modules sync
- STANDARD tier: Most modules async
- ADVANCED/ENTERPRISE: All async

**Dependencies**:
- torch
- config.settings
- HardwareTier
- detect_hardware_tier

**Reusability**: HIGH - Good adaptive strategy

---

## File Summary

**Assessment**: Excellent hardware detection with tier-based execution rules. Good balance of performance and compatibility.

**Key Learnings**:
1. Hardware tiers enable adaptive behavior
2. Module-specific rules fine-tune performance
3. Settings override allow manual control
4. Conservative defaults prevent overload

**Mistakes to Avoid**:
1. Don't hardcode rules - make configurable
2. Don't ignore multi-GPU total VRAM

**Recommendations**:
1. Make rules configurable via settings
2. Consider total VRAM across GPUs
3. Add dynamic adjustment based on system load
4. Add runtime tier re-detection

**Reusability Score**: HIGH - Excellent hardware detection pattern

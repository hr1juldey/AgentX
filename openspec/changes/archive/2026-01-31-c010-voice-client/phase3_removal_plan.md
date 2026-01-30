# Phase 3 Removal Plan: Internal Voice Services

**Created**: 2026-01-31
**Change**: C010-voice-client
**Purpose**: Document the removal of deprecated internal voice services

---

## Overview

This plan describes the removal of internal voice services (VADService, STTService, TTSService) in favor of external kyutai voice-server integration via VoiceGatewayService.

---

## Phase 1: Coexistence (COMPLETE)

**Status**: ✅ Complete

**Goal**: External kyutai integration available alongside internal services.

**Implementation**:
- Feature flag `USE_KYUTAI_EXTERNAL=True` enables external integration
- Internal services remain importable with deprecation warnings
- Both services can coexist without conflict

**Verification**:
```bash
python -c "
from agentx.infrastructure.external.voice_services import VADService, STTService, TTSService
from agentx.infrastructure.external.voice_gateway_service import VoiceGatewayService
print('Coexistence verified')
"
```

---

## Phase 2: Default to External (COMPLETE)

**Status**: ✅ Complete

**Goal**: External integration is the default behavior.

**Implementation**:
- Feature flag `USE_KYUTAI_EXTERNAL=True` is the default
- All new code uses VoiceGatewayService
- Internal services show deprecation warnings

**Verification**:
```bash
python -c "
from agentx.core.config import get_settings
assert get_settings().voice.use_kyutai_external == True
print('External integration is default')
"
```

---

## Phase 3: Removal of Internal Services (PLANNED)

**Status**: Planned (Future)

**Goal**: Remove deprecated internal voice services entirely.

**Prerequisites**:
1. All consuming code migrated to VoiceGatewayService
2. No imports of VADService, STTService, TTSService remain
3. Documentation fully updated
4. Migration period of at least 3 months

---

## Removal Checklist

### Step 1: Audit Usage

**Command**: Find all imports of deprecated services

```bash
# Find all imports of VADService
grep -r "from.*voice_services import.*VADService" agentx/ --include="*.py"
grep -r "VADService" agentx/ --include="*.py" | grep -v "deprecated"

# Find all imports of STTService
grep -r "from.*voice_services import.*STTService" agentx/ --include="*.py"
grep -r "STTService" agentx/ --include="*.py" | grep -v "deprecated"

# Find all imports of TTSService
grep -r "from.*voice_services import.*TTSService" agentx/ --include="*.py"
grep -r "TTSService" agentx/ --include="*.py" | grep -v "deprecated"
```

**Expected Result**: No usage found (except in voice_services.py itself)

### Step 2: Update Dependencies

**Files to Update**:
- Remove `silero`, `silero_vad`, `torch`, `torchaudio` from requirements if no longer needed
- Update `pyproject.toml` dependencies

**Commands**:
```bash
# Check if Silero is still used elsewhere
grep -r "from silero" agentx/ --include="*.py"
grep -r "from silero_vad" agentx/ --include="*.py"
grep -r "torch.hub.load" agentx/ --include="*.py"
```

### Step 3: Delete Files

**Files to Remove**:
```
agentx/infrastructure/external/voice_services.py
```

**Commands**:
```bash
rm agentx/infrastructure/external/voice_services.py
```

### Step 4: Update Documentation

**Files to Update**:
- `CLAUDE.md` - Remove internal voice service references
- `README.md` - Ensure only external integration is documented
- `docs/research/08_tts_stt_integration.md` - Mark legacy sections as removed
- `openspec/changes/c004-voice-streaming/` - Mark as fully deprecated

### Step 5: Remove Feature Flag

**Purpose**: Remove `USE_KYUTAI_EXTERNAL` feature flag once external is the only option.

**File**: `agentx/core/config.py`

**Before**:
```python
use_kyutai_external: bool = True
```

**After**: Remove the setting entirely (external is always used)

---

## Rollback Plan

If removal causes issues:

1. **Restore voice_services.py** from git:
   ```bash
   git checkout HEAD~1 agentx/infrastructure/external/voice_services.py
   ```

2. **Re-add dependencies**:
   ```bash
   uv pip install silero torch torchaudio
   ```

3. **Investigate failure**: Check logs and error messages to identify what still uses internal services

---

## Migration Timeline

| Phase | Status | Date | Notes |
|-------|--------|------|-------|
| Phase 1: Coexistence | ✅ Complete | 2026-01-31 | Both internal and external available |
| Phase 2: Default External | ✅ Complete | 2026-01-31 | External is default, internal deprecated |
| Phase 3: Removal | Planned | TBD | At least 3 months after Phase 2 |

**Recommended Removal Date**: 2026-05-01 (3 months after deprecation)

---

## Post-Removal Verification

After removal, verify:

```bash
# No imports of deprecated services
grep -r "VADService\|STTService\|TTSService" agentx/ --include="*.py"

# Only VoiceGatewayService is used
grep -r "VoiceGatewayService" agentx/ --include="*.py" | head -5

# All tests pass
pytest tests/integration/infrastructure/external/test_voice_*.py -v

# No feature flag references
grep -r "USE_KYUTAI_EXTERNAL" agentx/ --include="*.py"
```

---

**End of Phase 3 Removal Plan**

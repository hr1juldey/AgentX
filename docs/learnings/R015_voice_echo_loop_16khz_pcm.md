# R015: Voice Echo Loop - 16kHz PCM Streaming

**Date**: 2026-02-06
**Status**: Complete
**Related**: C010 Voice Client, C008 Organic UI

## Overview

Implementation of direct 16kHz PCM audio streaming from frontend to Kyutai voice server for optimal Whisper STT performance.

## Problem Statement

Initial implementation had two issues:
1. Frontend sent 24kHz audio → backend had to resample to 16kHz (Whisper requirement)
2. Sample rate mismatch caused poor transcription accuracy

## Solution

### Frontend Changes

**New AudioProcessor Class** (`frontend/src/lib/audio/AudioProcessor.ts`)
- Captures microphone audio at 48kHz (high quality input)
- Resamples to **16kHz** using linear interpolation
- Converts to **16-bit PCM** format
- Streams in **200ms chunks** for variable recording lengths

**Updated Voice Components**
- `voice-button.tsx` - AgentX backend integration
- `voice-button-kyutai-direct.tsx` - Direct Kyutai echo loop

### Backend Changes

**Critical Fix in** `whisper.py`:
```python
# Before: Hardcoded 24kHz (wrong!)
input_sample_rate: int = 24000

# After: Matches frontend 16kHz PCM
input_sample_rate: int = 16000
```

### Key Insight

The root issue was NOT the resampling function - it was the hardcoded `input_sample_rate` that didn't match what the frontend was sending.

**What was happening**:
1. Frontend sends 16kHz audio
2. Backend `SessionState.input_sample_rate = 24000` (hardcoded)
3. Backend checks: `24000 != 16000` → calls `resample(audio, 24000, 16000)`
4. Resampling treats 16kHz audio as if it were 24kHz
5. Result: Audio plays at 0.67x speed → broken transcription

**The fix**: Simply update `input_sample_rate` to match reality.

## Technical Details

### Audio Format

| Property | Value |
|----------|-------|
| Sample Rate | **16000 Hz** (Whisper native) |
| Channels | 1 (Mono) |
| Format | PCM Int16 |
| Chunk Size | 200ms (~3200 samples/chunk) |
| Encoding | Base64 |

### Message Flow

```
Frontend (16kHz PCM) → WebSocket → Kyutai STT (16kHz native) → Transcription
```

No backend resampling needed!

## Whisper Model Upgrade

Also upgraded from `base` (74M params) to `medium` (769M params):
- Better accuracy on complex vocabulary
- ~1.5GB VRAM with int8 quantization
- Fits within 1-2GB budget

## Lessons Learned

### 1. Sample Rate Must Match

**Rule**: Frontend and backend MUST agree on sample rate.

**Detection**: If transcription produces gibberish or single words, check sample rate mismatch first.

**Fix**: Ensure `SessionState.input_sample_rate` matches actual frontend sample rate.

### 2. Resampling is Expensive

- Best to stream at the target rate (16kHz) from the start
- Avoid backend resampling when possible
- Reduces latency and CPU usage

### 3. Hardcoded Defaults Are Dangerous

The `input_sample_rate = 24000` was a hidden assumption that broke when frontend changed.

**Better approaches**:
- Pass sample rate in Config message
- Detect from audio metadata
- Use constants shared between frontend/backend

### 4. Debugging Sample Rate Issues

**Symptoms**:
- Audio plays at wrong speed (0.67x or 1.5x)
- Only single words transcribed
- "VAD filtered out all audio"

**Checks**:
```bash
# Check frontend sample rate
# Look for: targetSampleRate: 16000

# Check backend sample rate
# Look for: SessionState.input_sample_rate

# Check if resampling is being called
# Look for: "Resampling audio from X Hz to Y Hz"
```

### 5. Whisper Model Sizing

| Model | Params | VRAM (int8) | Use Case |
|-------|--------|-------------|----------|
| tiny | 39M | ~80 MB | Testing only |
| base | 74M | ~150 MB | Fast, low accuracy |
| small | 244M | ~500 MB | Balanced |
| **medium** | **769M** | **~1.5 GB** | **Recommended** |
| large-v3 | 1.5B | ~3 GB | Best accuracy |

## Files Changed

### Frontend
- `frontend/src/lib/audio/AudioProcessor.ts` (NEW)
- `frontend/src/lib/voice/client.ts` (added `sendAudioChunk`, `sendEos`)
- `frontend/src/components/voice-button.tsx` (16kHz streaming)
- `frontend/src/components/voice-button-kyutai-direct.tsx` (16kHz streaming)

### Backend (Kyutai)
- `voice_server/config/settings.py` (model: base → medium)
- `voice_server/src/models/stt/whisper.py` (input_sample_rate: 24000 → 16000)

## Testing

**Test phrase**: "the demographic dividend of India must be utilised to get India out of poverty"

**Before** (24kHz → 16kHz resample):
- Output: "You"
- Language confidence: 20%

**After** (16kHz native):
- Output: Full phrase transcribed correctly
- Language confidence: >80%

## References

- [faster-whisper PyPI](https://pypi.org/project/faster-whisper/)
- C010 Voice Client implementation
- C008 Organic UI Design System

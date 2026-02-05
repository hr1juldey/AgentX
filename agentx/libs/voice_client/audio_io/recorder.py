"""Audio recorder for microphone input.

This module provides backward-compatible re-exports from the recording/ subdirectory.
The actual implementation has been split into focused modules:
- recorder.py: Main AudioRecorder class
- streaming.py: StreamRecorder with async streaming support
- silence.py: Silence detection and trimming utilities
"""

from agentx.libs.voice_client.audio_io.recording.recorder import AudioRecorder

__all__ = ["AudioRecorder"]

"""Audio recorder for microphone input."""

from collections.abc import AsyncIterator
from typing import Any

import numpy as np
import sounddevice as sd
from agentx.libs.voice_client.audio_io.devices import list_input_devices
from agentx.libs.voice_client.audio_io.recording.streaming import StreamRecorder
from agentx.libs.voice_client.constants import (
    DEFAULT_CHANNELS,
    DEFAULT_SAMPLE_RATE,
    SILENCE_THRESHOLD,
)


class AudioRecorder(StreamRecorder):
    """Record audio from microphone using sounddevice.

    Attributes:
        DEFAULT_SAMPLE_RATE: Default sample rate in Hz
        DEFAULT_CHANNELS: Default number of channels (mono)
        DEFAULT_DTYPE: Default numpy dtype for audio
    """

    DEFAULT_DTYPE = np.int16

    def __init__(
        self,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        channels: int = DEFAULT_CHANNELS,
        device: int | None = None,
    ) -> None:
        """Initialize the audio recorder.

        Args:
            sample_rate: Sample rate in Hz (default: 24000)
            channels: Number of audio channels (default: 1 for mono)
            device: Device index (None for system default)
        """
        super().__init__(sample_rate, channels, device)

    @classmethod
    def list_devices(cls) -> list[dict[str, Any]]:
        """List available audio input devices.

        Returns:
            List of device dictionaries with keys:
            - index: device index
            - name: device name
            - channels: maximum input channels
            - sample_rate: default sample rate
        """
        return list_input_devices()

    def record(
        self,
        duration_seconds: float,
        silence_threshold: float = SILENCE_THRESHOLD,
    ) -> tuple[np.ndarray, int]:
        """Record audio for a fixed duration.

        Args:
            duration_seconds: How long to record in seconds
            silence_threshold: RMS threshold for silence detection

        Returns:
            Tuple of (audio_array, sample_rate)
        """
        from agentx.libs.voice_client.audio_io.recording.silence import trim_silence

        frames = int(duration_seconds * self.sample_rate)
        recording = sd.rec(
            frames,
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=self.DEFAULT_DTYPE,
            device=self.device,
        )
        sd.wait()

        # Trim leading/trailing silence
        return trim_silence(recording, silence_threshold), self.sample_rate

    async def record_stream(
        self,
        chunk_size_ms: int = 50,
        silence_threshold: float = SILENCE_THRESHOLD,
        silence_duration_ms: float = 1500.0,
    ) -> AsyncIterator[bytes]:
        """Record audio in chunks, stop on silence.

        Delegates to StreamRecorder.record_stream().

        Args:
            chunk_size_ms: Audio chunk duration in milliseconds
            silence_threshold: RMS threshold for silence detection
            silence_duration_ms: Milliseconds of silence to trigger stop

        Yields:
            Audio chunks as bytes
        """
        async for chunk in super().record_stream(
            chunk_size_ms,
            silence_threshold,
            silence_duration_ms,
        ):
            yield chunk

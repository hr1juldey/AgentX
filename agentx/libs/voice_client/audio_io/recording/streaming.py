"""Streaming audio recording with silence detection."""

import asyncio
from collections.abc import AsyncIterator
from typing import Any

import numpy as np
import sounddevice as sd
from agentx.libs.voice_client.constants import (
    DEFAULT_CHUNK_MS,
    DEFAULT_SAMPLE_RATE,
    SILENCE_DURATION_MS,
    SILENCE_THRESHOLD,
)


class StreamRecorder:
    """Handles streaming audio recording with silence detection."""

    def __init__(
        self,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        channels: int = 1,
        device: int | None = None,
    ) -> None:
        """Initialize the stream recorder.

        Args:
            sample_rate: Sample rate in Hz
            channels: Number of audio channels
            device: Device index (None for system default)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.device = device
        self._stream: sd.InputStream | None = None

    async def record_stream(
        self,
        chunk_size_ms: int = DEFAULT_CHUNK_MS,
        silence_threshold: float = SILENCE_THRESHOLD,
        silence_duration_ms: float = SILENCE_DURATION_MS,
    ) -> AsyncIterator[bytes]:
        """Record audio in chunks, stop on silence.

        Args:
            chunk_size_ms: Audio chunk duration in milliseconds
            silence_threshold: RMS threshold for silence detection
            silence_duration_ms: Milliseconds of silence to trigger stop

        Yields:
            Audio chunks as bytes
        """
        chunk_size = (self.sample_rate * chunk_size_ms) // 1000
        silence_chunks = (self.sample_rate * silence_duration_ms) // 1000

        queue: asyncio.Queue[tuple[bytes, bool]] = asyncio.Queue()

        def audio_callback(
            indata: np.ndarray,
            frames: int,
            time: Any,
            status: Any,
        ) -> None:
            """Callback for each audio chunk.

            Args:
                indata: Input audio data
                frames: Number of frames
                time: Stream time
                status: Stream status
            """
            from agentx.libs.voice_client.audio_io.recording.silence import is_silent

            if status:
                print(f"Audio callback status: {status}")
                return

            is_silent_flag = is_silent(indata, silence_threshold)
            audio_bytes = indata.tobytes()

            # Put in queue with silence flag
            try:
                loop = asyncio.get_event_loop()
                asyncio.run_coroutine_threadsafe(
                    queue.put((audio_bytes, is_silent_flag)),
                    loop,
                )
            except RuntimeError:
                # Event loop closed
                pass

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=np.int16,
            blocksize=chunk_size,
            callback=audio_callback,
            device=self.device,
        )

        self._stream.start()

        silence_count = 0
        try:
            while True:
                try:
                    chunk, is_silent = await asyncio.wait_for(
                        queue.get(),
                        timeout=1.0,
                    )
                except asyncio.TimeoutError:
                    # Check if stream is still active
                    if self._stream and not self._stream.active:
                        break
                    continue

                if is_silent:
                    silence_count += chunk_size
                    if silence_count >= silence_chunks:
                        # Enough silence, stop recording
                        break
                else:
                    silence_count = 0

                yield chunk

        finally:
            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None

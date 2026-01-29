"""Voice streaming services for Real AgentX v0.1 (C004).

STT/TTS/VAD pipeline using Silero models.
Following voice integration patterns from CLAUDE.md.
"""

import io
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import scipy.io.wavfile as wavfile
import torch
from torch import nn


class VoiceConfig:
    """Voice service configuration."""

    STT_SAMPLE_RATE = 16000
    TTS_SAMPLE_RATE = 24000  # or 48000
    VAD_SAMPLE_RATE = 16000


class STTService:
    """Speech-to-Text service using Silero STT.

    Accepts any sample rate and resamples to 16kHz internally.
    """

    def __init__(self) -> None:
        """Initialize Silero STT model."""
        self._torch_device = self._get_device()
        self._load_model()

    def _get_device(self) -> torch.device:
        """Get the Torch device (CPU or CUDA).

        Returns:
            torch.device: The device to use.
        """
        use_cuda = torch.cuda.is_available()
        device_str = "cuda" if use_cuda else "cpu"
        return torch.device(device_str)

    def _load_model(self) -> None:
        """Load Silero STT model from torch.hub."""
        stt_result = torch.hub.load(
            repo_or_dir="snakers4/silero-models",
            model="silero_stt",
            language="en",
            device=self._torch_device,
            trust_repo=True,
        )

        self.stt_model = stt_result[0]  # type: ignore[index]
        self.stt_decoder = stt_result[1]  # type: ignore[index]
        utils_tuple = stt_result[2]  # type: ignore[index]
        self._stt_read_batch = utils_tuple[0]  # type: ignore[index]
        self._stt_prepare_model_input = utils_tuple[3]  # type: ignore[index]

    async def transcribe(self, audio_bytes: bytes) -> str:
        """Transcribe audio to text.

        Args:
            audio_bytes: Raw audio bytes (any sample rate).

        Returns:
            str: Transcribed text.
        """
        # Save to temp file
        temp_path = f"/tmp/temp_stt_{uuid.uuid4().hex}.wav"
        with open(temp_path, "wb") as f:
            f.write(audio_bytes)

        try:
            # Read and validate
            sr, audio_data = wavfile.read(temp_path)

            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)

            # Resample if not 16kHz
            if sr != VoiceConfig.STT_SAMPLE_RATE:
                from torchaudio.transforms import Resample

                audio_tensor = torch.from_numpy(
                    audio_data.astype(np.float32) / 32768.0
                )
                if audio_tensor.dim() == 1:
                    audio_tensor = audio_tensor.unsqueeze(0)

                resampler = Resample(sr, VoiceConfig.STT_SAMPLE_RATE)
                audio_tensor = resampler(audio_tensor)
                audio_data = audio_tensor.squeeze().numpy()
                sr = VoiceConfig.STT_SAMPLE_RATE

            # Prepare and transcribe
            input_batch = self._stt_prepare_model_input(
                self._stt_read_batch([temp_path]), device=self._torch_device
            )

            with torch.no_grad():
                output = self.stt_model(input_batch)

            text = self.stt_decoder(output[0].cpu())
            return text

        finally:
            # Clean up temp file
            Path(temp_path).unlink(missing_ok=True)


class TTSService:
    """Text-to-Speech service using Silero TTS.

    Generates audio at 24kHz or 48kHz.
    """

    def __init__(self) -> None:
        """Initialize Silero TTS model."""
        self._torch_device = self._get_device()
        self._load_model()

    def _get_device(self) -> torch.device:
        """Get the Torch device (CPU or CUDA).

        Returns:
            torch.device: The device to use.
        """
        use_cuda = torch.cuda.is_available()
        device_str = "cuda" if use_cuda else "cpu"
        return torch.device(device_str)

    def _load_model(self) -> None:
        """Load Silero TTS model."""
        from silero import silero_tts

        tts_result = silero_tts(language="en", speaker="v3_en")
        if isinstance(tts_result, tuple) and len(tts_result) >= 2:
            self.tts_model = tts_result[0]
            self.tts_example_text = tts_result[1]
        else:
            self.tts_model = tts_result
            self.tts_example_text = "Hello world"

        if hasattr(self.tts_model, "to"):
            self.tts_model.to(self._torch_device)

    async def synthesize(self, text: str) -> bytes:
        """Synthesize speech from text.

        Args:
            text: Text to synthesize.

        Returns:
            bytes: WAV audio bytes.
        """
        # Generate audio at exact sample rate
        audio = self.tts_model.apply_tts(
            text=text, speaker="en_5", sample_rate=VoiceConfig.TTS_SAMPLE_RATE
        )

        # Save to WAV
        audio_buffer = io.BytesIO()
        wavfile.write(
            audio_buffer, VoiceConfig.TTS_SAMPLE_RATE, audio.cpu().numpy()
        )
        audio_buffer.seek(0)
        return audio_buffer.read()


class VADService:
    """Voice Activity Detection service using Silero VAD.

    Detects speech activity in audio chunks.
    """

    def __init__(self) -> None:
        """Initialize Silero VAD model."""
        self._torch_device = self._get_device()
        self._load_model()

    def _get_device(self) -> torch.device:
        """Get the Torch device (CPU or CUDA).

        Returns:
            torch.device: The device to use.
        """
        use_cuda = torch.cuda.is_available()
        device_str = "cuda" if use_cuda else "cpu"
        return torch.device(device_str)

    def _load_model(self) -> None:
        """Load Silero VAD model."""
        from silero_vad import load_silero_vad

        self.vad_model = load_silero_vad()
        if hasattr(self.vad_model, "to"):
            self.vad_model.to(self._torch_device)

    def detect_speech(self, audio_np: np.ndarray) -> float:
        """Detect speech probability in audio.

        Args:
            audio_np: Audio data as numpy array.

        Returns:
            float: Speech probability (0-1).
        """
        # Always include sr parameter (per CLAUDE_POLICY.md)
        speech_prob = self.vad_model(
            torch.from_numpy(audio_np).float().to(self._torch_device),
            sr=VoiceConfig.VAD_SAMPLE_RATE,
        ).item()
        return speech_prob

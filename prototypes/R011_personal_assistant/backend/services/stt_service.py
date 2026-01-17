"""Speech-to-Text service using Silero STT."""

import logging
import uuid
from pathlib import Path

import numpy as np
import torch

logger = logging.getLogger(__name__)


# Lazy import torchaudio.transforms for conditional use
def _get_resampler(orig_freq: int, new_freq: int, dtype: torch.dtype):
    """Get resampler from torchaudio.transforms."""
    from torchaudio.transforms import Resample

    return Resample(orig_freq, new_freq, dtype=dtype)


class STTService:
    """Speech-to-Text service using Silero STT with GPU/CPU support."""

    def __init__(self):
        """Initialize STT service with GPU/CPU detection."""
        use_cuda = torch.cuda.is_available()
        device_str = "cuda" if use_cuda else "cpu"
        self._torch_device = torch.device(device_str)  # type: ignore[read-only]
        if use_cuda:
            logger.info(f"STT using GPU: {torch.cuda.get_device_name()}")
        else:
            logger.info("STT using CPU")
            torch.set_num_threads(1)

        self._initialize_model()

    def _initialize_model(self):
        """Initialize Silero STT model."""
        try:
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

            logger.info("Silero STT model loaded")

        except Exception as e:
            logger.error(f"Failed to initialize STT model: {e}")
            raise

    STT_SAMPLE_RATE = 16000

    async def transcribe(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio bytes to text using Silero STT.

        Args:
            audio_bytes: Raw audio bytes (WAV format, any sample rate)

        Returns:
            Transcribed text string
        """
        temp_path = f"/tmp/temp_stt_{uuid.uuid4().hex}.wav"

        try:
            # Save to temp file
            with open(temp_path, "wb") as f:
                f.write(audio_bytes)

            # Resample if needed
            import scipy.io.wavfile as wavfile

            sr, audio_data = wavfile.read(temp_path)

            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)

            # Resample if not 16kHz
            if sr != self.STT_SAMPLE_RATE:
                if audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
                    audio_tensor = torch.from_numpy(audio_data).float()
                else:
                    audio_tensor = torch.from_numpy(audio_data).float() / 32768.0

                if audio_tensor.dim() == 1:
                    audio_tensor = audio_tensor.unsqueeze(0)

                resampler = _get_resampler(
                    sr, self.STT_SAMPLE_RATE, dtype=audio_tensor.dtype
                )
                audio_tensor = resampler(audio_tensor)
                audio_data = audio_tensor.squeeze().numpy()
                sr = self.STT_SAMPLE_RATE

            # Convert to int16 for Silero
            if audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
                audio_data = np.clip(audio_data, -1.0, 1.0)
                audio_data = (audio_data * 32768).astype(np.int16)
            elif audio_data.dtype != np.int16:
                audio_data = audio_data.astype(np.int16)

            with open(temp_path, "wb") as f:
                wavfile.write(f, sr, audio_data)

            # Validate audio format
            validate_sr, validate_audio = wavfile.read(temp_path)
            assert validate_sr == 16000, f"Invalid sample rate: {validate_sr}"
            assert validate_audio.dtype == np.int16, (
                f"Invalid dtype: {validate_audio.dtype}"
            )
            assert validate_audio.ndim == 1, "Audio must be mono"

            # Prepare audio for STT
            input_batch = self._stt_prepare_model_input(
                self._stt_read_batch([temp_path]), device=self._torch_device
            )

            # Perform transcription
            with torch.no_grad():
                output = self.stt_model(input_batch)

            text = self.stt_decoder(output[0].cpu())

            logger.info(f"STT transcription: {text}")

            return text

        except Exception as e:
            logger.error(f"STT error: {e}")
            return ""

        finally:
            Path(temp_path).unlink(missing_ok=True)


# Global instance
stt_service = STTService()

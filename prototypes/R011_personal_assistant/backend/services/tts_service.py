"""Text-to-Speech service using Silero TTS."""

import io
import logging

import torch
from silero import silero_tts

logger = logging.getLogger(__name__)


class TTSService:
    """Text-to-Speech service using Silero TTS with GPU/CPU support."""

    def __init__(self):
        """Initialize TTS service with GPU/CPU detection."""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if self.device.type == "cuda":
            logger.info(f"TTS using GPU: {torch.cuda.get_device_name()}")
        else:
            logger.info("TTS using CPU")
            torch.set_num_threads(1)

        self._initialize_model()

    def _initialize_model(self):
        """Initialize Silero TTS model."""
        try:
            self.tts_model, self.tts_example_text = silero_tts(language="en", speaker="v3_en")
            self.tts_model.to(self.device)
            logger.info("Silero TTS model loaded (speaker: v3_en)")

        except Exception as e:
            logger.error(f"Failed to initialize TTS model: {e}")
            raise

    TTS_SAMPLE_RATE = 24000

    async def synthesize(self, text: str) -> bytes:
        """
        Convert text to speech audio using Silero TTS.

        Args:
            text: Text to synthesize

        Returns:
            WAV audio bytes
        """
        target_rate = self.TTS_SAMPLE_RATE

        try:
            # Generate audio
            audio = self.tts_model.apply_tts(text=text, speaker="en_0", sample_rate=target_rate)

            # Validate audio
            if not hasattr(audio, "shape"):
                raise ValueError(f"Generated audio is not a tensor, got {type(audio)}")

            expected_samples_per_char = target_rate * 0.1
            min_expected = len(text) * expected_samples_per_char * 0.5
            max_expected = len(text) * expected_samples_per_char * 2.0

            if len(audio) < min_expected or len(audio) > max_expected:
                raise ValueError(
                    f"Audio duration anomaly: {len(audio)} samples for {len(text)} chars"
                )

            # Save to WAV
            import scipy.io.wavfile as wavfile

            audio_buffer = io.BytesIO()
            wavfile.write(audio_buffer, target_rate, audio.cpu().numpy())
            audio_buffer.seek(0)

            audio_bytes = audio_buffer.read()
            if len(audio_bytes) < 100:
                raise ValueError("Generated WAV file is too small")

            logger.info(f"TTS synthesis: {text[:50]}... (rate={target_rate}Hz)")

            return audio_bytes

        except Exception as e:
            logger.error(f"TTS error: {e}")
            raise


# Global instance
tts_service = TTSService()

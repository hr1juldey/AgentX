"""Meeting notes service with Silero STT/TTS and WebSocket streaming."""

import io
import logging
import uuid
from collections import deque
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import torch
from silero import silero_tts
from silero_vad import VADIterator, load_silero_vad

from config.settings import settings

logger = logging.getLogger(__name__)


class MeetingNotesService:
    """Service for meeting notes with Silero STT/TTS and real-time streaming."""

    def __init__(self):
        """Initialize the service with GPU/CPU detection."""
        # Device detection: GPU first, CPU fallback
        use_cuda = torch.cuda.is_available()
        device_str = "cuda" if use_cuda else "cpu"
        self._torch_device = torch.device(device_str)  # type: ignore[read-only]
        if use_cuda:
            logger.info(f"Using GPU: {torch.cuda.get_device_name()}")
        else:
            logger.info("Using CPU")
            torch.set_num_threads(1)  # Optimize for CPU

        # Audio buffer for streaming
        self.audio_buffer = deque(maxlen=16000 * 5)  # 5 seconds buffer

        # Initialize Silero models
        self._initialize_models()

    def _initialize_models(self):
        """Initialize Silero models with GPU/CPU support."""
        try:
            # STT Model (Speech-to-Text) via torch.hub
            # Note: First run downloads ~130MB from GitHub (cached locally after)
            # Returns: (model, decoder, (read_batch, split_into_batches, read_audio, prepare_model_input))
            stt_result = torch.hub.load(
                repo_or_dir="snakers4/silero-models",
                model="silero_stt",
                language="en",
                device=self._torch_device,
                trust_repo=True,  # Suppress download prompt
            )

            self.stt_model = stt_result[0]  # type: ignore[index]
            self.stt_decoder = stt_result[1]  # type: ignore[index]

            # Store utils functions directly
            utils_tuple = stt_result[2]  # type: ignore[index]
            self._stt_read_batch = utils_tuple[0]
            self._stt_prepare_model_input = utils_tuple[3]

            logger.info("STT model loaded")

            # TTS Model (Text-to-Speech) using silero package
            # Available speakers for English: v3_en, lj_v2, lj_8khz, lj_16khz, v3_en_indic
            tts_result = silero_tts(language="en", speaker=settings.tts_speaker)
            # Handle variable-length return from silero_tts
            if isinstance(tts_result, tuple) and len(tts_result) >= 2:
                self.tts_model = tts_result[0]
                self.tts_example_text = tts_result[1]
            else:
                self.tts_model = tts_result
                self.tts_example_text = "Hello world"  # Default example text
            # Ensure the model is on the correct device
            if hasattr(self.tts_model, "to"):
                self.tts_model.to(self._torch_device)
            self.tts_speaker = settings.tts_speaker
            logger.info(f"TTS model loaded (speaker: {self.tts_speaker})")

            # VAD Model (Voice Activity Detection) with iterator
            self.vad_model = load_silero_vad()
            self.vad_iterator = VADIterator(
                self.vad_model,
                sampling_rate=16000,
                threshold=0.5,
                min_silence_duration_ms=500,
                speech_pad_ms=30,
            )
            logger.info("VAD model loaded")

        except Exception as e:
            logger.error(f"Failed to initialize Silero models: {e}")
            raise

    async def transcribe_audio(self, audio_data: bytes) -> Tuple[str, bool]:
        """Transcribe audio and detect speech activity."""
        try:
            # Decode bytes to numpy array (assuming 16-bit PCM, 16kHz mono)
            audio_np = (
                np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            )

            # Check for speech using VAD
            # VAD model requires sample rate parameter (16000 for speech)
            speech_prob = self.vad_model(
                torch.tensor(audio_np).float().to(self._torch_device), sr=16000
            ).item()
            has_speech = speech_prob > 0.5

            if not has_speech or len(audio_np) < 1600:  # Need at least 0.1 seconds
                return "", False

            # Save to temp file for STT
            temp_path = f"/tmp/temp_audio_{uuid.uuid4().hex}.wav"
            import scipy.io.wavfile as wavfile

            wavfile.write(temp_path, 16000, (audio_np * 32768).astype(np.int16))

            # GUARDRAIL: Validate audio format before STT
            try:
                validate_sr, validate_audio = wavfile.read(temp_path)
                logger.info(
                    f"STT input WAV: sr={validate_sr}, dtype={validate_audio.dtype}, "
                    f"shape={validate_audio.shape}, min={validate_audio.min()}, max={validate_audio.max()}"
                )

                # FAIL FAST: Assert Silero requirements
                assert validate_sr == 16000, (
                    f"Invalid sample rate: {validate_sr}, expected 16000"
                )
                assert validate_audio.dtype == np.int16, (
                    f"Invalid dtype: {validate_audio.dtype}, expected int16"
                )
                assert validate_audio.ndim == 1, (
                    f"Audio must be mono, got shape {validate_audio.shape}"
                )

                logger.info("STT audio validation passed")
            except AssertionError as e:
                logger.error(f"STT audio validation failed: {e}")
                return "", False

            # Prepare audio for STT
            input_batch = self._stt_prepare_model_input(
                self._stt_read_batch([temp_path]), device=self._torch_device
            )

            # Perform transcription
            with torch.no_grad():
                output = self.stt_model(input_batch)

            # Decode output
            text = self.stt_decoder(output[0].cpu())

            # Clean up temp file
            Path(temp_path).unlink(missing_ok=True)

            logger.info(f"Transcription: {text[:50]}...")

            return text, True

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return "", False

    # TTS Sample Rate Configuration (SINGLE SOURCE OF TRUTH)
    TTS_SAMPLE_RATE = 24000  # 24kHz - high quality, standard for TTS

    async def synthesize_speech(self, text: str) -> bytes:
        """
        Convert text to speech using Silero TTS with strict sample-rate contract.

        GUARANTEES:
        - Silero generates at exactly TTS_SAMPLE_RATE (24kHz)
        - WAV file is encoded at exactly TTS_SAMPLE_RATE
        - Playback will respect the WAV header
        """
        target_rate = self.TTS_SAMPLE_RATE

        try:
            # Generate audio at EXACT target sample rate
            try:
                # v3_en API
                audio = self.tts_model.apply_tts(
                    text=text, speaker="en_0", sample_rate=target_rate
                )
            except TypeError:
                # lj_v2 API: texts (plural)
                audio_list = self.tts_model.apply_tts(
                    texts=text, sample_rate=target_rate
                )
                audio = audio_list[0]

            # Validate audio
            if not hasattr(audio, "shape"):
                raise ValueError(f"Generated audio is not a tensor, got {type(audio)}")

            # Save to WAV at EXACT same sample rate
            import scipy.io.wavfile as wavfile

            audio_buffer = io.BytesIO()
            wavfile.write(audio_buffer, target_rate, audio.cpu().numpy())
            audio_buffer.seek(0)

            logger.info(
                f"TTS synthesis successful: {text[:50]}... (rate={target_rate}Hz)"
            )

            return audio_buffer.read()

        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            raise

    def process_audio_chunk(self, audio_chunk: np.ndarray) -> Optional[dict]:
        """Process audio chunk for streaming (WebSocket)."""
        try:
            # Convert to tensor if needed
            audio_tensor: torch.Tensor
            if isinstance(audio_chunk, np.ndarray):
                audio_tensor = torch.tensor(audio_chunk).float()
            else:
                audio_tensor = audio_chunk  # type: ignore[assignment]

            # Use VAD iterator to detect speech boundaries
            speech_dict = self.vad_iterator(
                audio_tensor.to(self._torch_device), return_seconds=True
            )

            return speech_dict

        except Exception as e:
            logger.error(f"Audio chunk processing error: {e}")
            return None

    def reset_vad_iterator(self):
        """Reset the VAD iterator state (for new meetings)."""
        self.vad_iterator.reset_states()
        logger.info("VAD iterator reset")

    async def check_health(self) -> dict:
        """Check service health and model status."""
        return {
            "stt_available": True,
            "tts_available": True,
            "vad_available": True,
            "device": self._torch_device.type,
            "models_loaded": all(
                [
                    hasattr(self, "stt_model"),
                    hasattr(self, "tts_model"),
                    hasattr(self, "vad_model"),
                ]
            ),
        }


# Global service instance
meeting_notes_service = MeetingNotesService()

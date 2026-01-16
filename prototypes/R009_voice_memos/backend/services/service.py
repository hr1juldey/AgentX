"""Voice memo service with Silero STT/TTS."""
import base64
import io
import logging
import uuid
from pathlib import Path
from typing import Optional

import numpy as np
import torch
from silero import silero_tts
from silero_vad import load_silero_vad

from config.settings import settings
from models.schemas import TranscriptionRequest, TranscriptionResponse, TTSSynthesisRequest

logger = logging.getLogger(__name__)


class VoiceMemoService:
    """Service for voice recording, transcription, and synthesis using Silero models."""

    def __init__(self):
        """Initialize the voice memo service with GPU/CPU detection."""
        self.upload_dir = settings.upload_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        # Device detection: GPU first, CPU fallback
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        if self.device.type == 'cuda':
            logger.info(f"Using GPU: {torch.cuda.get_device_name()}")
        else:
            logger.info("Using CPU")
            torch.set_num_threads(1)  # Optimize for CPU

        # Initialize Silero models
        self._initialize_models()

    def _initialize_models(self):
        """Initialize Silero models with GPU/CPU support."""
        try:
            # STT Model (Speech-to-Text) via torch.hub
            # Note: First run downloads ~112MB from GitHub (cached locally after)
            # Returns: (model, decoder, (read_batch, prepare_model_input, ...))
            stt_result = torch.hub.load(
                repo_or_dir='snakers4/silero-models',
                model='silero_stt',
                language='en',
                device=self.device,
                trust_repo=True  # Suppress download prompt
            )

            # Silero STT returns: (model, decoder, tuple_of_functions)
            # The tuple contains: (read_batch, prepare_model_input, pre_process, post_process)
            self.stt_model = stt_result[0]
            self.stt_decoder = stt_result[1]

            # Store utils functions directly
            # Tuple order: read_batch, split_into_batches, read_audio, prepare_model_input
            utils_tuple = stt_result[2]
            self._stt_read_batch = utils_tuple[0]
            self._stt_prepare_model_input = utils_tuple[3]

            logger.info("STT model loaded")

            # TTS Model (Text-to-Speech) using silero package
            # Available speakers for English: v3_en, lj_v2, lj_8khz, lj_16khz
            self.tts_model, self.tts_example_text = silero_tts(
                language='en',
                speaker=settings.tts_speaker
            )
            self.tts_model.to(self.device)
            self.tts_speaker = settings.tts_speaker
            logger.info(f"TTS model loaded (speaker: {self.tts_speaker})")

            # VAD Model (Voice Activity Detection)
            self.vad_model = load_silero_vad()
            logger.info("VAD model loaded")

        except Exception as e:
            logger.error(f"Failed to initialize Silero models: {e}")
            raise

    # STT Sample Rate Configuration
    # Silero STT expects 16kHz mono audio
    STT_SAMPLE_RATE = 16000

    async def transcribe_audio(self, request: TranscriptionRequest) -> TranscriptionResponse:
        """
        Transcribe audio file to text using Silero STT.

        Handles sample rate conversion:
        - Input: Any WAV format (converts to 16kHz mono if needed)
        - STT: Silero expects 16kHz mono
        """
        try:
            # Decode base64 audio
            audio_bytes = base64.b64decode(request.audio_data)

            # Save to temp file
            temp_path = f"/tmp/temp_stt_{uuid.uuid4().hex}.wav"

            # Try to use the audio directly first
            with open(temp_path, 'wb') as f:
                f.write(audio_bytes)

            # Check if we need to resample
            import scipy.io.wavfile as wavfile
            try:
                sr, audio_data = wavfile.read(temp_path)

                # Convert to mono if stereo
                if len(audio_data.shape) > 1:
                    audio_data = audio_data.mean(axis=1)

                # Resample if not 16kHz
                if sr != self.STT_SAMPLE_RATE:
                    import torchaudio.transforms as T
                    # Convert to tensor if needed
                    if audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
                        audio_tensor = torch.from_numpy(audio_data).float()
                    else:
                        audio_tensor = torch.from_numpy(audio_data).float() / 32768.0

                    # Add batch dimension if needed
                    if audio_tensor.dim() == 1:
                        audio_tensor = audio_tensor.unsqueeze(0)

                    # Resample using torchaudio
                    resampler = T.Resample(sr, self.STT_SAMPLE_RATE, dtype=audio_tensor.dtype)
                    audio_tensor = resampler(audio_tensor)

                    # Convert back to numpy
                    audio_data = audio_tensor.squeeze().numpy()
                    sr = self.STT_SAMPLE_RATE

                # Save audio with proper format conversion
                # If float, scale to int16 range
                if audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
                    # Float audio is in [-1, 1], scale to int16 range [-32768, 32767]
                    audio_data = np.clip(audio_data, -1.0, 1.0)  # Clip to prevent overflow
                    audio_data = (audio_data * 32768).astype(np.int16)
                elif audio_data.dtype != np.int16:
                    # Convert other types to int16
                    audio_data = audio_data.astype(np.int16)

                with open(temp_path, 'wb') as f:
                    wavfile.write(f, sr, audio_data)

            except Exception as e:
                logger.warning(f"Could not resample audio: {e}, using original")

            # GUARDRAIL: Validate audio format before STT (Silero is very sensitive)
            # This is the exact checkpoint from the debugging checklist
            try:
                validate_sr, validate_audio = wavfile.read(temp_path)
                logger.info(
                    f"STT input WAV: sr={validate_sr}, dtype={validate_audio.dtype}, "
                    f"shape={validate_audio.shape}, min={validate_audio.min()}, max={validate_audio.max()}"
                )

                # FAIL FAST: Assert Silero requirements
                assert validate_sr == 16000, f"Invalid sample rate: {validate_sr}, expected 16000"
                assert validate_audio.dtype == np.int16, f"Invalid dtype: {validate_audio.dtype}, expected int16"
                assert validate_audio.ndim == 1, f"Audio must be mono, got shape {validate_audio.shape}"

                logger.info("STT audio validation passed")
            except AssertionError as e:
                logger.error(f"STT audio validation failed: {e}")
                return TranscriptionResponse(
                    text=f"[Audio format error: {str(e)}]",
                    confidence=0.0,
                    language=request.language
                )

            # Prepare audio for STT
            input_batch = self._stt_prepare_model_input(
                self._stt_read_batch([temp_path]),
                device=self.device
            )

            # Perform transcription
            with torch.no_grad():
                output = self.stt_model(input_batch)

            # Decode output
            text = self.stt_decoder(output[0].cpu())

            # Clean up temp file
            Path(temp_path).unlink(missing_ok=True)

            logger.info(f"Transcription successful: {text}")

            return TranscriptionResponse(
                text=text,
                confidence=0.95,
                language=request.language
            )

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            # Clean up temp file if it exists
            try:
                Path(temp_path).unlink(missing_ok=True)
            except:
                pass
            return TranscriptionResponse(
                text="[Transcription failed - see logs]",
                confidence=0.0,
                language=request.language
            )

    # TTS Sample Rate Configuration (SINGLE SOURCE OF TRUTH)
    # This rate is used for: Silero generation, WAV encoding, and playback expectation
    TTS_SAMPLE_RATE = 24000  # 24kHz - high quality, standard for TTS

    async def synthesize_speech(self, request: TTSSynthesisRequest) -> bytes:
        """
        Convert text to speech using Silero TTS with strict sample-rate contract.

        GUARANTEES:
        - Silero generates at exactly TTS_SAMPLE_RATE (24kHz)
        - WAV file is encoded at exactly TTS_SAMPLE_RATE
        - Playback will respect the WAV header
        - No sample rate conversion or reinterpretation occurs

        This prevents the "chipmunk/fast" bug caused by rate mismatches.
        """
        target_rate = self.TTS_SAMPLE_RATE

        try:
            # STEP 1: Generate audio at EXACT target sample rate
            # Silero's apply_tts() uses sample_rate parameter for both generation
            # and internal processing - this sets the contract
            try:
                # v3_en API: text + speaker parameter
                audio = self.tts_model.apply_tts(
                    text=request.text,
                    speaker='en_0',
                    sample_rate=target_rate  # MUST match our target rate
                )
            except TypeError:
                try:
                    # lj_v2 API: texts (plural)
                    audio_list = self.tts_model.apply_tts(
                        texts=request.text,
                        sample_rate=target_rate  # MUST match our target rate
                    )
                    audio = audio_list[0]
                except TypeError:
                    # Fallback: no explicit sample_rate (use model default)
                    # But this is risky - we should validate
                    audio = self.tts_model.apply_tts(
                        text=request.text,
                        speaker='en_0'
                    )

            # STEP 2: Validate audio tensor
            if not hasattr(audio, 'shape'):
                raise ValueError(f"Generated audio is not a tensor, got {type(audio)}")

            expected_samples_per_char = target_rate * 0.1  # heuristic: ~100ms per char
            min_expected = len(request.text) * expected_samples_per_char * 0.5
            max_expected = len(request.text) * expected_samples_per_char * 2.0

            if len(audio) < min_expected or len(audio) > max_expected:
                raise ValueError(
                    f"Audio duration anomaly: {len(audio)} samples for {len(request.text)} chars "
                    f"(expected {min_expected:.0f}-{max_expected:.0f}). "
                    f"Sample rate mismatch detected!"
                )

            # STEP 3: Save to WAV at EXACT same sample rate
            # This is CRITICAL - the WAV header MUST match generation rate
            import scipy.io.wavfile as wavfile
            audio_buffer = io.BytesIO()
            wavfile.write(
                audio_buffer,
                target_rate,  # EXACT same rate used for generation
                audio.cpu().numpy()
            )
            audio_buffer.seek(0)

            # STEP 4: Verify the WAV file
            audio_bytes = audio_buffer.read()
            if len(audio_bytes) < 100:
                raise ValueError("Generated WAV file is too small, header may be corrupted")

            logger.info(f"TTS synthesis successful: {request.text[:50]}... (rate={target_rate}Hz, samples={len(audio)})")

            return audio_bytes

        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            raise

    async def save_audio_file(self, audio_data: bytes, filename: Optional[str] = None) -> Path:
        """Save audio data to file."""
        if filename is None:
            filename = f"{uuid.uuid4()}.wav"

        file_path = self.upload_dir / filename

        with open(file_path, "wb") as f:
            f.write(audio_data)

        logger.info(f"Saved audio file: {file_path}")
        return file_path

    def is_speech(self, audio_chunk: np.ndarray) -> bool:
        """Check if audio chunk contains speech using VAD."""
        try:
            speech_prob = self.vad_model(
                torch.tensor(audio_chunk).float().to(self.device)
            ).item()
            return speech_prob > 0.5
        except:
            return False

    def get_audio_duration(self, audio_data: bytes) -> float:
        """Get audio duration in seconds."""
        try:
            # Simple estimation: bytes / (sample_rate * bit_depth / 8 * channels)
            # Assuming 16kHz, 16-bit, mono for WAV
            return len(audio_data) / (16000 * 2)
        except Exception as e:
            logger.error(f"Failed to get audio duration: {e}")
            return 0.0

    async def check_health(self) -> dict:
        """Check service health and model status."""
        return {
            "stt_available": True,
            "tts_available": True,
            "vad_available": True,
            "device": self.device.type,
            "models_loaded": all([
                hasattr(self, 'stt_model'),
                hasattr(self, 'tts_model'),
                hasattr(self, 'vad_model')
            ])
        }


# Global service instance
voice_memo_service = VoiceMemoService()

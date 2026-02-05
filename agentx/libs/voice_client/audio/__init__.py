"""Audio file handling for the voice client SDK."""

from agentx.libs.voice_client.audio.loader import AudioLoader
from agentx.libs.voice_client.audio.processor import AudioProcessor
from agentx.libs.voice_client.audio.validator import AudioValidator
from agentx.libs.voice_client.audio.writer import AudioWriter


class AudioHandler:
    """Facade for audio operations.

    Provides backward-compatible API using the new split architecture.
    """

    load_audio_file = AudioLoader.load_audio_file
    validate_audio = AudioValidator.validate_audio
    calculate_chunk_size = AudioProcessor.calculate_chunk_size
    chunk_audio = AudioProcessor.chunk_audio
    save_wav = AudioWriter.save_wav


__all__ = ["AudioHandler", "AudioLoader", "AudioProcessor", "AudioValidator", "AudioWriter"]

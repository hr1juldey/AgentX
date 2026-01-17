"""Application settings."""

from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "Voice Memos"
    version: str = "0.1.0"
    port: int = 8009
    debug: bool = True
    cors_origins: List[str] = ["*"]

    # Storage settings
    upload_dir: Path = Path("./uploads")
    max_file_size_mb: int = 25

    # Device configuration (GPU first, CPU fallback)
    device: str = "auto"  # auto, cpu, cuda
    force_cpu: bool = False  # Force CPU even if CUDA available

    # Silero STT settings
    stt_language: str = "en"  # Silero uses language codes like 'en', 'es', 'de'

    # Silero TTS settings
    # Available speakers for English: v3_en (natural male), lj_v2 (female), lj_8khz, lj_16khz, v3_en_indic
    tts_speaker: str = "v3_en"  # Speaker ID for TTS

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.upload_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()

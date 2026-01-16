"""Request and response schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class VoiceMemo(BaseModel):
    """Voice memo schema."""

    id: str
    filename: str
    transcription: Optional[str] = None
    duration_seconds: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)


class TranscriptionRequest(BaseModel):
    """Transcription request schema."""

    audio_data: str = Field(..., description="Base64 encoded audio data")
    language: str = Field(default="en-US", description="Language code")


class TranscriptionResponse(BaseModel):
    """Transcription response schema."""

    text: str
    confidence: Optional[float] = None
    language: str


class TTSSynthesisRequest(BaseModel):
    """Text-to-speech synthesis request."""

    text: str = Field(..., min_length=1, max_length=5000, description="Text to synthesize")
    language: str = Field(default="en", description="Language code")
    slow: bool = Field(default=False, description="Slow speech rate")


class TTSSynthesisResponse(BaseModel):
    """Text-to-speech synthesis response."""

    audio_data: str = Field(..., description="Base64 encoded MP3 audio")
    language: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    stt_available: bool
    tts_available: bool

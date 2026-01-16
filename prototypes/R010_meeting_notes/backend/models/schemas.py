"""Request and response schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TranscriptionSegment(BaseModel):
    """Single transcription segment."""
    text: str
    timestamp: float
    is_speech: bool


class MeetingNote(BaseModel):
    """Meeting note schema."""
    id: str
    title: str
    segments: List[TranscriptionSegment]
    created_at: datetime = Field(default_factory=datetime.now)


class TranscriptionRequest(BaseModel):
    """Transcription request."""
    audio_data: str = Field(..., description="Base64 encoded audio")
    sample_rate: int = Field(default=16000, description="Audio sample rate")
    language: str = Field(default="en-US", description="Language code")


class RealTimeTranscription(BaseModel):
    """Real-time transcription response."""
    text: str
    is_speech: bool
    timestamp: float
    confidence: Optional[float] = None

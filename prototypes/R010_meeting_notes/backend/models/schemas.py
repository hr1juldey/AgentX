"""
Request and response schemas for Meeting Notes API.

This module provides Pydantic models for real-time meeting transcription
with enhanced Swagger documentation.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TranscriptionSegment(BaseModel):
    """A single transcribed segment with timing information.

    Represents one piece of transcribed speech with metadata
    about when it occurred and whether it contains actual speech.
    """

    text: str = Field(
        ...,
        description="Transcribed text content",
        examples=["Hello everyone, let's start the meeting"],
    )
    timestamp: float = Field(
        ..., description="Timestamp in seconds from the start", examples=[12.5], ge=0.0
    )
    is_speech: bool = Field(
        ..., description="Whether this segment contains speech (vs silence/noise)", examples=[True]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Hello everyone, let's start the meeting",
                    "timestamp": 12.5,
                    "is_speech": True,
                }
            ]
        }
    }


class MeetingNote(BaseModel):
    """A complete meeting note with all transcription segments.

    Represents a full meeting session with transcribed segments
    and metadata.
    """

    id: str = Field(
        ..., description="Unique identifier for the meeting", examples=["meeting-2024-01-15-001"]
    )
    title: str = Field(
        ...,
        description="Meeting title or description",
        examples=["Weekly Team Standup", "Product Planning Session"],
    )
    segments: List[TranscriptionSegment] = Field(
        ..., description="List of transcribed segments in chronological order", min_length=0
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="When the meeting note was created"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "meeting-2024-01-15-001",
                    "title": "Weekly Team Standup",
                    "segments": [
                        {
                            "text": "Hello everyone, let's start the meeting",
                            "timestamp": 12.5,
                            "is_speech": True,
                        },
                        {
                            "text": "Today we'll discuss the project status",
                            "timestamp": 15.2,
                            "is_speech": True,
                        },
                    ],
                    "created_at": "2024-01-15T10:00:00Z",
                }
            ]
        }
    }


class TranscriptionRequest(BaseModel):
    """Request to transcribe audio chunk for meeting notes.

    Send audio chunks for real-time transcription with speech activity detection.

    **How to send audio:**
    1. Read audio file bytes or capture from microphone
    2. Encode to Base64: `base64.b64encode(audio_bytes).decode()`
    3. Send the Base64 string as `audio_data`

    For best results, use 16kHz mono audio (auto-converted if needed).
    """

    audio_data: str = Field(
        ...,
        description="Base64-encoded audio chunk bytes. Encode with: base64.b64encode(audio_bytes).decode()",
        min_length=1,
    )
    sample_rate: int = Field(
        default=16000, description="Audio sample rate in Hz (16000 recommended)", ge=8000, le=48000
    )
    language: str = Field(
        default="en",
        description="Language code for transcription (en, es, de, fr, etc.)",
        pattern="^[a-z]{2}$",
    )

    model_config = {"json_schema_extra": {"examples": [{"sample_rate": 16000, "language": "en"}]}}


class RealTimeTranscription(BaseModel):
    """Real-time transcription response with speech detection.

    Contains transcribed text with confidence score and speech activity
    detection for each audio chunk.
    """

    text: str = Field(
        ...,
        description="Transcribed text from the audio chunk",
        examples=["Hello everyone, let's start"],
    )
    is_speech: bool = Field(
        ...,
        description="Whether speech was detected (vs silence/background noise)",
        examples=[True],
    )
    timestamp: float = Field(
        ...,
        description="Timestamp in seconds from the start of the meeting",
        examples=[45.3],
        ge=0.0,
    )
    confidence: Optional[float] = Field(
        None,
        description="Confidence score (0.0 to 1.0) if available",
        ge=0.0,
        le=1.0,
        examples=[0.92],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Hello everyone, let's start",
                    "is_speech": True,
                    "timestamp": 45.3,
                    "confidence": 0.92,
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """Health check response showing service status."""

    status: str = Field(..., description="Service health status", examples=["healthy", "unhealthy"])
    stt_available: bool = Field(
        ..., description="Whether speech-to-text is available", examples=[True]
    )
    tts_available: bool = Field(
        ..., description="Whether text-to-speech is available", examples=[True]
    )
    vad_available: bool = Field(
        ..., description="Whether voice activity detection is available", examples=[True]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "healthy",
                    "stt_available": True,
                    "tts_available": True,
                    "vad_available": True,
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Error response with details."""

    error: str = Field(
        ...,
        description="Type of error that occurred",
        examples=["ValidationError", "ProcessingError"],
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
        examples=["Failed to transcribe audio: invalid format"],
    )
    detail: Optional[str] = Field(None, description="Additional technical details for debugging")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "ValidationError",
                    "message": "Audio data is required",
                    "detail": "Field 'audio_data' is required but was not provided",
                }
            ]
        }
    }

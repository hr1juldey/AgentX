"""
Request and response schemas for Voice Memos API.

This module provides Pydantic models for all API endpoints with enhanced
Swagger documentation including examples and clear descriptions.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class VoiceMemo(BaseModel):
    """A voice memo with transcription.

    Represents a recorded audio memo with optional text transcription
    and metadata.
    """

    id: str = Field(
        ...,
        description="Unique identifier for the voice memo",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    filename: str = Field(
        ...,
        description="Original filename of the audio recording",
        examples=["memo_2024-01-15.wav"],
    )
    transcription: Optional[str] = Field(
        None,
        description="Transcribed text from the audio (if processed)",
        examples=["Hello world, this is a test recording"],
    )
    duration_seconds: Optional[float] = Field(
        None, description="Duration of the audio in seconds", examples=[12.5]
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="When the voice memo was created"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "filename": "memo_2024-01-15.wav",
                    "transcription": "Hello world, this is a test recording",
                    "duration_seconds": 12.5,
                    "created_at": "2024-01-15T10:30:00Z",
                }
            ]
        }
    }


class TranscriptionRequest(BaseModel):
    """Request to transcribe audio to text.

    Send Base64-encoded audio data to receive a text transcription.
    Supports WAV files with automatic sample rate conversion.

    **How to prepare your audio:**
    1. Save your audio as a WAV file
    2. Read the file bytes
    3. Encode to Base64: `base64.b64encode(file_bytes).decode()`
    4. Send the Base64 string as `audio_data`

    See endpoint documentation for Python code examples.
    """

    audio_data: str = Field(
        ...,
        description="Base64-encoded WAV file bytes. Read your audio file and encode with: base64.b64encode(file_bytes).decode()",
        min_length=1,
    )
    language: str = Field(
        default="en",
        description="Language code for transcription (en, es, de, fr, etc.)",
        pattern="^[a-z]{2}$",
    )

    model_config = {"json_schema_extra": {"examples": [{"language": "en"}]}}


class TranscriptionResponse(BaseModel):
    """Response containing transcribed text and metadata."""

    text: str = Field(
        ..., description="Transcribed text from the audio", examples=["Hello world, this is a test"]
    )
    confidence: Optional[float] = Field(
        None,
        description="Confidence score (0.0 to 1.0) if available",
        ge=0.0,
        le=1.0,
        examples=[0.95],
    )
    language: str = Field(..., description="Detected or specified language code", examples=["en"])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"text": "Hello world, this is a test", "confidence": 0.95, "language": "en"}
            ]
        }
    }


class TTSSynthesisRequest(BaseModel):
    """Request to convert text to speech audio.

    Generates natural-sounding speech from input text using Silero TTS.
    Returns audio in WAV format at 24kHz.
    """

    text: str = Field(
        ...,
        description="The text to convert to speech",
        min_length=1,
        max_length=5000,
        examples=["Hello world, this is a test of text to speech"],
    )
    language: str = Field(
        default="en",
        description="Language code (default: English)",
        examples=["en", "es", "de", "fr"],
        pattern="^[a-z]{2}$",
    )
    slow: bool = Field(
        default=False,
        description="Use slower speech rate for better clarity",
        examples=[False, True],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Hello world, this is a test of text to speech",
                    "language": "en",
                    "slow": False,
                }
            ]
        }
    }


class TTSSynthesisResponse(BaseModel):
    """Response containing synthesized speech audio.

    To save the audio file:
    1. Decode the Base64 string: `audio_bytes = base64.b64decode(audio_data)`
    2. Write to file: `with open('speech.wav', 'wb') as f: f.write(audio_bytes)`

    For direct file download, use the /tts/download endpoint instead.
    """

    audio_data: str = Field(
        ...,
        description="Base64-encoded WAV audio (24kHz, mono). Decode with: base64.b64decode(audio_data)",
    )
    language: str = Field(..., description="Language used for synthesis")

    model_config = {"json_schema_extra": {"examples": [{"language": "en"}]}}


class HealthResponse(BaseModel):
    """Health check response showing service status."""

    status: str = Field(..., description="Service health status", examples=["healthy", "unhealthy"])
    stt_available: bool = Field(
        ..., description="Whether speech-to-text is available", examples=[True]
    )
    tts_available: bool = Field(
        ..., description="Whether text-to-speech is available", examples=[True]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{"status": "healthy", "stt_available": True, "tts_available": True}]
        }
    }


class ErrorResponse(BaseModel):
    """Error response with details."""

    error: str = Field(
        ...,
        description="Type of error that occurred",
        examples=["ValidationError", "ProcessingError", "ServiceUnavailable"],
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

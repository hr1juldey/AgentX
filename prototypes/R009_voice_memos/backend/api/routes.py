"""
API routes for Voice Memos service.

This module provides REST endpoints for:
- Speech-to-Text (STT): Transcribe audio to text
- Text-to-Speech (TTS): Convert text to natural speech audio
- Health checks
"""

import base64

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response

from models.schemas import (
    HealthResponse,
    TranscriptionRequest,
    TranscriptionResponse,
    TTSSynthesisRequest,
)
from services.service import voice_memo_service

router = APIRouter(
    tags=["Voice Memos"],
    responses={
        400: {"description": "Invalid request", "model": dict},
        500: {"description": "Internal server error", "model": dict}
    }
)


@router.post(
    "/transcribe",
    response_model=TranscriptionResponse,
    summary="Transcribe audio to text",
    description="""
    Convert speech audio to written text using Silero STT.

    **How to use:**
    1. Encode your audio file (WAV format) to Base64
    2. Send the Base64 string in the `audio_data` field
    3. Receive transcribed text with confidence score

    **Supported formats:**
    - WAV files (any sample rate - auto-converted to 16kHz)
    - Mono or stereo (auto-converted to mono)
    - Maximum file size: 25MB

    **Example in Python:**
    ```python
    import base64
    import requests

    with open("audio.wav", "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode()

    response = requests.post(
        "http://localhost:8009/transcribe",
        json={"audio_data": audio_b64, "language": "en"}
    )
    print(response.json()["text"])
    ```
    """,
    responses={
        200: {
            "description": "Successful transcription",
            "content": {
                "application/json": {
                    "example": {
                        "text": "Hello world, this is a test",
                        "confidence": 0.95,
                        "language": "en"
                    }
                }
            }
        }
    }
)
async def transcribe_audio(request: TranscriptionRequest) -> TranscriptionResponse:
    """Transcribe audio to text using speech recognition."""
    try:
        result = await voice_memo_service.transcribe_audio(request)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid audio data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )


@router.post(
    "/tts",
    summary="Convert text to speech (Base64 response)",
    description="""
    Generate natural-sounding speech from text. Returns audio as Base64 string.

    Use this endpoint when you need the audio data as a string (e.g., for JSON APIs).
    For direct file download, use `/tts/download` instead.
    """,
    response_class=Response,
    responses={
        200: {
            "description": "Base64-encoded WAV audio",
            "content": {
                "text/plain": {
                    "example": "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA="
                }
            }
        }
    }
)
async def synthesize_speech(request: TTSSynthesisRequest) -> Response:
    """Convert text to speech audio, returned as Base64 string."""
    try:
        audio_data = await voice_memo_service.synthesize_speech(request)
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")

        return Response(
            content=audio_base64,
            media_type="text/plain",
            headers={
                "Content-Disposition": "attachment; filename=speech.wav"
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid text input: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TTS synthesis failed: {str(e)}"
        )


@router.post(
    "/tts/download",
    summary="Convert text to speech (file download)",
    description="""
    Generate natural-sounding speech from text. Returns audio as downloadable WAV file.

    **Audio specifications:**
    - Format: WAV
    - Sample rate: 24kHz
    - Channels: Mono
    - Quality: High (Silero TTS v3)

    **Example in Python:**
    ```python
    import requests

    response = requests.post(
        "http://localhost:8009/tts/download",
        json={"text": "Hello world", "language": "en"}
    )

    with open("speech.wav", "wb") as f:
        f.write(response.content)
    ```
    """,
    response_class=Response,
    responses={
        200: {
            "description": "WAV audio file",
            "content": {
                "audio/mpeg": {
                    "schema": {
                        "type": "string",
                        "format": "binary"
                    }
                }
            }
        }
    }
)
async def download_speech(request: TTSSynthesisRequest) -> Response:
    """Download speech as WAV file."""
    try:
        audio_data = await voice_memo_service.synthesize_speech(request)

        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.wav"
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid text input: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TTS synthesis failed: {str(e)}"
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="""
    Check if the service is running and all models are loaded.

    Returns the status of:
    - Speech-to-Text (STT) model
    - Text-to-Speech (TTS) model
    - Voice Activity Detection (VAD) model
    """
)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    health = await voice_memo_service.check_health()

    return HealthResponse(
        status="healthy" if health["models_loaded"] else "unhealthy",
        stt_available=health["stt_available"],
        tts_available=health["tts_available"]
    )

"""
API routes for Meeting Notes service.

This module provides REST endpoints for:
- Real-time Speech-to-Text (STT): Transcribe meeting audio with VAD
- Text-to-Speech (TTS): Convert text to natural speech audio
- Health checks
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
import base64

from models.schemas import (
    TranscriptionRequest,
    RealTimeTranscription,
    HealthResponse
)
from services.service import meeting_notes_service

router = APIRouter(
    tags=["Meeting Notes"],
    responses={
        400: {"description": "Invalid request", "model": dict},
        500: {"description": "Internal server error", "model": dict}
    }
)


@router.post(
    "/transcribe",
    response_model=RealTimeTranscription,
    summary="Transcribe audio chunk with speech detection",
    description="""
    Convert speech audio to written text using Silero STT with Voice Activity Detection.

    **How to use:**
    1. Encode your audio file (WAV format) to Base64
    2. Send the Base64 string in the `audio_data` field
    3. Receive transcribed text with speech activity flag

    **Supported formats:**
    - WAV files (any sample rate - auto-converted to 16kHz)
    - Mono or stereo (auto-converted to mono)
    - Streaming chunks for real-time transcription

    **Example in Python:**
    ```python
    import base64
    import requests

    with open("meeting_audio.wav", "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode()

    response = requests.post(
        "http://localhost:8010/transcribe",
        json={"audio_data": audio_b64, "sample_rate": 16000, "language": "en"}
    )
    result = response.json()
    print(f"Text: {result['text']}, Speech detected: {result['is_speech']}")
    ```
    """,
    responses={
        200: {
            "description": "Successful transcription",
            "content": {
                "application/json": {
                    "example": {
                        "text": "Hello everyone, let's start the meeting",
                        "is_speech": True,
                        "timestamp": 12.5,
                        "confidence": 0.92
                    }
                }
            }
        }
    }
)
async def transcribe_audio(request: TranscriptionRequest) -> RealTimeTranscription:
    """Transcribe audio with VAD for meeting notes."""
    try:
        audio_bytes = base64.b64decode(request.audio_data)
        text, is_speech = await meeting_notes_service.transcribe_audio(audio_bytes)
        return RealTimeTranscription(text=text, is_speech=is_speech, timestamp=0.0)
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
    Generate natural-sounding speech from text for meeting notes playback.

    **Example in Python:**
    ```python
    import requests
    import base64

    response = requests.post(
        "http://localhost:8010/tts",
        json={"text": "The meeting will start at 10 AM"}
    )

    result = response.json()
    audio_bytes = base64.b64decode(result["audio_data"])

    with open("meeting_note.wav", "wb") as f:
        f.write(audio_bytes)
    ```
    """,
    responses={
        200: {
            "description": "Base64-encoded WAV audio",
            "content": {
                "application/json": {
                    "example": {
                        "audio_data": "<Base64-encoded WAV audio>",
                        "format": "wav",
                        "sample_rate": 24000
                    }
                }
            }
        }
    }
)
async def text_to_speech(request: dict):
    """Convert text to speech audio, returned as Base64 string."""
    try:
        text = request.get("text", "")
        if not text:
            raise ValueError("text is required")

        audio_data = await meeting_notes_service.synthesize_speech(text)
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")
        return {"audio_data": audio_base64, "format": "wav", "sample_rate": 24000}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
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
async def health() -> HealthResponse:
    """Health check endpoint."""
    health_data = await meeting_notes_service.check_health()

    return HealthResponse(
        status="healthy" if health_data.get("stt_available") and health_data.get("tts_available") else "unhealthy",
        stt_available=health_data.get("stt_available", False),
        tts_available=health_data.get("tts_available", False),
        vad_available=health_data.get("vad_available", False)
    )

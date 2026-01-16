"""API routes."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
import base64
import io

from models.schemas import (
    TranscriptionRequest,
    TranscriptionResponse,
    TTSSynthesisRequest,
    TTSSynthesisResponse,
    HealthResponse
)
from services.service import voice_memo_service

router = APIRouter(tags=["voice"])


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(request: TranscriptionRequest):
    """Transcribe audio to text using speech recognition."""
    try:
        result = await voice_memo_service.transcribe_audio(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


@router.post("/tts")
async def synthesize_speech(request: TTSSynthesisRequest):
    """Convert text to speech audio."""
    try:
        audio_data = await voice_memo_service.synthesize_speech(request)
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")

        return Response(
            content=audio_base64,
            media_type="text/plain",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"TTS synthesis failed: {str(e)}"
        )


@router.post("/tts/download")
async def download_speech(request: TTSSynthesisRequest):
    """Download speech as MP3 file."""
    try:
        audio_data = await voice_memo_service.synthesize_speech(request)

        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"TTS synthesis failed: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    health = await voice_memo_service.check_health()

    return HealthResponse(
        status="healthy",
        stt_available=health["stt_available"],
        tts_available=health["tts_available"]
    )

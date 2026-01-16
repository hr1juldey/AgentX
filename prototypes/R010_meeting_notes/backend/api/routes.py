"""API routes."""
from fastapi import APIRouter, HTTPException
import base64
from models.schemas import TranscriptionRequest, RealTimeTranscription
from services.service import meeting_notes_service

router = APIRouter(tags=["meeting"])


@router.post("/transcribe")
async def transcribe_audio(request: TranscriptionRequest):
    """Transcribe audio with VAD."""
    try:
        audio_bytes = base64.b64decode(request.audio_data)
        text, is_speech = await meeting_notes_service.transcribe_audio(audio_bytes)
        return RealTimeTranscription(text=text, is_speech=is_speech, timestamp=0.0)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tts")
async def text_to_speech(request: dict):
    """Convert text to speech."""
    try:
        text = request.get("text", "")
        audio_data = await meeting_notes_service.synthesize_speech(text)
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")
        return {"audio_data": audio_base64, "format": "wav", "sample_rate": 24000}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    """Health check endpoint."""
    health_data = await meeting_notes_service.check_health()
    return {"status": "healthy", **health_data}

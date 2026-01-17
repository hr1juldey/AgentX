"""API routes for Personal Assistant with WebSocket voice support."""

import base64
import logging
import uuid

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from models.schemas import ChatRequest, ChatResponse, ToolSchema
from services.service import assistant_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["assistant"])


class TTSRequest(BaseModel):
    """Text-to-speech request."""

    text: str
    language: str = "en"


class TTSResponse(BaseModel):
    """Text-to-speech response with base64-encoded audio."""

    audio_data: str


@router.post("/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """Convert text to speech using Silero TTS.

    Returns base64-encoded WAV audio.
    """
    try:
        audio = await assistant_service.tts.synthesize(request.text)
        audio_b64 = base64.b64encode(audio).decode()
        return TTSResponse(audio_data=audio_b64)
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message with the DSPy ReAct agent.

    **Example in Python:**
    ```python
    import requests

    response = requests.post(
        "http://localhost:8011/chat",
        json={"message": "What is 2 + 2?", "conversation_id": "my-chat"}
    )
    result = response.json()
    print(result["response"])
    ```
    """
    try:
        response = await assistant_service.process_message(request)
        return response
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools", response_model=list[ToolSchema])
async def list_tools():
    """List available tools for the ReAct agent."""
    tools = [
        ToolSchema(
            name="calculator", description="Calculate mathematical expressions", parameters={}
        ),
        ToolSchema(name="search", description="Search for information", parameters={}),
        ToolSchema(name="weather", description="Get weather information", parameters={}),
    ]
    return tools


@router.get("/health")
async def health():
    """Check if the service and all models are healthy."""
    return {
        "status": "healthy",
        "agent_ready": True,
        "stt_available": hasattr(assistant_service, "stt"),
        "tts_available": hasattr(assistant_service, "tts"),
    }


@router.websocket("/ws/voice")
async def websocket_voice(websocket: WebSocket):
    """WebSocket endpoint for real-time voice conversation.

    **Message Flow:**
    1. Client connects → Server sends {"type": "connected", "session_id": "..."}
    2. Client sends audio chunks → {"type": "audio_chunk", "audio_data": "<base64>"}
    3. Server transcribes → {"type": "transcription", "text": "..."}
    4. Server thinks → {"type": "thinking"}
    5. Server streams response → {"type": "response_chunk", "text": "..."}
    6. Server sends audio → {"type": "audio", "data": "<base64>"}
    7. Server ready for more → {"type": "listening"}

    **Audio Format:**
    - Send audio chunks as Base64-encoded WAV
    - Recommended: 16kHz mono (auto-converted if needed)
    - Chunk size: ~1 second for real-time streaming

    **Example in JavaScript:**
    ```javascript
    const ws = new WebSocket("ws://localhost:8011/ws/voice");

    ws.onopen = () => console.log("Connected");

    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        switch (msg.type) {
            case "transcription":
                console.log("You said:", msg.text);
                break;
            case "response_chunk":
                console.log("Assistant:", msg.text);
                break;
            case "audio":
                playAudio(base64.decode(msg.data));
                break;
        }
    };

    // Send audio chunk
    ws.send(JSON.stringify({
        type: "audio_chunk",
        audio_data: base64Encode(audioChunk)
    }));
    ```
    """
    await websocket.accept()

    session_id = str(uuid.uuid4())
    history = []

    await websocket.send_json({"type": "connected", "session_id": session_id})

    logger.info(f"WebSocket connected: {session_id}")

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "audio_chunk":
                audio_bytes = base64.b64decode(data.get("audio_data", ""))

                # STT
                text = await assistant_service.stt.transcribe(audio_bytes)

                if not text.strip():
                    await websocket.send_json({"type": "listening"})
                    continue

                history.append({"role": "user", "content": text})

                await websocket.send_json({"type": "transcription", "text": text})

                # Stream response
                await websocket.send_json({"type": "thinking"})
                await websocket.send_json({"type": "response_start"})

                response_text = ""
                async for chunk in assistant_service.chat_stream(text, history):
                    response_text += chunk
                    await websocket.send_json({"type": "response_chunk", "text": chunk})

                history.append({"role": "assistant", "content": response_text})

                # TTS
                audio = await assistant_service.tts.synthesize(response_text)

                await websocket.send_json(
                    {"type": "audio", "data": base64.b64encode(audio).decode()}
                )

                await websocket.send_json({"type": "listening"})

            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except (WebSocketDisconnect, RuntimeError, OSError):
            pass

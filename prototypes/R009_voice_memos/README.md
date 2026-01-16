# R009: Voice Memos (Level 5)

Voice recording and transcription prototype with STT and TTS capabilities.

## Features

- **Voice Recording**: Record audio directly from browser
- **Speech-to-Text**: Transcribe audio using Google Speech Recognition
- **Text-to-Speech**: Synthesize speech from text using gTTS
- **Memo Management**: Save, view, and delete voice memos
- **Real-time Feedback**: Visual recording indicator and transcription status

## Tech Stack

- **Backend**: FastAPI + SpeechRecognition + gTTS + pydub
- **Frontend**: Next.js + shadcn/ui + MediaRecorder API
- **Port**: 8009

## Quick Start

### Backend

```bash
cd backend
pip install -e .
# Install system dependencies:
# - Ubuntu/Debian: sudo apt-get install ffmpeg libportaudio2
# - macOS: brew install ffmpeg portaudio
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Requirements

- Python 3.11+
- Node.js 18+
- FFmpeg (for audio processing)
- Microphone access (for browser recording)

## API Endpoints

- `POST /transcribe` - Transcribe audio to text
- `POST /tts` - Synthesize speech (returns base64)
- `POST /tts/download` - Synthesize speech (downloads MP3)
- `GET /health` - Health check

## Notes

- Requires microphone permission in browser
- Speech Recognition uses Google's free API (requires internet)
- Audio is recorded as WAV in browser, sent as base64
- TTS uses Google Translate TTS (free tier)

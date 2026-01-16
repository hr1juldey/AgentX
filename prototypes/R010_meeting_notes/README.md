# R010: Meeting Notes (Level 5)

Real-time meeting transcription with Voice Activity Detection.

## Features

- **Real-time Transcription**: Live streaming transcription
- **VAD**: Voice Activity Detection to identify speech segments
- **Meeting Notes**: Auto-generate notes from transcription
- **Timestamps**: Track when each segment was spoken

## Tech Stack

- **Backend**: FastAPI + webrtcvad + SpeechRecognition
- **Frontend**: Next.js + shadcn/ui
- **Port**: 8010

## Quick Start

### Backend
```bash
cd backend
pip install -e .
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Notes

- VAD helps separate speech from silence
- Streaming transcription updates in real-time
- Google Speech Recognition API (requires internet)

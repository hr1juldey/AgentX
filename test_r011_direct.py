#!/usr/bin/env python3
"""Direct test of R011 STT service."""

import sys

sys.path.insert(
    0,
    "/home/riju279/Documents/Code/XRIG/AgentX/prototypes/R011_personal_assistant/backend",
)

from services.stt_service import stt_service

WAV_FILE = "/home/riju279/Documents/Code/XRIG/AgentX/silero_test.wav"


async def test_stt_direct():
    """Test STT service directly."""
    print(f"Testing STT with: {WAV_FILE}")

    with open(WAV_FILE, "rb") as f:
        audio_data = f.read()

    print(f"Audio size: {len(audio_data)} bytes")

    # Test transcription
    result = await stt_service.transcribe(audio_data)

    print(f"\nTranscription result: '{result}'")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_stt_direct())

#!/usr/bin/env python3
"""Test R011 backend STT with WAV file."""

import base64
import requests

WAV_FILE = "/home/riju279/Documents/Code/XRIG/AgentX/silero_test.wav"
API_URL = "http://localhost:8011"


def test_stt():
    """Test STT endpoint with WAV file."""
    # Read WAV file
    with open(WAV_FILE, "rb") as f:
        audio_data = f.read()

    # Encode to base64
    audio_b64 = base64.b64encode(audio_data).decode()

    print(f"Audio file size: {len(audio_data)} bytes")
    print(f"Base64 size: {len(audio_b64)} chars")
    print("\nTesting STT endpoint...")

    # Test STT
    response = requests.post(
        f"{API_URL}/chat",
        json={"message": "Transcribe this audio", "conversation_id": "test"},
    )

    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.json()}")


if __name__ == "__main__":
    test_stt()

#!/usr/bin/env python3
"""Demo script to test TTS output with kyutai server - FULL AUDIO.

Usage:
    python tests/integration/infrastructure/external/test_tts_demo.py
"""

import asyncio
import json
import time
from uuid import uuid4

import websockets


KYUTAI_TTS_URL = "ws://localhost:16000/api/v1/ws/tts?encoding=json"


async def test_tts_output():
    """Test TTS output with kyutai server - capture full audio."""
    session_id = str(uuid4())

    print("🎤 Testing TTS Output (FULL AUDIO)")
    print(f"📡 Connecting to {KYUTAI_TTS_URL}")

    tts_ws = None
    try:
        tts_ws = await websockets.connect(KYUTAI_TTS_URL)
        print("✅ Connected")

        # Config
        config_msg = {
            "type": "Config",
            "data": {"voice_id": "default", "output_format": "pcm_int16", "streaming": True},
            "session_id": session_id,
            "timestamp": time.time(),
        }
        await tts_ws.send(json.dumps(config_msg))
        print("📝 Config sent")

        # Send text
        text = "Hello! This is a test of the AgentX voice integration with kyutai text to speech. The system is working properly and producing high quality audio output."
        text_msg = {
            "type": "Text",
            "data": text,
            "session_id": session_id,
            "timestamp": time.time(),
        }
        await tts_ws.send(json.dumps(text_msg))
        print(f"🗣️  Synthesizing: '{text}'\n")

        # Receive ALL audio until EOS
        audio_chunks = []
        chunk_count = 0

        while True:
            response = await asyncio.wait_for(tts_ws.recv(), timeout=10.0)
            message = json.loads(response)

            msg_type = message.get("type")

            if msg_type == "Audio":
                import base64
                audio_data = base64.b64decode(message.get("data", ""))
                audio_chunks.append(audio_data)
                chunk_count += 1
                print(f"   Chunk {chunk_count}: {len(audio_data)} bytes", end="\r")

            elif msg_type == "Eos":
                print("\n\n✅ EOS received - synthesis complete!")
                break

            elif msg_type == "Text" and message.get("data", {}).get("source") == "tts":
                # TTS status message
                status = message["data"]
                print(f"\n   TTS Status: {status}")

        # Save raw PCM
        if audio_chunks:
            combined = b"".join(audio_chunks)
            filename = f"/tmp/tts_output_full_{session_id[:8]}.pcm"

            with open(filename, "wb") as f:
                f.write(combined)

            duration = len(combined) / (24000 * 2)  # bytes / (sample_rate * bytes_per_sample)
            print(f"\n💾 Saved {len(combined)} bytes to {filename}")
            print(f"   Duration: {duration:.2f} seconds @ 24000 Hz")
            print("\n▶️  Playing audio...")

            # Play the audio
            import subprocess
            subprocess.run(["aplay", "-f", "S16_LE", "-r", "24000", "-c", "1", filename])

            print(f"\n✅ Done! File saved at: {filename}")
            print(f"   Play again: ffplay -f s16le -ar 24000 -ac 1 {filename}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if tts_ws:
            await tts_ws.close()
            print("\n🔌 Closed")


if __name__ == "__main__":
    asyncio.run(test_tts_output())

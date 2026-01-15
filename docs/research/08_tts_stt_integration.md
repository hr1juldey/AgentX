# TTS/STT Integration Guide for Real-Time Voice AI

## Overview

This guide covers building real-time voice interfaces for AGENTX using CPU-efficient Text-to-Speech (TTS) and Speech-to-Text (STT) models. The primary challenge is managing the real-time, unpredictable nature of human speech while maintaining low latency and natural conversation flow.

## The Real-Time Challenge

### Why Speech is Different from Text

**Text-Based Interactions:**
- Input is discrete and complete (user presses Enter)
- Can process entire messages at once
- Easy to buffer and queue
- No timing constraints

**Speech-Based Interactions:**
- Input is continuous and streaming
- Cannot predict when speech will end
- Must process chunks in real-time
- Strict latency requirements (<300ms for natural feel)
- Must handle interruptions and turn-taking
- Memory constraints from streaming buffers

### The Core Problem: Predicting Speech End

```
User Speech Timeline:
┌─────────────────────────────────────────────────────────┐
│ [silence] [speaking...] [pause...] [still speaking]     │
│                                                           │
│ VAD:     ──► DETECTED ──► DETECTED ──► MAYBE DONE?      │
│                                                           │
│ System:  [buffer chunk] [buffer chunk] [wait...]       │
│                                                           │
│ Challenge: When is speech actually finished?            │
│ - False positive: Cut user off mid-sentence            │
│ - False negative: Awkward silence before response      │
└─────────────────────────────────────────────────────────┘
```

**Key Insight:** Your PC cannot predict when speech ends. It must wait for context using Voice Activity Detection (VAD) + timeout heuristics.

## Technology Stack

### 1. Pocket TTS (Text-to-Speech)

**Model:** `kyutai/pocket-tts`

**Key Specifications:**
- **Parameters:** 100M (extremely lightweight)
- **Platform:** CPU-only (no GPU needed)
- **Latency:** ~200ms to first audio chunk
- **Speed:** 6x real-time on MacBook Air M4
- **Memory:** 1.1GB base, up to 8.5GB with context (known issue)
- **Voice Cloning:** 5-10 second audio sample
- **Languages:** English only (as of Jan 2026)

**Architecture:**
- Uses **CALM (Continuous Audio Language Models)** - predicts continuous audio features instead of discrete tokens
- Processes text and audio in parallel for efficiency
- Streaming-first design (can handle infinitely long text)

**Installation:**
```bash
pip install "pocket-tts>=1.0.1"
pip install "torch>=2.5.0"  # CPU-only PyTorch
pip install "scipy>=1.14.0" "soundfile>=0.12.0"
```

### 2. Kyutai STT 2.6B (Speech-to-Text)

**Model:** `kyutai/stt-2.6b-en` or `kyutai/stt-2.6b-en-trfs` (Transformers)

**Key Specifications:**
- **Parameters:** 2.6B
- **Platform:** CPU/GPU
- **Language:** English
- **Architecture:** Based on Moshi speech-text foundation model
- **Features:** Streaming transcription with timestamps

**Installation:**
```bash
# STT model via Transformers
pip install "transformers>=4.30.0"
pip install "torch>=2.5.0"

# Model will be downloaded from HuggingFace on first use
# huggingface-cli login  # Required for some models
```

### 3. Voice Activity Detection (VAD)

**Options:**

#### A. Silero VAD (Recommended)
```bash
pip install "silero-vad>=5.1.0"
```

**Advantages:**
- Deep learning-based, highly accurate
- Low latency (<50ms)
- Handles noise well
- Probability-based (not just energy threshold)

#### B. WebRTC VAD (Alternative)
```bash
pip install "webrtcvad>=2.0.10"
```

**Advantages:**
- Lightweight, fast
- Battle-tested in WebRTC
- Good for resource-constrained environments

## Architecture Patterns

### Pattern 1: Simple Pipeline (Latency: 500-1000ms)

```
Audio Input → VAD → Buffer → STT → LLM → TTS → Audio Output
```

**Use Case:** Simple voice commands, not real-time conversation

**Implementation:**
```python
import asyncio
from pocket_tts import TTSModel
from silero_vad import VAD

class SimpleVoicePipeline:
    def __init__(self):
        self.tts = TTSModel()
        self.tts.load_model()
        self.vad = VAD()
        self.is_speaking = False

    async def process_audio(self, audio_chunk):
        # Wait for silence (VAD timeout)
        if not self.vad(audio_chunk):
            return None

        # STT processing
        text = await self.transcribe(audio_chunk)

        # LLM inference
        response = await self.llm_generate(text)

        # TTS generation
        audio = self.tts.generate_audio(response)
        return audio
```

**Pros:** Simple to implement
**Cons:** High latency, feels unnatural for conversation

### Pattern 2: Streaming Pipeline (Latency: 300-500ms)

```
Audio Stream → VAD → Chunked STT → LLM Stream → TTS Stream → Audio Stream
     ↓              ↓            ↓            ↓           ↓
  [real-time]   [continuous]  [streaming]  [streaming]  [playback]
```

**Use Case:** Natural conversation with interruptions

**Implementation:**
```python
import asyncio
import websockets
from collections import deque

class StreamingVoicePipeline:
    def __init__(self):
        self.tts = TTSModel()
        self.tts.load_model()

        # Audio buffer for VAD
        self.audio_buffer = deque(maxlen=16000 * 5)  # 5 seconds @ 16kHz
        self.vad_window = deque(maxlen=16000 * 1)     # 1 second for VAD

        # State management
        self.is_speaking = False
        self.silence_counter = 0
        self.SILENCE_THRESHOLD = 30  # ~1 second @ 30fps

    async def handle_websocket(self, websocket):
        """Handle bidirectional WebSocket for real-time audio."""
        try:
            async for message in websocket:
                audio_chunk = self.decode_audio(message)

                # VAD processing
                is_speech = self.vad.process(audio_chunk)

                if is_speech:
                    self.silence_counter = 0
                    self.audio_buffer.extend(audio_chunk)
                else:
                    self.silence_counter += 1

                # Trigger processing after silence threshold
                if self.silence_counter > self.SILENCE_THRESHOLD and len(self.audio_buffer) > 0:
                    # Process buffered speech
                    audio_data = np.array(self.audio_buffer)
                    self.audio_buffer.clear()

                    # Stream processing
                    await self.process_speech_stream(audio_data, websocket)

        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")

    async def process_speech_stream(self, audio_data, websocket):
        """Process speech with streaming response."""

        # STT (streaming)
        text_stream = self.stt.transcribe_stream(audio_data)

        # LLM (streaming)
        response_stream = self.llm.generate_stream(text_stream)

        # TTS (streaming) - start generating audio immediately
        audio_queue = asyncio.Queue()

        # Start TTS task
        tts_task = asyncio.create_task(
            self.tts_stream_worker(response_stream, audio_queue)
        )

        # Send audio chunks as they're generated
        while True:
            audio_chunk = await audio_queue.get()
            if audio_chunk is None:  # Sentinel for end
                break

            # Send to client
            await websocket.send(self.encode_audio(audio_chunk))

        await tts_task

    async def tts_stream_worker(self, text_stream, audio_queue):
        """Worker that generates TTS audio in real-time."""

        async for text_chunk in text_stream:
            # Generate audio chunk
            audio_chunk = self.tts.generate_audio(text_chunk)
            await audio_queue.put(audio_chunk)

        # Send end sentinel
        await audio_queue.put(None)
```

**Pros:** Lower latency, feels more natural
**Cons:** More complex, requires careful queue management

### Pattern 3: Interruptible Pipeline (Latency: 200-400ms)

```
Audio Input → VAD → [Interrupt Check] → STT → LLM → TTS → Audio Output
                                              ↓
                                        [Can be interrupted]
```

**Use Case:** Natural conversation with seamless interruptions

**Key Features:**
- Detect user interruptions while AI is speaking
- Stop TTS immediately when interrupted
- Resume from context
- Handle barge-in scenarios

**Implementation:**
```python
class InterruptibleVoicePipeline:
    def __init__(self):
        self.tts = TTSModel()
        self.tts.load_model()

        # Interruption state
        self.interrupted = False
        self.currently_speaking = False
        self.interrupt_lock = asyncio.Lock()

    async def generate_interruptible_speech(self, text, websocket):
        """Generate speech that can be interrupted by user."""

        # Split into sentences for interruption points
        sentences = self.split_into_sentences(text)

        for sentence in sentences:
            async with self.interrupt_lock:
                if self.interrupted:
                    # User interrupted, stop speaking
                    self.currently_speaking = False
                    self.interrupted = False
                    break

                self.currently_speaking = True

            # Generate audio for this sentence
            audio = self.tts.generate_audio(sentence)

            # Send in chunks to allow faster interruption
            for chunk in self.chunk_audio(audio, chunk_size=0.5):  # 500ms chunks
                async with self.interrupt_lock:
                    if self.interrupted:
                        break

                await websocket.send(self.encode_audio(chunk))

                # Small delay to allow interruption check
                await asyncio.sleep(0.01)

        self.currently_speaking = False

    async def handle_interruption(self, audio_chunk):
        """Handle user interruption."""

        is_speech = self.vad.process(audio_chunk)

        if is_speech and self.currently_speaking:
            # User interrupted while AI was speaking
            async with self.interrupt_lock:
                self.interrupted = True

            # Buffer the interruption audio
            self.interruption_buffer.extend(audio_chunk)
```

**Pros:** Most natural conversation feel
**Cons:** Most complex, requires precise timing

## Real-Time Context Management

### Challenge 1: Unknown Speech Duration

**Problem:** You don't know when the user will stop speaking.

**Solutions:**

#### A. VAD with Timeout (Recommended)
```python
class VADTimeoutStrategy:
    def __init__(self, silence_duration=1.0, sample_rate=16000):
        self.vad = SileroVAD()
        self.silence_duration = silence_duration
        self.sample_rate = sample_rate
        self.silence_frames = int(silence_duration * sample_rate / 512)  # 512 frame size
        self.silence_counter = 0
        self.audio_buffer = []

    async def process_audio_stream(self, audio_stream):
        """Process audio with VAD timeout."""

        async for audio_chunk in audio_stream:
            # Process each frame
            for frame in self.frame_generator(audio_chunk, frame_size=512):
                is_speech = self.vad(frame)

                if is_speech:
                    self.silence_counter = 0
                    self.audio_buffer.extend(frame)
                else:
                    self.silence_counter += 1

                # Check if speech ended
                if self.silence_counter >= self.silence_frames and len(self.audio_buffer) > 0:
                    # Speech ended, return buffered audio
                    audio_data = np.array(self.audio_buffer)
                    self.audio_buffer = []
                    self.silence_counter = 0
                    yield audio_data
```

#### B. Fixed Buffer with Overrun Detection
```python
class FixedBufferStrategy:
    def __init__(self, max_duration=10.0, sample_rate=16000):
        self.max_frames = int(max_duration * sample_rate)
        self.audio_buffer = []

    async def process_audio_stream(self, audio_stream):
        """Process audio with fixed buffer."""

        async for audio_chunk in audio_stream:
            self.audio_buffer.extend(audio_chunk)

            # Check buffer overrun
            if len(self.audio_buffer) >= self.max_frames:
                audio_data = np.array(self.audio_buffer[:self.max_frames])
                self.audio_buffer = self.audio_buffer[self.max_frames:]
                yield audio_data
```

### Challenge 2: Turn-Taking Coordination

**Problem:** Determining when to stop listening and start speaking.

**Solutions:**

#### A. Simple Timeout-Based
```python
async def timeout_based_turn_taking(self, audio_stream):
    """Use timeout to determine turns."""

    silence_duration = 0
    while True:
        audio_chunk = await audio_stream.get()

        is_speech = self.vad.process(audio_chunk)

        if is_speech:
            silence_duration = 0
        else:
            silence_duration += len(audio_chunk) / self.sample_rate

            # Check for turn end
            if silence_duration > 0.5:  # 500ms of silence
                return self.get_buffered_audio()
```

#### B. Prosody-Based (Advanced)
```python
async def prosody_based_turn_taking(self, audio_stream):
    """Use prosody (intonation, pause) to detect turn ends."""

    # This is more complex and requires additional models
    # to detect prosodic features like falling intonation

    # Simplified: combine VAD with energy detection
    energy_threshold = -30  # dB

    async for audio_chunk in audio_stream:
        is_speech = self.vad.process(audio_chunk)
        energy = self.calculate_energy(audio_chunk)

        if is_speech and energy < energy_threshold:
            # Possible turn end (falling energy)
            return self.get_buffered_audio()
```

### Challenge 3: Interruption Handling

**Problem:** User starts speaking while AI is generating response.

**Solutions:**

#### A. Full Duplex (Best for Natural Conversation)
```python
class FullDuplexVoiceAgent:
    """Full duplex: can listen while speaking."""

    def __init__(self):
        self.listening_task = None
        self.speaking_task = None
        self.interrupted = False

    async def start_listening(self, websocket):
        """Start listening in background."""

        self.listening_task = asyncio.create_task(
            self.listen_continuously(websocket)
        )

    async def listen_continuously(self, websocket):
        """Listen for speech, even while speaking."""

        async for message in websocket:
            audio_chunk = self.decode_audio(message)
            is_speech = self.vad.process(audio_chunk)

            if is_speech and self.speaking_task and not self.speaking_task.done():
                # User interrupted!
                self.interrupted = True
                self.speaking_task.cancel()

                # Buffer interruption audio
                self.interruption_buffer.extend(audio_chunk)

    async def speak_with_interruption(self, text, websocket):
        """Speak, but allow interruption."""

        self.speaking_task = asyncio.current_task()
        self.interrupted = False

        # Split into chunks for faster interruption
        for chunk in self.split_text_chunks(text, max_length=50):
            if self.interrupted:
                break

            audio = self.tts.generate_audio(chunk)
            await websocket.send(self.encode_audio(audio))
            await asyncio.sleep(0.01)  # Allow interruption check
```

#### B. Turn-Based (Simpler)
```python
class TurnBasedVoiceAgent:
    """Take turns: listen, then speak."""

    async def conversation_loop(self, websocket):
        """Alternating conversation."""

        while True:
            # Listen phase
            user_audio = await self.listen_for_turn(websocket)

            # Process phase
            user_text = await self.stt.transcribe(user_audio)
            response_text = await self.llm.generate(user_text)

            # Speak phase
            await self.speak_response(response_text, websocket)
```

## Memory Management

### Challenge: Unbounded Memory Growth

**Problem:** Pocket TTS has a known issue where RAM usage grows from 1.1GB to 32GB+ over time due to context accumulation.

**Solutions:**

#### A. Model Reload Strategy
```python
class MemoryManagedTTS:
    """Reload model to clear memory."""

    def __init__(self, reload_threshold=100):
        self.tts = TTSModel()
        self.tts.load_model()
        self.generation_count = 0
        self.reload_threshold = reload_threshold

    def generate_audio(self, text):
        """Generate with memory management."""

        self.generation_count += 1

        # Generate audio
        audio = self.tts.generate_audio(text)

        # Periodically reload to clear memory
        if self.generation_count >= self.reload_threshold:
            self.reload_model()

        return audio

    def reload_model(self):
        """Reload model to free memory."""

        # Unload
        del self.tts
        torch.cuda.empty_cache()  # If using GPU

        # Reload
        self.tts = TTSModel()
        self.tts.load_model()
        self.generation_count = 0
```

#### B. Process Isolation Strategy
```python
class ProcessIsolatedTTS:
    """Run TTS in separate process for memory isolation."""

    def __init__(self):
        self.tts_process = None
        self.start_tts_process()

    def start_tts_process(self):
        """Start TTS in separate process."""

        self.tts_process = multiprocessing.Process(
            target=self.tts_worker,
            args=(self.request_queue, self.response_queue)
        )
        self.tts_process.start()

    def tts_worker(self, request_queue, response_queue):
        """Worker process for TTS."""

        tts = TTSModel()
        tts.load_model()

        while True:
            text = request_queue.get()

            if text is None:  # Shutdown signal
                break

            audio = tts.generate_audio(text)
            response_queue.put(audio)

            # Periodic reload
            if self.generation_count % 100 == 0:
                del tts
                tts = TTSModel()
                tts.load_model()

    def generate_audio(self, text):
        """Generate audio via worker process."""

        self.request_queue.put(text)
        audio = self.response_queue.get()
        return audio
```

#### C. Voice State Caching Strategy
```python
class VoiceStateCache:
    """Cache voice states to reduce recomputation."""

    def __init__(self, max_cached_voices=10):
        self.voice_cache = {}
        self.max_cached_voices = max_cached_voices
        self.access_order = []

    def get_voice_state(self, voice_prompt):
        """Get cached voice state or create new one."""

        voice_key = hash(voice_prompt.tobytes())

        if voice_key in self.voice_cache:
            # Update access order
            self.access_order.remove(voice_key)
            self.access_order.append(voice_key)
            return self.voice_cache[voice_key]

        # Create new voice state
        voice_state = self.tts.get_state_for_audio_prompt(voice_prompt)

        # Cache management
        if len(self.voice_cache) >= self.max_cached_voices:
            # Evict least recently used
            lru_key = self.access_order.pop(0)
            del self.voice_cache[lru_key]

        # Add to cache
        self.voice_cache[voice_key] = voice_state
        self.access_order.append(voice_key)

        return voice_state
```

## WebSocket Bidirectional Streaming

### Architecture

```
Client (Browser/Phone)
    ↕ WebSocket
Server (FastAPI)
    ↕ asyncio.Queue
STT Worker ←────┐
    ↓           │
LLM Worker ────┤ Streaming Pipeline
    ↓           │
TTS Worker ←────┘
    ↓
Audio Queue
    ↕ WebSocket
Client
```

### Implementation

```python
from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect
import asyncio
import json

app = FastAPI()

class BidirectionalVoiceAgent:
    """Full duplex voice agent with WebSocket."""

    def __init__(self):
        self.tts = TTSModel()
        self.tts.load_model()

        # Queues for audio streaming
        self.audio_input_queue = asyncio.Queue(maxsize=100)
        self.audio_output_queue = asyncio.Queue(maxsize=100)

        # VAD
        self.vad = SileroVAD()

        # State
        self.is_speaking = False
        self.interrupted = False

    async def websocket_endpoint(self, websocket: WebSocket):
        """Handle WebSocket connection."""

        await websocket.accept()

        try:
            # Start background tasks
            input_task = asyncio.create_task(
                self.process_input_audio(websocket)
            )

            output_task = asyncio.create_task(
                self.process_output_audio(websocket)
            )

            # Wait for completion or error
            await asyncio.gather(input_task, output_task)

        except WebSocketDisconnect:
            print("Client disconnected")
        finally:
            # Cleanup
            input_task.cancel()
            output_task.cancel()

    async def process_input_audio(self, websocket):
        """Process incoming audio from client."""

        audio_buffer = []
        silence_counter = 0

        try:
            async for message in websocket:
                audio_chunk = self.decode_audio(message)

                # VAD processing
                is_speech = self.vad.process(audio_chunk)

                if is_speech:
                    silence_counter = 0
                    audio_buffer.extend(audio_chunk)

                    # Check for interruption
                    if self.is_speaking:
                        self.interrupted = True
                else:
                    silence_counter += 1

                    # Check if speech ended (silence threshold)
                    if silence_counter > 30 and len(audio_buffer) > 0:  # ~1 second
                        # Process buffered speech
                        audio_data = np.array(audio_buffer)
                        audio_buffer = []
                        silence_counter = 0

                        # Send to STT
                        await self.audio_input_queue.put(audio_data)

        except asyncio.CancelledError:
            pass

    async def process_output_audio(self, websocket):
        """Process outgoing audio to client."""

        try:
            while True:
                # Get audio from TTS
                audio_chunk = await self.audio_output_queue.get()

                if audio_chunk is None:  # End of speech
                    await websocket.send(json.dumps({"type": "speech_end"}))
                    self.is_speaking = False
                else:
                    # Send audio chunk
                    await websocket.send(self.encode_audio(audio_chunk))
                    self.is_speaking = True

        except asyncio.CancelledError:
            pass

    async def speech_pipeline(self):
        """Main speech processing pipeline."""

        while True:
            # Get audio from input queue
            audio_data = await self.audio_input_queue.get()

            # Check for interruption
            if self.interrupted:
                self.interrupted = False
                continue  # Skip this turn

            # STT
            user_text = await self.stt.transcribe(audio_data)

            # LLM
            response_text = await self.llm.generate(user_text)

            # TTS (streaming)
            await self.tts_stream(response_text)

    async def tts_stream(self, text):
        """Stream TTS output."""

        # Split into sentences
        sentences = self.split_into_sentences(text)

        for sentence in sentences:
            if self.interrupted:
                break

            # Generate audio
            audio = self.tts.generate_audio(sentence)

            # Chunk for streaming
            for chunk in self.chunk_audio(audio, chunk_size=0.5):  # 500ms
                if self.interrupted:
                    break

                await self.audio_output_queue.put(chunk)

        # Send end signal
        await self.audio_output_queue.put(None)

    @staticmethod
    def decode_audio(message):
        """Decode WebSocket message to audio array."""

        # Assuming PCM16 format
        return np.frombuffer(message, dtype=np.int16)

    @staticmethod
    def encode_audio(audio_array):
        """Encode audio array to WebSocket message."""

        # Assuming PCM16 format
        return audio_array.tobytes()

    @staticmethod
    def split_into_sentences(text):
        """Split text into sentences for streaming."""

        # Simple split on punctuation
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s for s in sentences if s]

    @staticmethod
    def chunk_audio(audio, chunk_size):
        """Chunk audio into smaller pieces."""

        chunk_length = int(chunk_size * 24000)  # 24kHz sample rate
        for i in range(0, len(audio), chunk_length):
            yield audio[i:i + chunk_length]

# WebSocket route
@app.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket):
    agent = BidirectionalVoiceAgent()

    # Start pipeline
    pipeline_task = asyncio.create_task(agent.speech_pipeline())

    # Handle WebSocket
    await agent.websocket_endpoint(websocket)

    # Cleanup
    pipeline_task.cancel()
```

## Latency Budget

### Target: <300ms End-to-End

```
Component Breakdown:
├─ VAD Processing: 50ms
├─ STT Transcription: 100ms
├─ LLM Generation: 50ms (first token)
├─ TTS Generation: 100ms (first audio chunk)
└─ Network: 0ms (local)

Total: 300ms
```

### Optimization Strategies

1. **VAD:** Use Silero VAD with low latency mode
2. **STT:** Use streaming STT with chunked processing
3. **LLM:** Use streaming generation, send tokens as they arrive
4. **TTS:** Use Pocket TTS with voice state caching
5. **Network:** Use WebSocket with local server (zero latency)

### Measuring Latency

```python
import time

class LatencyTracker:
    """Track latency through the pipeline."""

    def __init__(self):
        self.metrics = {
            "vad": [],
            "stt": [],
            "llm": [],
            "tts": [],
            "total": []
        }

    def track_vad(self, start_time):
        self.metrics["vad"].append(time.time() - start_time)

    def track_stt(self, start_time):
        self.metrics["stt"].append(time.time() - start_time)

    def track_llm(self, start_time):
        self.metrics["llm"].append(time.time() - start_time)

    def track_tts(self, start_time):
        self.metrics["tts"].append(time.time() - start_time)

    def get_percentiles(self):
        """Get p50, p95, p99 latencies."""

        stats = {}
        for component, timings in self.metrics.items():
            if timings:
                timings_sorted = sorted(timings)
                stats[component] = {
                    "p50": timings_sorted[len(timings_sorted) // 2],
                    "p95": timings_sorted[int(len(timings_sorted) * 0.95)],
                    "p99": timings_sorted[int(len(timings_sorted) * 0.99)],
                }
        return stats
```

## Best Practices

### 1. Always Use VAD
```python
# Good
is_speech = vad.process(audio_chunk)
if is_speech:
    buffer.extend(audio_chunk)

# Bad
buffer.extend(audio_chunk)  # Buffers everything, including silence
```

### 2. Stream Everything Possible
```python
# Good
async for token in llm.generate_stream(text):
    async for audio_chunk in tts.generate_stream(token):
        await websocket.send(audio_chunk)

# Bad
full_text = await llm.generate(text)
full_audio = tts.generate_audio(full_text)
await websocket.send(full_audio)
```

### 3. Use Appropriate Buffer Sizes
```python
# Good: 500ms chunks
chunk_size = 0.5
chunk_length = int(chunk_size * sample_rate)

# Bad: Too small (overhead)
chunk_size = 0.01  # 10ms

# Bad: Too large (latency)
chunk_size = 5.0  # 5 seconds
```

### 4. Handle Interruptions Gracefully
```python
# Always check for interruption
if self.interrupted:
    # Stop processing
    return

# Allow interruption points
for sentence in sentences:
    if self.interrupted:
        break
    # Process sentence
```

### 5. Monitor Memory Usage
```python
import psutil

def check_memory():
    """Check memory usage."""

    process = psutil.Process()
    memory_info = process.memory_info()

    print(f"Memory: {memory_info.rss / 1024 / 1024:.2f} MB")

    if memory_info.rss > 8 * 1024 * 1024 * 1024:  # 8GB
        print("WARNING: High memory usage!")
```

## Troubleshooting

### Issue: High Latency

**Symptoms:** >500ms response time

**Solutions:**
1. Check VAD is working (not buffering silence)
2. Reduce buffer sizes
3. Use streaming instead of batch processing
4. Profile each component to find bottleneck

### Issue: Memory Growth

**Symptoms:** RAM usage increases over time

**Solutions:**
1. Reload TTS model periodically
2. Clear audio buffers after processing
3. Use process isolation
4. Monitor memory usage

### Issue: Interruptions Don't Work

**Symptoms:** Can't interrupt AI speech

**Solutions:**
1. Check VAD is running while AI speaks (full duplex)
2. Reduce audio chunk sizes for faster interruption
3. Use asyncio.Lock for state management
4. Test interruption during speech, not after

### Issue: Poor Turn-Taking

**Symptoms:** Awkward pauses or premature responses

**Solutions:**
1. Adjust VAD silence threshold (try 500ms-1000ms)
2. Use prosody detection for better turn detection
3. Add minimum speech duration before checking for turn end
4. Use fixed buffer as fallback

## References

- [Pocket TTS GitHub](https://github.com/kyutai-labs/pocket-tts)
- [Pocket TTS HuggingFace](https://huggingface.co/kyutai/pocket-tts)
- [Kyutai STT 2.6B](https://huggingface.co/kyutai/stt-2.6b-en)
- [Silero VAD](https://github.com/snakers4/silero-vad)
- [Moshi Paper](https://arxiv.org/abs/2410.00037)
- [LiveKit Real-Time Voice](https://livekit.io/)
- [FastAPI WebSocket](https://fastapi.tiangolo.com/advanced/websockets/)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run voice agent
python -m agentx.voice.server

# Connect with WebSocket client
# ws://localhost:8000/ws/voice
```

---

**Key Takeaway:** The main challenge with real-time voice is not the models (Pocket TTS is fast enough), it's the **async architecture** for handling unpredictable speech timing, interruptions, and turn-taking. Focus on VAD accuracy, streaming pipelines, and graceful interruption handling.

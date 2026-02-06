/**
 * Audio Processor for capturing and encoding 16kHz PCM audio.
 *
 * Handles:
 * - Real-time audio capture from microphone
 * - Resampling to 16kHz (Whisper requirement)
 * - 16-bit PCM encoding
 * - Chunk-based streaming for variable recording lengths
 */

export interface AudioProcessorOptions {
  targetSampleRate: number; // 16000 for Whisper
  channels: number; // 1 for mono
  chunkDurationMs: number; // Chunk size in milliseconds
}

export interface AudioProcessorCallbacks {
  onChunk: (pcmBase64: string) => void;
  onError: (error: Error) => void;
}

/**
 * Audio processor for 16kHz PCM capture.
 *
 * Uses Web Audio API to capture, resample, and encode audio.
 */
export class AudioProcessor {
  private audioContext: AudioContext | null = null;
  private mediaStream: MediaStream | null = null;
  private source: MediaStreamAudioSourceNode | null = null;
  private processor: ScriptProcessorNode | null = null;
  private isRecording = false;

  private readonly options: AudioProcessorOptions;
  private readonly callbacks: AudioProcessorCallbacks;

  // Resampling buffer for sample rate conversion
  private resampleBuffer: Float32Array = new Float32Array(0);
  private resampleOffset = 0;

  // Output buffer for accumulating samples
  private outputBuffer: Int16Array = new Int16Array(0);
  private outputOffset = 0;

  // Chunk size in samples
  private readonly chunkSize: number;

  constructor(options: AudioProcessorOptions, callbacks: AudioProcessorCallbacks) {
    this.options = {
      targetSampleRate: options.targetSampleRate || 16000,
      channels: options.channels || 1,
      chunkDurationMs: options.chunkDurationMs || 200, // 200ms chunks
    };
    this.callbacks = callbacks;

    // Calculate chunk size in samples
    this.chunkSize = Math.floor(
      (this.options.targetSampleRate * this.options.chunkDurationMs) / 1000
    );
  }

  /**
   * Start recording audio.
   */
  async start(): Promise<void> {
    if (this.isRecording) {
      throw new Error('Already recording');
    }

    try {
      // Get user media
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: this.options.channels,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      // Create audio context
      this.audioContext = new AudioContext({
        sampleRate: 48000, // Use high quality for input
      });

      // Create source
      this.source = this.audioContext.createMediaStreamSource(this.mediaStream);

      // Create script processor for real-time processing
      const bufferSize = 4096; // 4096 samples
      this.processor = this.audioContext.createScriptProcessor(
        bufferSize,
        this.options.channels,
        this.options.channels
      );

      this.processor.onaudioprocess = (event) => {
        this.processAudioBuffer(event.inputBuffer);
      };

      // Connect the graph
      this.source.connect(this.processor);
      this.processor.connect(this.audioContext.destination);

      this.isRecording = true;
      console.log('[AudioProcessor] Recording started');
    } catch (error) {
      this.callbacks.onError(error as Error);
      throw error;
    }
  }

  /**
   * Stop recording and send final chunk.
   */
  stop(): void {
    if (!this.isRecording) {
      return;
    }

    this.isRecording = false;

    // Send any remaining data
    if (this.outputOffset > 0) {
      const finalChunk = this.outputBuffer.slice(0, this.outputOffset);
      this.sendChunk(finalChunk);
    }

    // Cleanup
    this.processor?.disconnect();
    this.source?.disconnect();
    this.mediaStream?.getTracks().forEach((track) => track.stop());
    this.audioContext?.close();

    // Reset buffers
    this.resampleBuffer = new Float32Array(0);
    this.outputBuffer = new Int16Array(0);
    this.resampleOffset = 0;
    this.outputOffset = 0;

    console.log('[AudioProcessor] Recording stopped');
  }

  /**
   * Process audio buffer from script processor.
   */
  private processAudioBuffer(buffer: AudioBuffer): void {
    if (!this.isRecording) return;

    const inputData = buffer.getChannelData(0); // Mono
    const inputSampleRate = buffer.sampleRate;
    const targetSampleRate = this.options.targetSampleRate;

    // If sample rates match, process directly
    if (inputSampleRate === targetSampleRate) {
      this.processSamples(inputData);
    } else {
      // Resample using linear interpolation
      const resampled = this.resample(inputData, inputSampleRate, targetSampleRate);
      this.processSamples(resampled);
    }
  }

  /**
   * Resample audio using linear interpolation.
   */
  private resample(
    input: Float32Array,
    inputSampleRate: number,
    targetSampleRate: number
  ): Float32Array {
    const ratio = inputSampleRate / targetSampleRate;
    const outputLength = Math.ceil(input.length / ratio);
    const output = new Float32Array(outputLength);

    for (let i = 0; i < outputLength; i++) {
      const srcIndex = i * ratio;
      const srcIndexInt = Math.floor(srcIndex);
      const srcIndexFrac = srcIndex - srcIndexInt;

      if (srcIndexInt + 1 < input.length) {
        // Linear interpolation
        output[i] =
          input[srcIndexInt] * (1 - srcIndexFrac) +
          input[srcIndexInt + 1] * srcIndexFrac;
      } else {
        output[i] = input[srcIndexInt] || 0;
      }
    }

    return output;
  }

  /**
   * Process samples and send chunks.
   */
  private processSamples(samples: Float32Array): void {
    // Convert float32 to int16 PCM
    const pcm = this.floatToInt16(samples);

    // Append to output buffer
    const newBuffer = new Int16Array(this.outputBuffer.length + pcm.length);
    newBuffer.set(this.outputBuffer);
    newBuffer.set(pcm, this.outputBuffer.length);
    this.outputBuffer = newBuffer;

    // Send complete chunks
    while (this.outputOffset + this.chunkSize <= this.outputBuffer.length) {
      const chunk = this.outputBuffer.slice(this.outputOffset, this.outputOffset + this.chunkSize);
      this.sendChunk(chunk);
      this.outputOffset += this.chunkSize;
    }

    // Shift buffer to remove sent data
    if (this.outputOffset > 0) {
      const remaining = this.outputBuffer.length - this.outputOffset;
      const newBuffer = new Int16Array(remaining);
      newBuffer.set(this.outputBuffer.slice(this.outputOffset));
      this.outputBuffer = newBuffer;
      this.outputOffset = 0;
    }
  }

  /**
   * Convert float32 audio to int16 PCM.
   */
  private floatToInt16(float32: Float32Array): Int16Array {
    const int16 = new Int16Array(float32.length);
    for (let i = 0; i < float32.length; i++) {
      const s = Math.max(-1, Math.min(1, float32[i]));
      int16[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
    }
    return int16;
  }

  /**
   * Send chunk as base64 encoded PCM.
   */
  private sendChunk(chunk: Int16Array): void {
    // Convert to bytes
    const bytes = new Uint8Array(chunk.buffer);

    // Encode as base64
    const binary = Array.from(bytes, (byte) => String.fromCharCode(byte)).join('');
    const base64 = btoa(binary);

    this.callbacks.onChunk(base64);
  }

  /**
   * Check if currently recording.
   */
  get recording(): boolean {
    return this.isRecording;
  }
}

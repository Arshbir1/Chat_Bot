import sounddevice as sd
import numpy as np
import time
import wave
from scipy import signal

def record_audio(filename, max_duration=30, silence_threshold=500, silence_duration=2.0):
    """
    Record audio with voice activity detection and noise reduction
    
    Args:
        filename: Output audio file path
        max_duration: Maximum recording duration in seconds
        silence_threshold: Amplitude threshold to detect silence
        silence_duration: Duration of silence (in seconds) to stop recording
    """
    # Higher quality audio settings
    CHUNK = 1024
    CHANNELS = 1
    RATE = 44100  # Increased from 16000 for better quality
    SAMPLE_WIDTH = 2  # 2 bytes for int16 (16-bit audio)

    print("Listening... (speak now)")

    # For silence detection
    silent_chunks = 0
    silent_threshold = silence_duration * (RATE / CHUNK)

    frames = []
    recording_started = False
    start_time = time.time()

    try:
        # Initialize a stream for continuous recording
        stream = sd.InputStream(samplerate=RATE, channels=CHANNELS, dtype='int16', blocksize=CHUNK)
        stream.start()

        while True:
            # Check if max duration exceeded
            if time.time() - start_time > max_duration:
                print("Maximum recording duration reached")
                break

            # Read audio data (equivalent to CHUNK frames)
            data, overflowed = stream.read(CHUNK)
            if overflowed:
                print("Warning: Audio buffer overflowed")
                continue

            frames.append(data)

            # Calculate RMS (root mean square) for voice activity detection
            rms = np.sqrt(np.mean(data**2))

            # Voice activity detection
            if not recording_started and rms > silence_threshold:
                print("Recording started...")
                recording_started = True

            # Silence detection to end recording
            if recording_started:
                if rms < silence_threshold:
                    silent_chunks += 1
                    if silent_chunks > silent_threshold:
                        print("Silence detected, stopping recording")
                        break
                else:
                    silent_chunks = 0

    except KeyboardInterrupt:
        print("Recording stopped manually")
    finally:
        stream.stop()
        stream.close()

    if not recording_started or len(frames) < RATE // CHUNK:  # Less than 1 second of audio
        print("No speech detected, recording cancelled")
        return False

    # Combine frames into a single NumPy array
    audio_data = np.concatenate(frames, axis=0)

    # Apply preprocessing to improve audio quality
    processed_audio = preprocess_audio(audio_data, RATE)

    # Save the processed audio to a WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(RATE)
        wf.writeframes(processed_audio)

    print(f"Recording finished and saved to {filename}")
    return True

def preprocess_audio(audio_data, sample_rate):
    """Apply audio preprocessing to improve speech recognition quality"""
    # Normalize audio
    audio = audio_data / np.max(np.abs(audio_data))

    # Apply noise reduction using a simple high-pass filter
    # This helps remove low-frequency background noise
    b, a = signal.butter(5, 80/(sample_rate/2), 'highpass')
    filtered_audio = signal.filtfilt(b, a, audio)

    # Apply a gentle low-pass filter to reduce high-frequency noise
    b, a = signal.butter(5, 8000/(sample_rate/2), 'lowpass')
    filtered_audio = signal.filtfilt(b, a, filtered_audio)

    # Convert back to the original scale (int16)
    filtered_audio = (filtered_audio * 32767).astype(np.int16)

    # Convert to bytes for saving to WAV file
    return filtered_audio.tobytes()

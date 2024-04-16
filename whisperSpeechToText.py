import whisper
import sounddevice as sd
import numpy as np
import scipy.signal
import keyboard

frames = []  # Define frames as a list to hold audio data chunks

def record_audio_with_spacebar(sample_rate=44100, channels=1):
    global frames
    frames.clear()  # Clear any previous recordings

    def callback(indata, frame_count, time_info, status):
        frames.append(indata.copy())  # Append the current frame of audio data to the frames list

    with sd.InputStream(samplerate=sample_rate, channels=channels, callback=callback):
        print("Press and hold the spacebar to start recording...")
        keyboard.wait('space')  # Wait until space bar is pressed to start recording
        print("Recording... Release the spacebar to stop.")
        while keyboard.is_pressed('space'):
            pass  # Keep recording while spacebar is pressed
        print("Recording stopped.")

    return np.concatenate(frames, axis=0)  # Return a single array concatenated from the list of frames

def transcribe_with_whisper(audio):
    # Flatten the audio to ensure it's 1D
    audio = audio.flatten()
    audio = audio.astype(np.float32)  # Convert to float32 as required by Whisper
    
    print(f"Transcribing audio with shape: {audio.shape}")  # Should now be 1D
    print(f"Max sample value: {np.max(audio)}")  # Diagnostic print
    print(f"Min sample value: {np.min(audio)}")  # Diagnostic print

    model = whisper.load_model("base")
    result = model.transcribe(audio)
    print("Transcribed Text:", result['text'])


if __name__ == "__main__":
    # print(sd.query_devices())

    sd.default.device = 2  # Set the desired input device here
    sample_rate = 44100  # Default sample rate for recording
    audio = record_audio_with_spacebar(sample_rate=sample_rate)
    if audio.size > 0:  # Check if audio contains data
        # Resample to 16kHz for Whisper if needed
        if sample_rate != 16000:
            audio = scipy.signal.resample_poly(audio, 16000, sample_rate)
        transcribed_text = transcribe_with_whisper(audio)
    # After recording, add these lines:
    print(f"Recorded audio length in samples: {len(audio)}")
    print(f"Audio array shape: {audio.shape}")
    if np.any(np.isnan(audio)) or np.any(np.isinf(audio)):
        print("Audio contains NaNs or infinite values.")
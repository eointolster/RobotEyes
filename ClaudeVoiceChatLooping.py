#claude-3-haiku-20240307
import whisper
import sounddevice as sd
import numpy as np
import scipy.signal
import keyboard
import anthropic
import requests
import pygame
import pprint

# Initialize the Anthropics API client with your API key
claude_api_key = "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"  # Replace with your actual API key for Anthropic
client = anthropic.Anthropic(api_key=claude_api_key)

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
    audio = audio.flatten()
    audio = audio.astype(np.float32)  # Convert to float32 as required by Whisper
    model = whisper.load_model("base")
    result = model.transcribe(audio)
    return result['text']

def send_to_claude_api(text, conversation_history):
    # Directly append the new user message here, ensuring it's not duplicated
    user_message = {
        "role": "user",
        "content": [{"type": "text", "text": text}]
    }
    conversation_history.append(user_message)

    try:
        response = client.messages.create(
            model= "claude-3-haiku-20240307",#"claude-3-haiku-20240307",#"claude-3-opus-20240229",
            max_tokens=400,
            temperature=0,
            system="respond briefly to the user",
            messages=conversation_history
        )
        # Assuming the successful response includes a text attribute directly
        # This might need adjustment based on the actual response structure
        claude_response_text = response.content  # Adjust if necessary
        
        # Append Claude's response to the history
        claude_message = {
            "role": "assistant",
            "content": claude_response_text  # Ensure this matches expected format
        }
        conversation_history.append(claude_message)

        return claude_response_text, conversation_history
    except Exception as e:
        print(f"Error in sending message to Claude API: {e}")
        return None, conversation_history

def convert_text_to_speech(text):
    print(f"Converting text to speech: {text}")
    url = "https://api.elevenlabs.io/v1/text-to-speech/txBahrIQnLBRd00RGCN5/stream"
    querystring = {"optimize_streaming_latency":"1"}
    headers = {
        "xi-api-key": "5c924f93c3f3a228a6da75ab00f73bc2",
        "Content-Type": "application/json"
    }
    payload = {
        "voice_settings": {
            "stability": .7,
            "similarity_boost": 1
        },
        "text": text,
        "model_id": "eleven_multilingual_v2"
    }
    response = requests.post(url, json=payload, headers=headers)
   
    if response.status_code == 200:
        with open("output.mp3", "wb") as f:
            f.write(response.content)
        print("Text-to-speech conversion completed successfully. Audio saved as output.mp3.")
        return "output.mp3"
    else:
        print(f"Error converting text to speech: {response.text}")
        return None

def play_audio(file_path):
    print(f"Playing audio file: {file_path}")
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()
        print(f"Audio file played successfully: {file_path}")
    except FileNotFoundError:
        print(f"Audio file not found: {file_path}")
    except Exception as e:
        print(f"Error playing audio file: {str(e)}")

def main():
    sd.default.device = 2  # Set the desired input device here
    sample_rate = 44100
    conversation_history = []  # Initialize conversation history
    while True:
        audio = record_audio_with_spacebar(sample_rate=sample_rate)
        if audio.size > 0:
            if sample_rate != 16000:
                audio = scipy.signal.resample_poly(audio, 16000, sample_rate)
            transcribed_text = transcribe_with_whisper(audio)
            print(f"Transcribed Text: {transcribed_text}")
            
            claude_response, conversation_history = send_to_claude_api(transcribed_text, conversation_history)
            if claude_response:
                # Assuming claude_response is a list of ContentBlock objects
                # Extract the text from each ContentBlock and join them into a single string, if there are multiple blocks
                response_text = " ".join([block.text for block in claude_response if hasattr(block, 'text')])
                print(f"Claude's Response: {response_text}")
                audio_file = convert_text_to_speech(response_text)  # Pass the extracted text
                if audio_file:
                    play_audio(audio_file)

            if transcribed_text.lower() == "goodbye":
                break

if __name__ == "__main__":
    main()



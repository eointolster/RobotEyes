import pyaudio
import speech_recognition as sr
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import keyboard
import threading
from threading import Lock

# Create a lock
mic_lock = Lock()

class ElevenLabsTTSTool:
    def __init__(self, api_key):
        self.api_key = api_key
       
    def use_tool(self, text):
        print(f"Converting text to speech: {text}")
        try:
            url = "https://api.elevenlabs.io/v1/text-to-speech/txBahrIQnLBRd00RGCN5/stream"
            querystring = {"optimize_streaming_latency": "1"}
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "voice_settings": {
                    "stability": .4,
                    "similarity_boost": 1
                },
                "text": text,
                "model_id": "eleven_multilingual_v2"
            }
            response = requests.post(url, json=payload, headers=headers)
           
            if response.status_code == 200:
                audio_data = io.BytesIO(response.content)
                return audio_data
            else:
                raise Exception(f"Error converting text to speech: {response.text}")
        except Exception as e:
            raise Exception(f"Error converting text to speech: {str(e)}")

def send_to_claude_api(user_input, conversation_history):
    # Set up the API endpoint and headers
    api_endpoint = "https://api.anthropic.com/v1/complete"
    api_key = "yourapiKey"  # Replace with your actual Claude API key
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
   
    # Include conversation history in the prompt
    history_prompt = ""
    if conversation_history:
        history_prompt = "\n".join(conversation_history[-5:])  # Limit history to last 5 interactions
   
    # Prepare the API request payload
    payload = {
        "prompt": f"{history_prompt}\nUser: {user_input}\nAssistant: ",
        "model": "claude-3-haiku-20240307",
        "max_tokens_to_sample": 500,
        "stop_sequences": ["\n\nUser:"],
        "temperature": 0.7
    }
   
    try:
        # Send the API request
        response = requests.post(api_endpoint, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        # Extract the generated response from the API response
        api_response = response.json()
        generated_response = api_response["completion"]
        return generated_response.strip()
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while making the API request: {e}")
        return "Sorry, an error occurred while processing your request."

def update_image(response_text):
    image = Image.open("background.png")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 24)
    draw.rectangle((50, 400, image.width - 50, image.height - 50), fill=(0, 0, 0))  # Clear previous text
    draw.text((50, 400), response_text, font=font, fill=(255, 255, 255))
    image.show()

# Set up speech recognition
recognizer = sr.Recognizer()
mic_index = 2  # Specify the index of your microphone (for Logi C270 HD Webcam)

# Set up ElevenLabs TTS
elevenlabs_api_key = "yourapiKey"  # Replace with your actual ElevenLabs API key
elevenlabs_tts_tool = ElevenLabsTTSTool(elevenlabs_api_key)

# Set up conversation history
conversation_history = []

def process_audio(audio_data):
    with mic_lock:
        # Convert speech to text
        try:
            user_input = recognizer.recognize_sphinx(audio_data)
            print("User:", user_input)
        except sr.UnknownValueError:
            print("Speech recognition could not understand audio")
            return
        except sr.RequestError as e:
            print("Could not request results from speech recognition service; {0}".format(e))
            return
       
        # Send user input to Claude API
        conversation_history.append(user_input)
        response = send_to_claude_api(user_input, conversation_history)
        conversation_history.append(response)
       
        # Convert Claude response to speech
        try:
            audio_data = elevenlabs_tts_tool.use_tool(response)
            # Play the audio using PyAudio
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(2), channels=1, rate=44100, output=True)
            stream.write(audio_data.getvalue())
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception as e:
            print(f"Error occurred while converting text to speech: {str(e)}")
       
        # Display response text on PNG image
        update_image(response)

def on_space_press(event):
    print("Spacebar pressed. Starting recording...")
    with sr.Microphone(device_index=mic_index) as source:
        print("Adjusting for ambient noise, please wait...")
        recognizer.adjust_for_ambient_noise(source)
       
        print("Listening for speech. Speak now!")
        audio_data = recognizer.listen(source)
       
        print("Recognizing speech...")
        # Start a new thread to process the audio
        threading.Thread(target=process_audio, args=(audio_data,)).start()

def on_esc_press(event):
    print("Esc key pressed. Exiting...")
    exit()

# Register the spacebar press and Esc key press events
keyboard.on_press_key(' ', on_space_press)
keyboard.on_press_key('esc', on_esc_press)

print("Press the spacebar to start recording. Release the spacebar to stop recording.")
print("Press the Esc key to exit the program.")

# Keep the program running
while True:
    pass


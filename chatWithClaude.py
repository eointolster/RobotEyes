import speech_recognition as sr
import keyboard
import os
import anthropic

# Function to recognize speech
def recognize_speech():
    recognizer = sr.Recognizer()
    mic_index = 2  # Adjust based on your microphone
    with sr.Microphone(device_index=mic_index) as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for speech. Speak now!")
        audio_data = recognizer.listen(source)
        try:
            text = recognizer.recognize_sphinx(audio_data)
            print(f"Recognized text: {text}")
            return text
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Sphinx error; {e}")

# Function to send text to Claude API and get response
def send_to_claude(text):
    claude_api_key = os.getenv("ANTHROPIC_API_KEY")
    client = anthropic.Client(api_key=claude_api_key)
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": text}
        ]
    )
    print("Claude's response:", message)

# Main loop waiting for spacebar press
print("Press the spacebar to start voice recognition.")
while True:
    try:
        if keyboard.is_pressed('space'):
            text = recognize_speech()
            if text:
                send_to_claude(text)
            print("Press the spacebar to start voice recognition again.")
    except Exception as e:
        print("Error:", e)

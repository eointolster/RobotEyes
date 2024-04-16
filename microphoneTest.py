import speech_recognition as sr

# Initialize recognizer class (for recognizing the speech)
recognizer = sr.Recognizer()

# Specify the index of your microphone (for Logi C270 HD Webcam)
mic_index = 2

# Use the microphone with the specified index
with sr.Microphone(device_index=mic_index) as source:
    print("Adjusting for ambient noise, please wait...")
    recognizer.adjust_for_ambient_noise(source)
    
    print("Listening for speech. Speak now!")
    audio_data = recognizer.listen(source)
    
    print("Recognizing speech...")
    try:
        # Recognize speech using Sphinx
        text = recognizer.recognize_sphinx(audio_data)
        print(f"Recognized text: {text}")
    except sr.UnknownValueError:
        print("Sphinx could not understand the audio")
    except sr.RequestError as e:
        print(f"Could not request results from Sphinx service; {e}")
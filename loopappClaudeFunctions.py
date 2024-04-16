import os
import sys
from pydub import AudioSegment
from tool_use_package.tools.base_tool import BaseTool
from tool_use_package.tool_user import ToolUser
from tool_use_package.tools.search.brave_search_tool import BraveSearchTool
import anthropic
import shutil
import subprocess
from pydub import AudioSegment
from pydub.playback import play
import winsound
import numpy as np
import wave
import struct
from dotenv import load_dotenv
import requests
import datetime, zoneinfo
import pygame
import pretty_midi
import tempfile
import mido
import fluidsynth
from pytube import YouTube
from pydub import AudioSegment
import os

load_dotenv()
brave_api_key = os.getenv("BRAVE_API_KEY")
if brave_api_key is None:
    print("BRAVE_API_KEY environment variable not found.")
else:
    print("BRAVE_API_KEY is set.")
claude_api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Client(api_key=claude_api_key)
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
# Define the function to directly test the Brave API
def direct_api_test():
    # Retrieve the API key from environment variables
    brave_api_key = os.getenv("BRAVE_API_KEY")
    if brave_api_key is None:
        print("BRAVE_API_KEY environment variable not found.")
        return
   
    print("BRAVE_API_KEY is set. Proceeding with API test.")
   
    # Set up the headers with your API key
    headers = {"Accept": "application/json", "X-Subscription-Token": brave_api_key}
   
    # Make the API request
    response = requests.get("https://api.search.brave.com/res/v1/web/search", params={"q": "test"}, headers=headers)
   
    # Print out the response status code and JSON content
    print(response.status_code, response.json())
direct_api_test()
# Get the current working directory
current_dir = os.getcwd()
# 1. Define the Tools
class AdditionTool(BaseTool):
    """Adds together two numbers, a + b."""
    def use_tool(self, a, b):
        print(f"Adding {a} and {b}")
        return a+b
class FileWriteTool(BaseTool):
    """Writes content to a file."""
    def use_tool(self, file_path, content):
        # Modify the file path to be relative to the current directory
        file_path = os.path.join(current_dir, file_path)
        print(f"Writing to file: {file_path}")
        with open(file_path, 'w') as file:
            file.write(content)
        return f"Content written to file: {file_path}"
class FileReadTool(BaseTool):
    """Reads content from a file."""
    def use_tool(self, file_path):
        # Modify the file path to be relative to the current directory
        file_path = os.path.join(current_dir, file_path)
        print(f"Reading from file: {file_path}")
        with open(file_path, 'r') as file:
            content = file.read()
        return content
class FileCopyTool(BaseTool):
    """Copies a file or folder to another location."""
    def use_tool(self, source_path, destination_path):
        # Modify the source and destination paths to be relative to the current directory
        source_path = os.path.join(current_dir, source_path)
        destination_path = os.path.join(current_dir, destination_path)
        print(f"Copying from {source_path} to {destination_path}")
        shutil.copy(source_path, destination_path)
        return f"File/folder copied from {source_path} to {destination_path}"
class MinicondaStartTool(BaseTool):
    """Starts a Miniconda application."""
    def use_tool(self, app_name):
        print(f"Starting Miniconda application: {app_name}")
        try:
            miniconda_path = r"C:\Users\eoint\miniconda3"
            activate_script = os.path.join(miniconda_path, "Scripts", "activate.bat")
            subprocess.run([activate_script, miniconda_path], shell=True, check=True)
            subprocess.run([app_name], shell=True, check=True)
            return f"Miniconda application '{app_name}' started successfully."
        except subprocess.CalledProcessError as e:
            return f"Error starting Miniconda application '{app_name}': {str(e)}"      
class StartCMDTool(BaseTool):
    """Starts a new Command Prompt (cmd.exe) window."""
    def use_tool(self):
        print("Starting a new Command Prompt window...")
        subprocess.Popen('cmd.exe', creationflags=subprocess.CREATE_NEW_CONSOLE)
        return "A new Command Prompt window has been started." 
class CMDInteractionTool(BaseTool):
    """Interacts with a Command Prompt (cmd.exe) window by writing commands and reading the output."""
    def use_tool(self, command):
        print(f"Running command in Command Prompt: {command}")
        try:
            process = subprocess.Popen('cmd.exe', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            stdout, stderr = process.communicate(command + '\n')
            if stderr:
                return f"Error executing command: {stderr}"
            else:
                return stdout.strip()
        except Exception as e:
            return f"Error interacting with Command Prompt: {str(e)}"    
class CreateAudioFileTool(BaseTool):
    """Creates an audio file (.wav or .mp3) with the specified content."""
    def use_tool(self, file_path, content_file_path, format="wav"):
        print(f"Creating audio file: {file_path}")
       
        try:
            # Create an AudioSegment from the content file path
            audio_segment = AudioSegment.from_file(content_file_path, format=format)
           
            # Export the AudioSegment to the specified file path
            audio_segment.export(file_path, format=format)
           
            return f"Audio file created: {file_path}"
        except FileNotFoundError as e:
            error_message = f"Error creating audio file: Content file not found: {content_file_path}"
            print(error_message)
            return error_message
        except Exception as e:
            error_message = f"Error creating audio file: {str(e)}"
            print(error_message)
            return error_message   
class PlayAudioFileTool(BaseTool):
    """Plays an audio file (.wav or .mp3)."""
    def use_tool(self, file_path):
        print(f"Playing audio file: {file_path}")
       
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.quit()
           
            return f"Audio file played successfully: {file_path}"
        except FileNotFoundError:
            return f"Audio file not found: {file_path}"
        except Exception as e:
            return f"Error playing audio file: {str(e)}"
class PythonFileReviewTool(BaseTool):
    """Reviews and modifies a Python file for issues."""
    def use_tool(self, file_path):
        # Modify the file path to be relative to the current directory
        file_path = os.path.join(current_dir, file_path)
        print(f"Reviewing Python file: {file_path}")
       
        try:
            with open(file_path, 'r') as file:
                content = file.read()
           
            # Perform review and modifications here
            modified_content = self.review_and_modify(content)
           
            with open(file_path, 'w') as file:
                file.write(modified_content)
           
            return f"Python file reviewed and modified: {file_path}"
        except FileNotFoundError:
            return f"Python file not found: {file_path}"
        except Exception as e:
            return f"Error reviewing Python file: {str(e)}"
   
    def review_and_modify(self, content):
        # Implement your review and modification logic here
        # For example, you can check for specific issues or patterns and modify the content accordingly
        # This is just a placeholder example
        modified_content = content.replace('issue', 'fixed')
        return modified_content
class PipInstallTool(BaseTool):
    """Installs Python packages using pip."""
    def use_tool(self, package_name):
        print(f"Installing package: {package_name}")
        try:
            subprocess.run(["pip", "install", package_name], check=True)
            return f"Package '{package_name}' installed successfully."
        except subprocess.CalledProcessError as e:
            return f"Error installing package '{package_name}': {str(e)}"      
class SolutionVerificationTool(BaseTool):
    """Verifies if the solution requested by the user was successful."""
    def use_tool(self, user_request, solution_output):
        print(f"Verifying solution for user request: {user_request}")
       
        if "error" in solution_output.lower():
            suggestion = "It seems there was an error in the solution. Please review the Python script for any issues or missing dependencies. You may need to install additional packages using pip."
            return f"Solution verification failed. Suggestion: {suggestion}"
        else:
            return "Solution verification passed. The solution appears to be successful."
class CreateFolderTool(BaseTool):
    """Creates a new folder at the specified path."""
    def use_tool(self, folder_path):
        # Modify the folder path to be relative to the current directory
        folder_path = os.path.join(current_dir, folder_path)
        print(f"Creating folder: {folder_path}")
        os.makedirs(folder_path, exist_ok=True)
        return f"Folder created: {folder_path}"
class TimeOfDayTool(BaseTool):
    """Tool to get the current time of day."""
    def use_tool(self, time_zone):
        # Get the current time
        now = datetime.datetime.now()
        # Convert to the specified time zone
        tz = zoneinfo.ZoneInfo(time_zone)
        localized_time = now.astimezone(tz)
        return localized_time.strftime("%H:%M:%S")   
class ElevenLabsTTSTool(BaseTool):
    """Converts text to speech using ElevenLabs API."""
    def use_tool(self, text):
        print(f"Converting text to speech: {text}")
        try:                                                    
            url = "https://api.elevenlabs.io/v1/text-to-speech/txBahrIQnLBRd00RGCN5/stream"
            querystring = {"optimize_streaming_latency":"1"}
            headers = {
                "xi-api-key": "yourapiKey",
                "Content-Type": "application/json"
            }
            payload = {
                "voice_settings": {
                    "stability": .3,
                    "similarity_boost": 1
                },
                "text": text,
                "model_id": "eleven_multilingual_v1"
            }
            response = requests.request("POST", url, json=payload, headers=headers)
           
            if response.status_code == 200:
                with open("output.mp3", "wb") as f:
                    f.write(response.content)
                return "Text-to-speech conversion completed successfully. Audio saved as output.mp3."
            else:
                return f"Error converting text to speech: {response.text}"
        except Exception as e:
            return f"Error converting text to speech: {str(e)}"
class PianoMusicGenerationTool(BaseTool):
    """Generates piano music based on user-specified notes and durations."""
    def use_tool(self, file_path, tempo=120, output_file_path='generated_piano_music.mp3'):
        print(f"Generating piano music from file: {file_path}")
       
        # Read the content of the file
        with open(file_path, 'r') as file:
            content = file.read()
       
        # Parse the notes and durations from the file content
        notes = []
        durations = []
        for line in content.split('\n'):
            if line.startswith('Notes:'):
                notes = [note.strip() for note in line.split(':')[1].split(',')]
            elif line.startswith('Durations:'):
                durations = [float(duration.strip()) for duration in line.split(':')[1].split(',')]
       
        # Create an empty audio segment
        audio_segment = AudioSegment.silent(duration=0)
       
        # Generate audio for each note and duration
        for note_name, duration in zip(notes, durations):
            # Get the frequency of the note
            frequency = self.note_to_frequency(note_name)
           
            # Generate a sine wave for the note
            sine_wave = Sine(frequency).to_audio_segment(duration=duration * 1000)
           
            # Append the sine wave to the audio segment
            audio_segment += sine_wave
       
        # Export the audio segment as an MP3 file
        audio_segment.export(output_file_path, format="mp3")
       
        # Play the MP3 file using pygame
        pygame.mixer.init()
        pygame.mixer.music.load(output_file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()
       
        return f"Piano music generated from {file_path}, saved as {output_file_path}, and played."
   
    def note_to_frequency(self, note):
        # Implement the logic to convert a note name to its corresponding frequency
        # You can use a dictionary or a formula to calculate the frequency based on the note name
        # For simplicity, let's assume we have a dictionary mapping note names to frequencies
        note_frequencies = {
            'C4': 261.63,
            'D4': 293.66,
            'E4': 329.63,
            'F4': 349.23,
            'G4': 392.00,
            'A4': 440.00,
            'B4': 493.88,
            'C5': 523.25
        }
        return note_frequencies.get(note, 0.0)    
class SongSearchAndPlayTool(BaseTool):
    """Searches for a song on YouTube, downloads the audio, and plays it."""
    def use_tool(self, song_name):
        print(f"Searching for song: {song_name}")
       
        try:
            # Search for the song on YouTube
            query = f"{song_name} audio"
            url = f"https://www.youtube.com/results?search_query={query}"
            response = requests.get(url)
            search_results = re.findall(r"watch\?v=(\S{11})", response.text)
            video_url = f"https://www.youtube.com/watch?v={search_results[0]}"
           
            # Download the audio from the YouTube video
            yt = YouTube(video_url)
            audio_stream = yt.streams.filter(only_audio=True).first()
            audio_file = audio_stream.download(filename="song.mp3")
           
            # Convert the audio file to WAV format
            audio = AudioSegment.from_file(audio_file, format="mp3")
            audio.export("song.wav", format="wav")
           
            # Play the audio file
            pygame.mixer.init()
            pygame.mixer.music.load("song.wav")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.quit()
           
            # Clean up the downloaded files
            os.remove("song.mp3")
            os.remove("song.wav")
           
            return f"Song '{song_name}' played successfully."
        except Exception as e:
            return f"Error playing song '{song_name}': {str(e)}"
        
# 2. Tool Descriptions
addition_tool_name = "perform_addition"
addition_tool_description = """Add one number (a) to another (b), returning a+b.
Use this tool WHENEVER you need to perform any addition calculation, as it will ensure your answer is precise."""
addition_tool_parameters = [
    {"name": "a", "type": "float", "description": "The first number in your addition equation."},
    {"name": "b", "type": "float", "description": "The second number in your addition equation."}
]
addition_tool = AdditionTool(addition_tool_name, addition_tool_description, addition_tool_parameters)
###########################################
search_tool_name = "search_brave"
search_tool_description = "The search engine will search using the Brave search engine for web pages similar to your query. It returns for each page its url and the full page content. Use this tool if you want to make web searches about a topic."
search_tool_parameters = [
    {"name": "query", "type": "str", "description": "The search query to enter into the Brave search engine."},
    {"name": "n_search_results_to_use", "type": "int", "description": "The number of search results to return, where each search result is a website page."}
]
search_tool = BraveSearchTool(
    name=search_tool_name,
    description=search_tool_description,
    parameters=search_tool_parameters,
    brave_api_key=os.environ["BRAVE_API_KEY"],
    truncate_to_n_tokens=5000
)
###########################################
file_write_tool_name = "file_write"
file_write_tool_description = """Writes content to a file.
Use this tool to create files or scripts as requested by the user."""
file_write_tool_parameters = [
    {"name": "file_path", "type": "str", "description": "The path of the file to write to."},
    {"name": "content", "type": "str", "description": "The content to write to the file."}
]
file_write_tool = FileWriteTool(file_write_tool_name, file_write_tool_description, file_write_tool_parameters)
###########################################
file_read_tool_name = "file_read"
file_read_tool_description = """Reads content from a file.
Use this tool to read files when needed to answer a question or provide information."""
file_read_tool_parameters = [
{"name": "file_path", "type": "str", "description": "The path of the file to read from."}
]
file_read_tool = FileReadTool(file_read_tool_name, file_read_tool_description, file_read_tool_parameters)
###########################################
create_folder_tool_name = "create_folder"
create_folder_tool_description = """Creates a new folder at the specified path.
Use this tool to create folders as requested by the user."""
create_folder_tool_parameters = [
    {"name": "folder_path", "type": "str", "description": "The path of the folder to create."}
]
create_folder_tool = CreateFolderTool(create_folder_tool_name, create_folder_tool_description, create_folder_tool_parameters)
###########################################
file_copy_tool_name = "file_copy"
file_copy_tool_description = """Copies a file or folder from a source path to a destination path.
Use this tool to copy files or folders to a different location."""
file_copy_tool_parameters = [
    {"name": "source_path", "type": "str", "description": "The path of the file or folder to copy."},
    {"name": "destination_path", "type": "str", "description": "The path where the file or folder should be copied to."}
]
file_copy_tool = FileCopyTool(file_copy_tool_name, file_copy_tool_description, file_copy_tool_parameters)
###########################################
miniconda_start_tool_name = "miniconda_start"
miniconda_start_tool_description = """Starts a Miniconda application.
Use this tool to start a Miniconda application by providing the application name."""
miniconda_start_tool_parameters = [
    {"name": "app_name", "type": "str", "description": "The name of the Miniconda application to start."}
]
miniconda_start_tool = MinicondaStartTool(miniconda_start_tool_name, miniconda_start_tool_description, miniconda_start_tool_parameters)
###########################################
start_cmd_tool_name = "start_cmd"
start_cmd_tool_description = """Starts a new Command Prompt (cmd.exe) window.
Use this tool to open a new Command Prompt window for running commands."""
start_cmd_tool_parameters = []
start_cmd_tool = StartCMDTool(start_cmd_tool_name, start_cmd_tool_description, start_cmd_tool_parameters)
###########################################
cmd_interaction_tool_name = "cmd_interaction"
cmd_interaction_tool_description = """Interacts with a Command Prompt (cmd.exe) window by writing commands and reading the output.
Use this tool to execute commands in a Command Prompt window and retrieve the output."""
cmd_interaction_tool_parameters = [
    {"name": "command", "type": "str", "description": "The command to execute in the Command Prompt window."}
]
cmd_interaction_tool = CMDInteractionTool(cmd_interaction_tool_name, cmd_interaction_tool_description, cmd_interaction_tool_parameters)
###########################################
create_audio_file_tool_name = "create_audio_file"
create_audio_file_tool_description = """Creates an audio file (.wav or .mp3) with the specified content.
Use this tool to create audio files as requested by the user."""
create_audio_file_tool_parameters = [
    {"name": "file_path", "type": "str", "description": "The path of the audio file to create."},
    {"name": "content_file_path", "type": "str", "description": "The path of the audio content file to use."},
    {"name": "format", "type": "str", "description": "The format of the audio file (default: 'wav')."}
]
create_audio_file_tool = CreateAudioFileTool(create_audio_file_tool_name, create_audio_file_tool_description, create_audio_file_tool_parameters)
###########################################
play_audio_file_tool_name = "play_audio_file"
play_audio_file_tool_description = """Plays an audio file (.wav or .mp3).
Use this tool to play audio files when requested by the user."""
play_audio_file_tool_parameters = [
    {"name": "file_path", "type": "str", "description": "The path of the audio file to play."}
]
play_audio_file_tool = PlayAudioFileTool(play_audio_file_tool_name, play_audio_file_tool_description, play_audio_file_tool_parameters)
###########################################
# Add the new tool to the tool descriptions
python_file_review_tool_name = "python_file_review"
python_file_review_tool_description = """Reviews and modifies a Python file for issues.
Use this tool to review and modify Python files after they have been created."""
python_file_review_tool_parameters = [
    {"name": "file_path", "type": "str", "description": "The path of the Python file to review and modify."}
]
python_file_review_tool = PythonFileReviewTool(python_file_review_tool_name, python_file_review_tool_description, python_file_review_tool_parameters)
###########################################
pip_install_tool_name = "pip_install"
pip_install_tool_description = """Installs Python packages using pip.
Use this tool to install any required Python packages."""
pip_install_tool_parameters = [
    {"name": "package_name", "type": "str", "description": "The name of the Python package to install."}
]
pip_install_tool = PipInstallTool(pip_install_tool_name, pip_install_tool_description, pip_install_tool_parameters)
###########################################
solution_verification_tool_name = "solution_verification"
solution_verification_tool_description = """Verifies if the solution requested by the user was successful.
Use this tool to check if the solution provided meets the user's request and suggest improvements if needed."""
solution_verification_tool_parameters = [
    {"name": "user_request", "type": "str", "description": "The original user request or query."},
    {"name": "solution_output", "type": "str", "description": "The output or response generated as the solution."}
]
solution_verification_tool = SolutionVerificationTool(solution_verification_tool_name, solution_verification_tool_description, solution_verification_tool_parameters)
###########################################
tool_name = "get_time_of_day"
tool_description = "Retrieve the current time of day in Hour-Minute-Second format for a specified time zone. Time zones should be written in standard formats such as UTC, US/Pacific, Europe/London."
tool_parameters = [
    {"name": "time_zone", "type": "str", "description": "The time zone to get the current time for, such as UTC, US/Pacific, Europe/London."}
]
time_of_day_tool = TimeOfDayTool(tool_name, tool_description, tool_parameters)
###########################################
elevenlabs_tts_tool_name = "elevenlabs_tts"
elevenlabs_tts_tool_description = """Converts text to speech using ElevenLabs API.
   Use this tool to generate audio output from given text."""
elevenlabs_tts_tool_parameters = [
    {"name": "text", "type": "str", "description": "The text to convert to speech."}
]
elevenlabs_tts_tool = ElevenLabsTTSTool(elevenlabs_tts_tool_name, elevenlabs_tts_tool_description, elevenlabs_tts_tool_parameters)
###########################################
piano_music_generation_tool_name = "piano_music_generation"
piano_music_generation_tool_description = """Generates piano music based on user-specified parameters.
Use this tool to create simple piano melodies."""
piano_music_generation_tool_parameters = [
    {"name": "file_path", "type": "str", "description": "The path to the file containing the notes and durations."},
    {"name": "tempo", "type": "int", "description": "The tempo of the music in beats per minute (default is 120)."},
    {"name": "output_file_path", "type": "str", "description": "The path to save the generated MIDI file (default is 'generated_piano_music.mid')."}
]
piano_music_generation_tool = PianoMusicGenerationTool(piano_music_generation_tool_name, piano_music_generation_tool_description, piano_music_generation_tool_parameters)
###########################################
song_search_and_play_tool_name = "song_search_and_play"
song_search_and_play_tool_description = """Searches for a song on YouTube, downloads the audio, and plays it.
Use this tool to play any song requested by the user."""
song_search_and_play_tool_parameters = [
    {"name": "song_name", "type": "str", "description": "The name of the song to search and play."}
]
song_search_and_play_tool = SongSearchAndPlayTool(song_search_and_play_tool_name, song_search_and_play_tool_description, song_search_and_play_tool_parameters)

#3. Assign Tools and Ask Claude
tool_user = ToolUser([addition_tool, file_write_tool, file_read_tool, create_folder_tool, file_copy_tool, start_cmd_tool, miniconda_start_tool, cmd_interaction_tool, create_audio_file_tool, play_audio_file_tool, python_file_review_tool, pip_install_tool, solution_verification_tool, search_tool, time_of_day_tool,elevenlabs_tts_tool,piano_music_generation_tool, song_search_and_play_tool]) #

while True:
    query = input("Enter your query (or 'exit' to quit): ")
    if query.lower() == 'exit':
        break
    
    messages = [
        {
            "role":"user",
            "content": query
        }
    ]
    try:
        response = tool_user.use_tools(messages, execution_mode="automatic")
        print(response)
       
        verification_result = tool_user.use_tools([
            {
                "role": "user",
                "content": f"Verify the solution for the user request: {query}"
            },
            {
                "role": "assistant",
                "content": response
            }
        ], execution_mode="automatic")
        print(verification_result)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

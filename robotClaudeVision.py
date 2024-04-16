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
class CSVReadTool(BaseTool):
    """Reads the latest description from the descriptions.csv file."""
    def use_tool(self):
        file_path = os.path.join(current_dir, "descriptions.csv")
        with open(file_path, 'r') as file:
            lines = file.readlines()
            if lines:
                latest_description = lines[-1].strip()
                return latest_description
            else:
                return "No descriptions found in the file." 
class ESPMotorControlTool(BaseTool):
    """Controls the motors connected to the Arduino ESP."""
    def use_tool(self, command):
        print(f"Sending command to ESP: {command}")
        try:
            url = f"http://192.168.0.208/{command}"
            response = requests.get(url)
            if response.status_code == 200:
                return f"Command '{command}' sent successfully to the ESP."
            else:
                return f"Error sending command to ESP: {response.text}"
        except Exception as e:
            return f"Error sending command to ESP: {str(e)}"

# 2. Tool Descriptions
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
csv_read_tool_name = "csv_read"
csv_read_tool_description = """Reads the latest description from the descriptions.csv file. Use this tool to get the current description seen by the camera."""
csv_read_tool = CSVReadTool(csv_read_tool_name, csv_read_tool_description, [])

tool_user = ToolUser([
    file_write_tool,
    file_read_tool,
    create_folder_tool,
    file_copy_tool,
    search_tool,
    time_of_day_tool,
    elevenlabs_tts_tool,
    csv_read_tool  # Add the CSVReadTool to the tool_user
])
###########################################
esp_motor_control_tool_name = "esp_motor_control"
esp_motor_control_tool_description = """Controls the motors connected to the Arduino ESP. Use this tool to send commands to rotate the motors based on the camera description."""
esp_motor_control_tool = ESPMotorControlTool(esp_motor_control_tool_name, esp_motor_control_tool_description, [])

tool_user = ToolUser([
    file_write_tool,
    file_read_tool,
    create_folder_tool,
    file_copy_tool,
    search_tool,
    time_of_day_tool,
    elevenlabs_tts_tool,
    csv_read_tool,
    esp_motor_control_tool  # Add the ESPMotorControlTool to the tool_user
])
############################################

#3. Assign Tools and Ask Claude
tool_user = ToolUser([ file_write_tool, file_read_tool, create_folder_tool, file_copy_tool, search_tool, time_of_day_tool,elevenlabs_tts_tool, csv_read_tool]) #


while True:
    query = input("Enter your query (or 'exit' to quit): ")
    if query.lower() == 'exit':
        break

    # Read the latest description from the descriptions.csv file
    latest_description = csv_read_tool.use_tool()

    messages = [
        {"role": "assistant", "content": f"The current description seen by the camera is: {latest_description}"},
        {"role": "user", "content": query}
    ]

    try:
        response = tool_user.use_tools(messages, execution_mode="automatic")
        print(response)

        # Check if the response contains a motor control command
        if "rotate the motors" in query.lower():
            if "person" in latest_description.lower():
                # Send commands to rotate the motors
                esp_motor_control_tool.use_tool("M3_FORWARD")
                esp_motor_control_tool.use_tool("M4_FORWARD")
                print("Motors rotated to turn towards the person.")
            else:
                print("No person detected in the latest description.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

# while True:
#     query = input("Enter your query (or 'exit' to quit): ")
#     if query.lower() == 'exit':
#         break

#     # Read the latest description from the descriptions.csv file
#     latest_description = csv_read_tool.use_tool()

#     messages = [
#         {"role": "assistant", "content": f"The current description seen by the camera is: {latest_description}"},
#         {"role": "user", "content": query}
#     ]

#     try:
#         response = tool_user.use_tools(messages, execution_mode="automatic")
#         print(response)
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")

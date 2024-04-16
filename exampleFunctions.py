from tool_use_package.tools.base_tool import BaseTool
from tool_use_package.tool_user import ToolUser
from tool_use_package.tools.search.brave_search_tool import BraveSearchTool
import os
current_dir = os.getcwd()

class FileReadTool(BaseTool):
    """Reads content from a file."""
    def use_tool(self, file_path):
        # Modify the file path to be relative to the current directory
        file_path = os.path.join(current_dir, file_path)
        print(f"Reading from file: {file_path}")
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    

file_read_tool_name = "file_read"
file_read_tool_description = """Reads content from a file.
Use this tool to read files when needed to answer a question or provide information."""
file_read_tool_parameters = [
{"name": "file_path", "type": "str", "description": "The path of the file to read from."}
]
file_read_tool = FileReadTool(file_read_tool_name, file_read_tool_description, file_read_tool_parameters)

tool_user = ToolUser([file_read_tool]) 
from .base import Skill
from typing import Dict, Any
import datetime
import os

class TimeSkill(Skill):
    @property
    def name(self) -> str:
        return "get_current_time"

    @property
    def description(self) -> str:
        return "Gets the current system date and time."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

    def execute(self, **kwargs) -> str:
        return f"Current date and time: {datetime.datetime.now().isoformat()}"

class FileReaderSkill(Skill):
    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Reads the contents of a text file from the filesystem."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "The absolute or relative path to the file."
                }
            },
            "required": ["filepath"]
        }

    def execute(self, filepath: str = None, **kwargs) -> str:
        if not filepath:
            return "Error: filepath is required."
        try:
            with open(filepath, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file {filepath}: {str(e)}"

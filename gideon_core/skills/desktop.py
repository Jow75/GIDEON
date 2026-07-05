from .base import Skill
from typing import Dict, Any
import subprocess
import os
import platform

class LaunchApplicationSkill(Skill):
    @property
    def name(self) -> str:
        return "launch_application"

    @property
    def description(self) -> str:
        return "Launches a desktop application by name or executable."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                    "description": "The exact name or path of the application to launch (e.g., 'notepad', 'calc')."
                }
            },
            "required": ["app_name"]
        }

    def execute(self, app_name: str = None, **kwargs) -> str:
        if not app_name:
            return "Error: app_name is required."

        system = platform.system()
        try:
            if system == "Windows":
                # Safer alternative to start with shell=True
                # os.startfile safely opens a file or application using its associated program
                # or executable path without invoking the shell interpreter.
                try:
                    os.startfile(app_name)
                    return f"Successfully sent command to launch {app_name} on Windows."
                except AttributeError:
                    # Fallback if startfile is missing in some environments
                    subprocess.Popen([app_name])
                    return f"Successfully sent command to launch {app_name} on Windows."
            elif system == "Darwin":
                # macOS
                subprocess.Popen(["open", "-a", app_name])
                return f"Successfully sent command to launch {app_name} on macOS."
            elif system == "Linux":
                # Linux
                subprocess.Popen([app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return f"Successfully sent command to launch {app_name} on Linux."
            else:
                return f"Error: Unsupported OS for launching apps ({system})"
        except FileNotFoundError:
            return f"Error: Application '{app_name}' could not be found."
        except Exception as e:
            return f"Error launching application {app_name}: {str(e)}"

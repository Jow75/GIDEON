from .base import Skill
from typing import Dict, Any
import datetime
from core.manifest import SkillManifest
from core.os.factory import get_os

class TimeSkill(Skill):
    manifest = SkillManifest(
        name="get_current_time",
        version="1.0.0",
        description="Gets the current system date and time.",
        permissions=[],
        required_capabilities=[],
        requires_confirmation=False,
        execution_category="utility"
    )

    @property
    def name(self) -> str:
        return self.manifest.name

    @property
    def description(self) -> str:
        return self.manifest.description

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
    manifest = SkillManifest(
        name="read_file",
        version="1.0.0",
        description="Reads the contents of a text file from the filesystem.",
        permissions=["fs_read"],
        required_capabilities=[],
        requires_confirmation=False,
        execution_category="utility"
    )

    @property
    def name(self) -> str:
        return self.manifest.name

    @property
    def description(self) -> str:
        return self.manifest.description

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

class ListProcessesSkill(Skill):
    manifest = SkillManifest(
        name="list_processes",
        version="1.0.0",
        description="Lists currently running processes.",
        permissions=["system_cmd"],
        required_capabilities=["supports_process_control"],
        requires_confirmation=False,
        execution_category="system"
    )

    @property
    def name(self) -> str:
        return self.manifest.name

    @property
    def description(self) -> str:
        return self.manifest.description

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

    def execute(self, **kwargs) -> str:
        os_interface = get_os()
        if not os_interface.capabilities.supports_process_control:
            return f"Error: The current OS ({os_interface.os_name}) does not support process control."
            
        processes = os_interface.get_process_list()
        # Return top 15 by CPU to avoid huge payload
        processes.sort(key=lambda p: p.cpu_percent, reverse=True)
        top = processes[:15]
        
        result = [f"Top 15 Processes on {os_interface.os_name}:"]
        for p in top:
            result.append(f"PID: {p.pid} | Name: {p.name} | CPU: {p.cpu_percent}% | Mem: {p.memory_percent}%")
        return "\n".join(result)

class KillProcessSkill(Skill):
    manifest = SkillManifest(
        name="kill_process",
        version="1.0.0",
        description="Terminates a process by its PID.",
        permissions=["system_cmd"],
        required_capabilities=["supports_process_control"],
        requires_confirmation=True,
        execution_category="system"
    )

    @property
    def name(self) -> str:
        return self.manifest.name

    @property
    def description(self) -> str:
        return self.manifest.description

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pid": {
                    "type": "integer",
                    "description": "The Process ID to terminate."
                }
            },
            "required": ["pid"]
        }

    def execute(self, pid: int = None, **kwargs) -> str:
        if pid is None:
            return "Error: pid is required."
            
        os_interface = get_os()
        if not os_interface.capabilities.supports_process_control:
            return f"Error: The current OS ({os_interface.os_name}) does not support process control."
            
        success = os_interface.kill_process(pid)
        if success:
            return f"Successfully terminated process {pid}."
        else:
            return f"Failed to terminate process {pid}. It may not exist or permission was denied."

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from abc import ABC, abstractmethod

class SystemCapabilities(BaseModel):
    supports_screen_capture: bool = False
    supports_global_hotkeys: bool = False
    supports_process_control: bool = False
    supports_native_notifications: bool = False
    supports_audio_capture: bool = False
    supports_audio_playback: bool = False

class ProcessInfo(BaseModel):
    pid: int
    name: str
    cpu_percent: float = 0.0
    memory_percent: float = 0.0

class OSInterface(ABC):
    """
    Abstract base class for all OS-specific implementations.
    Provides a unified interface for the AI to interact with the underlying system.
    """
    
    @property
    @abstractmethod
    def capabilities(self) -> SystemCapabilities:
        """Return the capabilities supported by this OS implementation."""
        pass

    @property
    @abstractmethod
    def os_name(self) -> str:
        """Return the normalized OS name (e.g., 'Windows', 'Linux', 'macOS')."""
        pass

    @abstractmethod
    def get_telemetry(self) -> Dict[str, Any]:
        """Collect current system telemetry (CPU, RAM, Disk, etc.)."""
        pass

    @abstractmethod
    async def execute_command(self, command: str, background: bool = False) -> str:
        """Execute a shell command natively and return output."""
        pass

    @abstractmethod
    def get_process_list(self) -> List[ProcessInfo]:
        """Return a list of currently running processes."""
        pass

    @abstractmethod
    def kill_process(self, pid: int) -> bool:
        """Terminate a process by ID."""
        pass

    @abstractmethod
    async def open_application(self, app_name: str) -> str:
        """Launch a desktop application by name."""
        pass

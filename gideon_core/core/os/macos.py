import asyncio
import psutil
from typing import Dict, Any, List
from core.os.base import OSInterface, SystemCapabilities, ProcessInfo

class MacOS(OSInterface):
    @property
    def capabilities(self) -> SystemCapabilities:
        return SystemCapabilities(
            supports_screen_capture=True,
            supports_global_hotkeys=False, # Often requires Accessibility permissions
            supports_process_control=True,
            supports_native_notifications=True, # via osascript
            supports_audio_capture=True,
            supports_audio_playback=True
        )

    @property
    def os_name(self) -> str:
        return "macOS"

    def get_telemetry(self) -> Dict[str, Any]:
        return {
            "os": self.os_name,
            "cpu_percent": psutil.cpu_percent(interval=None),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }

    async def execute_command(self, command: str, background: bool = False) -> str:
        if background:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            return f"Background process started with PID: {process.pid}"
        
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            return f"Error: {stderr.decode('utf-8', errors='ignore')}"
        return stdout.decode('utf-8', errors='ignore')

    def get_process_list(self) -> List[ProcessInfo]:
        processes = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(ProcessInfo(
                    pid=p.info['pid'],
                    name=p.info['name'],
                    cpu_percent=p.info['cpu_percent'] or 0.0,
                    memory_percent=p.info['memory_percent'] or 0.0
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processes

    def kill_process(self, pid: int) -> bool:
        try:
            p = psutil.Process(pid)
            p.terminate()
            return True
        except Exception:
            return False

    async def open_application(self, app_name: str) -> str:
        return await self.execute_command(f"open -a {app_name}", background=True)

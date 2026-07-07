import platform
import logging
from typing import Optional
from core.os.base import OSInterface

logger = logging.getLogger(__name__)

_os_instance: Optional[OSInterface] = None

def get_os() -> OSInterface:
    """
    Auto-detects the host platform and returns the appropriate OSInterface implementation.
    Acts as a singleton to avoid re-initialization overhead.
    """
    global _os_instance
    if _os_instance is not None:
        return _os_instance

    system = platform.system().lower()
    
    if system == "windows":
        from core.os.windows import WindowsOS
        _os_instance = WindowsOS()
    elif system == "linux":
        from core.os.linux import LinuxOS
        _os_instance = LinuxOS()
    elif system == "darwin":
        from core.os.macos import MacOS
        _os_instance = MacOS()
    else:
        logger.warning(f"Unsupported OS: {system}. Falling back to Linux abstraction.")
        from core.os.linux import LinuxOS
        _os_instance = LinuxOS()
        
    logger.info(f"OS Abstraction Layer initialized for: {_os_instance.os_name}")
    return _os_instance

import logging

logger = logging.getLogger(__name__)

class GuardianService:
    """
    Security and bounds-checking service.
    Ensures actions requested by the AI or user do not violate safety standards.
    """
    def __init__(self):
        self.blocked_commands = ["rm -rf /", "format", "del /s /q", "DROP TABLE"]
        self.restricted_directories = ["C:\\Windows", "/etc", "/root"]

    def check_command(self, command: str) -> bool:
        """Returns True if command is safe to execute, False otherwise."""
        cmd_lower = command.lower()
        for blocked in self.blocked_commands:
            if blocked.lower() in cmd_lower:
                logger.warning(f"Guardian blocked destructive command: {command}")
                return False
        return True

    def check_file_access(self, path: str) -> bool:
        """Returns True if the file path is safe to access."""
        path_lower = path.lower()
        for restricted in self.restricted_directories:
            if restricted.lower() in path_lower:
                logger.warning(f"Guardian blocked restricted path access: {path}")
                return False
        return True

    def scan_prompt_injection(self, text: str) -> bool:
        """
        Scans input for common prompt injection patterns.
        In a full implementation, this would route to meta/llama-guard-4-12b via the Router.
        """
        injection_markers = ["ignore all previous", "system prompt", "you are no longer"]
        text_lower = text.lower()
        for marker in injection_markers:
            if marker in text_lower:
                logger.warning(f"Guardian detected possible prompt injection: {marker}")
                return False
        return True

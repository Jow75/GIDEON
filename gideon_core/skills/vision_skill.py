from core.manifest import SkillManifest
from core.vision import VisionService
from core.os.factory import get_os

class VisionCaptureSkill:
    manifest = SkillManifest(
        name="capture_screen",
        version="1.0.0",
        description="Captures the current screen and returns the file path for visual processing.",
        permissions=["fs_write"],
        required_capabilities=["vision"],
        requires_confirmation=False,
        execution_category="system"
    )

    def __init__(self):
        self.vision = VisionService()

    def execute(self, filename: str = "capture.png", **kwargs) -> str:
        os_interface = get_os()
        if not os_interface.capabilities.supports_screen_capture:
            return f"Error: The current OS ({os_interface.os_name}) does not support screen capture."

        filepath = self.vision.capture_screenshot(filename)
        if filepath:
            return f"Screenshot successfully saved to {filepath}."
        return "Failed to capture screenshot."

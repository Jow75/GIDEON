import mss
import mss.tools
import os
from typing import Optional
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class VisionService:
    """
    Handles screen capture and visual context generation.
    """
    def __init__(self):
        self.screenshots_dir = os.path.join(settings.data_dir, "screenshots")
        os.makedirs(self.screenshots_dir, exist_ok=True)

    def capture_screenshot(self, filename: str = "current_screen.png") -> Optional[str]:
        """
        Captures the primary monitor screen and saves it to disk.
        Returns the absolute path to the saved screenshot.
        """
        filepath = os.path.join(self.screenshots_dir, filename)
        try:
            with mss.mss() as sct:
                # Capture primary monitor
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=filepath)
            
            logger.info(f"Screenshot saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None

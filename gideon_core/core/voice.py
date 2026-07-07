import sounddevice as sd
import soundfile as sf
import os
import logging
from typing import Optional
from config.settings import settings

logger = logging.getLogger(__name__)

class VoiceService:
    """
    Handles audio capture and interfaces with STT/TTS APIs.
    """
    def __init__(self):
        self.audio_dir = os.path.join(settings.data_dir, "audio")
        os.makedirs(self.audio_dir, exist_ok=True)
        self.sample_rate = 16000

    def record_audio(self, duration_sec: int = 5, filename: str = "recording.wav") -> Optional[str]:
        """
        Records audio from the default microphone for a set duration.
        """
        filepath = os.path.join(self.audio_dir, filename)
        logger.info(f"Recording audio for {duration_sec} seconds...")
        
        try:
            recording = sd.rec(int(duration_sec * self.sample_rate), 
                             samplerate=self.sample_rate, 
                             channels=1)
            sd.wait()  # Wait until recording is finished
            
            sf.write(filepath, recording, self.sample_rate)
            logger.info(f"Audio saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to record audio: {e}")
            return None

    # STT/TTS placeholders to be wired to the Router
    async def transcribe_audio(self, filepath: str) -> str:
        # Placeholder for actual Whisper API call
        return f"[Mock Transcription of {os.path.basename(filepath)}]"

    async def generate_speech(self, text: str, output_filename: str = "speech.wav") -> Optional[str]:
        # Placeholder for TTS generation
        return os.path.join(self.audio_dir, output_filename)

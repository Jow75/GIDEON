from .base import STTProvider, TTSProvider
import time

class MockSTTProvider(STTProvider):
    def listen_and_transcribe(self) -> str:
        print("[Microphone: Listening...]")
        time.sleep(1)
        # In a real environment, this would capture audio and transcribe
        return "Hello Gideon, this is a mock transcribed voice command."

class MockTTSProvider(TTSProvider):
    def speak(self, text: str):
        print(f"[Speaker: Synthesizing] {text}")
        # In a real environment, this would play the audio

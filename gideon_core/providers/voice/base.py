from abc import ABC, abstractmethod

class STTProvider(ABC):
    @abstractmethod
    def listen_and_transcribe(self) -> str:
        """Listens to microphone input and returns transcribed text."""

class TTSProvider(ABC):
    @abstractmethod
    def speak(self, text: str):
        """Synthesizes text to speech and plays it."""

from core.manifest import SkillManifest
from core.voice import VoiceService

class AudioRecordSkill:
    manifest = SkillManifest(
        name="record_audio",
        version="1.0.0",
        description="Records audio from the microphone for a specified duration.",
        permissions=["fs_write", "mic_capture"],
        required_capabilities=[],
        requires_confirmation=True,
        execution_category="system"
    )

    def __init__(self):
        self.voice = VoiceService()

    def execute(self, duration_sec: int = 5, filename: str = "record.wav", **kwargs) -> str:
        filepath = self.voice.record_audio(duration_sec, filename)
        if filepath:
            return f"Audio successfully recorded and saved to {filepath}."
        return "Failed to record audio."

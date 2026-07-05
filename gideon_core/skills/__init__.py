from .base import Skill
from .system import TimeSkill, FileReaderSkill
from .desktop import LaunchApplicationSkill

def get_available_skills() -> dict[str, Skill]:
    """Registry of available skills."""
    skills = [TimeSkill(), FileReaderSkill(), LaunchApplicationSkill()]
    return {skill.name: skill for skill in skills}

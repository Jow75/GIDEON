from .base import Skill
from .system import TimeSkill, FileReaderSkill

def get_available_skills() -> dict[str, Skill]:
    """Registry of available skills."""
    skills = [TimeSkill(), FileReaderSkill()]
    return {skill.name: skill for skill in skills}

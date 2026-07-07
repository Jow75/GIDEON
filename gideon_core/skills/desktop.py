from .base import Skill
from typing import Dict, Any
from core.manifest import SkillManifest
from core.os.factory import get_os

class LaunchApplicationSkill(Skill):
    manifest = SkillManifest(
        name="launch_application",
        version="1.0.0",
        description="Launches a desktop application by name or executable.",
        permissions=[],
        required_capabilities=[],
        requires_confirmation=False,
        execution_category="system"
    )

    @property
    def name(self) -> str:
        return self.manifest.name

    @property
    def description(self) -> str:
        return self.manifest.description

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                    "description": "The exact name or path of the application to launch (e.g., 'notepad', 'calc')."
                }
            },
            "required": ["app_name"]
        }

    async def execute(self, app_name: str = None, **kwargs) -> str:
        if not app_name:
            return "Error: app_name is required."

        os_interface = get_os()
        try:
            return await os_interface.open_application(app_name)
        except Exception as e:
            return f"Error launching application {app_name}: {str(e)}"

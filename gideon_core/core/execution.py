import os
import importlib
import pkgutil
from typing import Dict, Any, Optional
import logging
import inspect
from core.guardian import GuardianService
from core.manifest import SkillManifest
from config.settings import settings
from core.event_bus import EventBus, Event

logger = logging.getLogger(__name__)

class ExecutionService:
    """
    Dynamically loads and manages skills.
    Executes skills through the GuardianService for safety.
    """
    def __init__(self, guardian: GuardianService, event_bus: Optional[EventBus] = None):
        self.guardian = guardian
        self.event_bus = event_bus
        self.skills: Dict[str, Any] = {}
        self._discover_skills()

    def _discover_skills(self):
        """Dynamically discover and load all skill classes from the skills package."""
        import skills
        package_dir = os.path.dirname(skills.__file__)
        
        for _, module_name, is_pkg in pkgutil.iter_modules([package_dir]):
            if is_pkg:
                continue
            
            try:
                module = importlib.import_module(f"skills.{module_name}")
                # Look for a class that has an 'execute' method and a 'manifest' attribute
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and hasattr(attr, "execute") and hasattr(attr, "manifest"):
                        manifest = attr.manifest
                        if isinstance(manifest, SkillManifest):
                            skill_name = manifest.name
                            self.skills[skill_name] = attr()
                            logger.info(f"Loaded skill: {skill_name} v{manifest.version}")
                        else:
                            logger.warning(f"Class {attr_name} in {module_name} has invalid manifest.")
            except Exception as e:
                logger.error(f"Failed to load skill module {module_name}: {e}")

    def get_skill_descriptions(self) -> Dict[str, str]:
        """Returns a mapping of skill names to their descriptions."""
        return {name: skill.manifest.description for name, skill in self.skills.items()}

    async def execute_skill(self, skill_name: str, **kwargs) -> str:
        """Executes a skill after passing it through the GuardianService."""
        if skill_name not in self.skills:
            return f"[Error: Unknown skill '{skill_name}']"
            
        skill = self.skills[skill_name]
        manifest = skill.manifest
        
        if manifest.requires_confirmation:
            logger.info(f"Skill {skill_name} requires confirmation. (Mock auto-confirming for now)")
        
        # Check permissions
        if "fs_read" in manifest.permissions and 'path' in kwargs and not self.guardian.check_file_access(kwargs['path']):
            return "[Error: Guardian blocked access to restricted path]"
            
        if "fs_write" in manifest.permissions and 'path' in kwargs and not self.guardian.check_file_access(kwargs['path']):
            return "[Error: Guardian blocked access to restricted path]"
            
        if "system_cmd" in manifest.permissions and 'command' in kwargs and not self.guardian.check_command(kwargs['command']):
            return "[Error: Guardian blocked destructive command execution]"

        try:
            # Some skills might be async, some sync. Handle both gracefully.
            import asyncio
            if inspect.iscoroutinefunction(skill.execute):
                result = await skill.execute(**kwargs)
            else:
                # Run sync skills in an executor to avoid blocking the event loop
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, lambda: skill.execute(**kwargs))
            return str(result)
        except Exception as e:
            logger.error(f"Skill execution failed: {e}", exc_info=True)
            return f"[Error executing {skill_name}: {e}]"

    async def execute_remote_skill(self, skill_name: str, target_node: str = "any", timeout: float = 30.0, **kwargs) -> str:
        """Dispatches a skill to be executed by a remote worker."""
        if not self.event_bus:
            return "[Error: Remote execution not available (no event bus)]"
            
        import uuid
        import asyncio
        from datetime import datetime, timezone
        
        request_id = str(uuid.uuid4())
        correlation_id = str(uuid.uuid4())
        
        payload = {
            "request_id": request_id,
            "node_id": settings.node_id,
            "target_node": target_node,
            "skill_name": skill_name,
            "arguments": kwargs,
            "correlation_id": correlation_id,
            "timeout": timeout,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        future = asyncio.Future()
        
        async def response_handler(event: Event):
            if event.payload.get("request_id") == request_id:
                if not future.done():
                    future.set_result(event)
                    
        self.event_bus.subscribe("execute_skill_response", response_handler)
        self.event_bus.subscribe("execute_skill_failed", response_handler)
        self.event_bus.subscribe("execute_skill_timeout", response_handler)
        
        try:
            await self.event_bus.publish(Event(
                type="execute_skill_request",
                source=settings.node_id,
                payload=payload
            ))
            
            response_event = await asyncio.wait_for(future, timeout=timeout + 2.0)
            
            if response_event.type == "execute_skill_response":
                return str(response_event.payload.get("returned_data"))
            else:
                reason = response_event.payload.get("failure_reason", "Unknown failure")
                return f"[Error: Remote execution failed - {reason}]"
                
        except asyncio.TimeoutError:
            return "[Error: Remote execution timed out]"
        finally:
            self.event_bus.unsubscribe("execute_skill_response", response_handler)
            self.event_bus.unsubscribe("execute_skill_failed", response_handler)
            self.event_bus.unsubscribe("execute_skill_timeout", response_handler)

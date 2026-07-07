from providers.base import Message
from orchestration.router import AIOperationsRouter

class AutomationAgent:
    """Specialized agent for desktop automation workflows."""
    def __init__(self, router: AIOperationsRouter):
        self.router = router

    async def analyze_workflow(self, request: str, os_info: str) -> str:
        """Analyzes a complex desktop request and suggests an automation approach."""
        messages = [
            Message(role="system", content=f"You are the Gideon Automation Agent. Your operating system is {os_info}. Output an explanation of how you would automate the requested desktop workflow using Python (e.g., pyautogui or subprocess). Focus on robustness and handling varying UI states."),
            Message(role="user", content=request)
        ]
        return await self.router.execute_task(required_tags=["reasoning"], messages=messages)

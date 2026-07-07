from providers.base import Message
from orchestration.router import AIOperationsRouter

class CoderAgent:
    """Specialized agent for writing and reviewing code."""
    def __init__(self, router: AIOperationsRouter):
        self.router = router

    async def write_code(self, prompt: str) -> str:
        """Uses a coding-specific model to generate code."""
        messages = [
            Message(role="system", content="You are the Gideon Coder Agent. Write clean, production-ready code. Output ONLY the code block without markdown wrappers if possible, or keep explanations extremely brief."),
            Message(role="user", content=prompt)
        ]
        return await self.router.execute_task(required_tags=["coding"], messages=messages)

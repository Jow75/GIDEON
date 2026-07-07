import json
import re
from typing import List, Dict, Any
from providers.base import Message
from orchestration.router import AIOperationsRouter

class PlannerAgent:
    """
    Takes a complex request and breaks it down into a structured JSON plan.
    """
    def __init__(self, router: AIOperationsRouter):
        self.router = router

    async def generate_plan(self, objective: str, world_state: str) -> List[Dict[str, Any]]:
        """Generates a list of steps to achieve the objective."""
        system_prompt = f"""You are the Gideon Planner Agent. Your job is to break down complex objectives into a sequence of actionable steps.
Current World State:
{world_state}

Return ONLY a JSON array of step objects, in this exact format:
```json
[
  {{"step": 1, "action": "read_file", "description": "Read the configuration file."}},
  {{"step": 2, "action": "summarize", "description": "Summarize the contents."}}
]
```"""

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=f"Objective: {objective}")
        ]

        response_text = await self.router.execute_task(required_tags=["reasoning"], messages=messages)

        plan_json_str = None
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            plan_json_str = json_match.group(1)
        elif response_text.strip().startswith('[') and response_text.strip().endswith(']'):
            plan_json_str = response_text.strip()

        if plan_json_str:
            try:
                plan = json.loads(plan_json_str)
                if isinstance(plan, list):
                    return plan
            except Exception as e:
                print(f"[Planner Error: {e}]")

        return [{"step": 1, "action": "fallback", "description": "Execute request directly."}]

    async def validate_step(self, step_description: str, execution_result: str) -> bool:
        """Validates if a planned step was completed successfully based on its result."""
        val_prompt = f"""You are a validation engine.
Step Description: {step_description}
Execution Result: {execution_result}

Did the execution result successfully achieve the goal of the step?
Reply strictly with "YES" or "NO"."""

        messages = [Message(role="system", content=val_prompt)]
        response = await self.router.execute_task(required_tags=["reasoning"], messages=messages)
        
        return "YES" in response.upper()

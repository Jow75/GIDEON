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

    def generate_plan(self, objective: str, world_state: str) -> List[Dict[str, Any]]:
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

        response_text = self.router.execute_task(required_tags=["reasoning"], messages=messages)

        # Parse JSON
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if not json_match:
            # Fallback
            json_match = type('obj', (object,), {'group': lambda self, n: response_text.strip()})()

        try:
            plan = json.loads(json_match.group(1))
            if isinstance(plan, list):
                return plan
        except Exception as e:
            print(f"[Planner Error: {e}]")

        return [{"step": 1, "action": "fallback", "description": "Execute request directly."}]
